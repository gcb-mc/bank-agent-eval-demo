# Bank Agent Evaluation Lab

A local HTML/JavaScript and Python demonstration of the evaluation lifecycle for a fictional bank's informational RAG assistant.

**Status:** repository setup and SDK/resource compatibility discovery. The demo application is not implemented yet.

## Intended experience

Create and human-review a golden dataset, invoke both a Python-orchestrated RAG target and a native Microsoft Foundry agent, run real SDK evaluations, inspect failures, compare versions, demonstrate release gates, and correlate sampled online evaluations with OpenTelemetry traces.

All bank documents and scenarios will be synthetic. The assistant will not access real accounts, make credit decisions, or perform transactions.

## Implementation tracking

- [Implementation plan](docs/implementation-plan.md): scope, sequence, decision gates, and acceptance criteria.
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
