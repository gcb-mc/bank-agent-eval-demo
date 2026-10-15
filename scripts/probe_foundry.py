"""Run explicitly approved, synthetic-only Foundry compatibility probes."""

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID, uuid4
from urllib.parse import urlsplit

QUERY = (
    "Fictional Cedar Bank policy: lost debit cards must be frozen in the bank app "
    "and reported to bank support. In one sentence, what should a customer do "
    "after losing a debit card? Do not request account details or perform actions."
)


def settings(environ):
    endpoint = environ.get("AZURE_AI_PROJECT_ENDPOINT", "").rstrip("/")
    parsed = urlsplit(endpoint)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or not parsed.hostname.endswith(".services.ai.azure.com")
        or parsed.username
        or parsed.password
        or parsed.port not in (None, 443)
        or parsed.query
        or parsed.fragment
        or len(parsed.path.split("/")) != 4
        or not parsed.path.startswith("/api/projects/")
        or not parsed.path.split("/")[-1]
    ):
        raise ValueError("Set a valid HTTPS Foundry project endpoint.")
    tenant = str(UUID(environ.get("AZURE_TENANT_ID", "")))
    model = environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "").strip()
    if not model:
        raise ValueError("AZURE_AI_MODEL_DEPLOYMENT_NAME is required.")
    return endpoint, tenant, model


def evaluation_schema():
    return {
        "type": "custom",
        "item_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "response": {"type": "string"},
            },
            "required": ["query", "response"],
        },
    }


def inline_source(answer):
    if not answer or not answer.strip():
        raise ValueError("Cannot evaluate an empty model answer.")
    return {
        "type": "jsonl",
        "source": {
            "type": "file_content",
            "content": [{"item": {"query": QUERY, "response": answer}}],
        },
    }


def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True), encoding="utf-8")


def probe(output, live):
    from azure.ai.projects import AIProjectClient
    from azure.ai.projects.models import TestingCriterionAzureAIEvaluator
    from azure.identity import AzureCliCredential

    endpoint, tenant, model = settings(os.environ)
    output.mkdir(parents=True, exist_ok=False)
    state = {"phase": "read_only", "live_requested": live}
    save(output / "state.json", state)
    with AzureCliCredential(tenant_id=tenant) as credential:
        with AIProjectClient(
            endpoint=endpoint,
            credential=credential,
            retry_total=0,
            allow_preview=True,
            connection_timeout=15,
            read_timeout=30,
        ) as project:
            evaluators = list(project.beta.evaluators.list(type="builtin"))
            save(
                output / "evaluators.json",
                [evaluator.as_dict() for evaluator in evaluators],
            )
            state["catalog_count"] = len(evaluators)
            save(output / "state.json", state)
            if not live:
                state["phase"] = "read_only_completed"
                save(output / "state.json", state)
                print(f"Read-only catalog query completed. Local evidence: {output}")
                return
            with project.get_openai_client() as client:
                client = client.with_options(max_retries=0, timeout=60)
                state["phase"] = "model_request"
                save(output / "state.json", state)
                answer = client.responses.create(
                    model=model,
                    input=QUERY,
                    max_output_tokens=256,
                    store=False,
                )
                save(output / "model-response.json", answer.model_dump(mode="json"))
                data = inline_source(answer.output_text)
                state["phase"] = "evaluation_create"
                save(output / "state.json", state)
                evaluation = client.evals.create(
                    name="bank-demo-compatibility",
                    data_source_config=evaluation_schema(),
                    testing_criteria=[
                        TestingCriterionAzureAIEvaluator(
                            type="azure_ai_evaluator",
                            name="coherence",
                            evaluator_name="builtin.coherence",
                            initialization_parameters={"model": model},
                            data_mapping={
                                "query": "{{item.query}}",
                                "response": "{{item.response}}",
                            },
                        )
                    ],
                )
                state["eval_id"] = evaluation.id
                state["phase"] = "run_submit"
                save(output / "state.json", state)
                run = client.evals.runs.create(
                    eval_id=evaluation.id,
                    name="one-case-compatibility",
                    data_source=data,
                )
                state["run_id"] = run.id
                state["phase"] = "polling"
                save(output / "state.json", state)
                deadline = time.monotonic() + 600
                while run.status not in ("completed", "failed", "canceled", "cancelled"):
                    if time.monotonic() >= deadline:
                        state["phase"] = "poll_timeout_remote_may_continue"
                        save(output / "state.json", state)
                        raise TimeoutError(
                            "Polling deadline reached; remote work may continue. "
                            "Use the saved IDs to inspect it. Do not resubmit."
                        )
                    print(f"Remote evaluation status: {run.status}", flush=True)
                    time.sleep(5)
                    run = client.evals.runs.retrieve(
                        eval_id=evaluation.id, run_id=run.id
                    )
                save(output / "run.json", run.model_dump(mode="json"))
                state["remote_status"] = run.status
                if run.status != "completed":
                    state["phase"] = "remote_failed_or_cancelled"
                    save(output / "state.json", state)
                    raise RuntimeError(
                        f"Remote run ended with status {run.status}; see local evidence."
                    )
                state["phase"] = "download_items"
                save(output / "state.json", state)
                items = [
                    item.model_dump(mode="json")
                    for item in client.evals.runs.output_items.list(
                        eval_id=evaluation.id, run_id=run.id
                    )
                ]
                save(output / "output-items.json", items)
                if not items:
                    raise RuntimeError("Completed run returned no output items.")
                state["item_count"] = len(items)
                state["phase"] = "completed"
                save(output / "state.json", state)
                print(f"Real evaluation outputs saved locally: {output}")


def main():
    from azure.core.exceptions import AzureError
    from openai import APIError

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--live",
        action="store_true",
        help="Submit one billable model call and one one-case cloud evaluation.",
    )
    args = parser.parse_args()
    run_name = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = Path("artifacts") / "compatibility" / f"{run_name}-{uuid4().hex[:8]}"
    try:
        probe(output, args.live)
    except (AzureError, APIError, ValueError, RuntimeError, TimeoutError) as error:
        state_path = output / "state.json"
        if state_path.exists():
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["failed_phase"] = state["phase"]
            state["phase"] = "failed"
            state["error"] = {"type": type(error).__name__, "message": str(error)}
            save(state_path, state)
        raise


if __name__ == "__main__":
    main()
