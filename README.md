# Bank Agent Evaluation Lab

A local HTML/JavaScript and Python demonstration of the evaluation lifecycle for a fictional bank's informational RAG assistant.

**Status:** repository setup and SDK/resource compatibility discovery. The demo application is not implemented yet.

**Current blocker:** the selected Foundry data-plane hostname does not resolve from the execution machine. Management-plane lookup works, but no live model/evaluation probe has been submitted. See the [capability report](docs/capabilities.md).

## Intended experience

Create and human-review a golden dataset, invoke both a Python-orchestrated RAG target and a native Microsoft Foundry agent, run real SDK evaluations, inspect failures, compare versions, demonstrate release gates, and correlate sampled online evaluations with OpenTelemetry traces.

All bank documents and scenarios will be synthetic. The assistant will not access real accounts, make credit decisions, or perform transactions.

## Implementation tracking

- [Implementation plan](docs/implementation-plan.md): scope, sequence, decision gates, and acceptance criteria.
- [Step 1 capability report](docs/capabilities.md): verified evidence and remaining blockers.
- GitHub issues: one issue for each implementation step, with dependencies and progress comments.
- Git commits: persistent implementation changes, linked to the corresponding issue.

Commands run in a dedicated local PowerShell terminal. Raw terminal transcripts, Azure resource configuration, credentials, and evaluation artifacts are not published here. Issues record sanitized actions and outcomes rather than raw sensitive output.

## Execution boundaries

- Browser UI and Python API run locally on loopback.
- Real Azure inference/evaluation requires network access and can incur charges.
- SDK/API compatibility must be verified before building dependent features.
- Missing or unsupported capabilities are reported explicitly; saved results are never presented as live execution.
- Observability backend selection remains open: compare Grafana/Tempo/Prometheus, Jaeger, and the self-hosted Phoenix alternative before choosing.
- No production deployment or installed CI pipeline is included in the initial scope.

## Compatibility tools

Use Python 3.13 in an isolated environment:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe scripts\inspect_sdk.py
```

`inspect_sdk.py` inspects installed contracts without network requests. The full dependency lock records the resolved environment; `requirements.txt` pins direct dependencies.

For Azure probes, sign in manually with Azure CLI and set process-local configuration. Substitute the intended project endpoint, tenant GUID and existing deployment name; never commit their values.

```powershell
$env:AZURE_AI_PROJECT_ENDPOINT = "<your-Foundry-project-endpoint>"
$env:AZURE_TENANT_ID = "<your-tenant-guid>"
$env:AZURE_AI_MODEL_DEPLOYMENT_NAME = "<your-existing-deployment-name>"
.\.venv\Scripts\python.exe scripts\probe_foundry.py
```

The default probe only reads the built-in evaluator catalog. After network access and resource selection are verified, `--live` explicitly authorizes one synthetic model response and one one-case coherence evaluation. It is a compatibility check, not a RAG quality assessment or a golden dataset.

Evidence is written under ignored `artifacts\compatibility\` directories. Remote evaluation IDs are saved before polling. Automatic submission retries are disabled; inspect saved state before rerunning after an ambiguous error. Polling timeout does not mean the remote job stopped. The probe inspects cancellation API availability but does not test a real cancellation.

Hosted-agent deployment, the UI, RAG implementation, monitoring and observability remain future steps. Do not treat passing local tests as proof of live Azure connectivity.
