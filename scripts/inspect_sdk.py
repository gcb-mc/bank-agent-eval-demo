"""Inspect installed SDK contracts without sending any network requests."""

import inspect
import json
from importlib import metadata

from azure.ai.projects import AIProjectClient
from azure.identity import AzureCliCredential


def describe(operation):
    if operation is None:
        return {"available": False}
    # Preview guards proxy attribute access without exposing the wrapped methods in dir().
    operation = getattr(operation, "_operation", operation)
    result = {"available": True, "methods": {}}
    names = set(dir(operation)) | {"list_latest_versions", "list_versions"}
    for name in sorted(names):
        if name.startswith("_") or name in ("with_raw_response", "with_streaming_response"):
            continue
        value = getattr(operation, name, None)
        if callable(value):
            result["methods"][name] = str(inspect.signature(value))
    return result


def main():
    result = {
        "versions": {
            name: metadata.version(name)
            for name in ("azure-ai-projects", "openai", "azure-identity")
        }
    }
    with AzureCliCredential() as credential:
        with AIProjectClient(
            endpoint="https://example.services.ai.azure.com/api/projects/example",
            credential=credential,
            allow_preview=True,
        ) as client:
            result["project_operations"] = [
                name for name in dir(client) if not name.startswith("_")
            ]
            for name in ("agents", "connections", "evaluators", "evaluation_rules"):
                result[name] = describe(getattr(client, name, None))
            result["beta_operations"] = [
                name for name in dir(client.beta) if not name.startswith("_")
            ]
            result["beta"] = describe(client.beta)
            result["beta_evaluators"] = describe(
                getattr(client.beta, "evaluators", None)
            )
            with client.get_openai_client() as openai:
                result["evaluations"] = describe(openai.evals)
                result["runs"] = describe(openai.evals.runs)
                result["output_items"] = describe(openai.evals.runs.output_items)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
