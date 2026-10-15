# Implementation plan

## Goal

Build a local evaluation lab for a fictional bank's informational chat-based RAG assistant, from reviewed golden data through sampled online evaluation and trace-to-regression feedback.

This is a public, sanitized implementation roadmap. Local resource identifiers, credentials, transcripts, and raw execution artifacts are intentionally excluded.

## Architecture

- Same-origin HTML/CSS/JavaScript UI served by a local Python FastAPI API.
- Entra authentication and SDK calls only in the backend.
- Two targets: Python-orchestrated RAG using Azure AI Search and Foundry models, and a native Foundry Agent Service agent.
- Bounded durable jobs; SQLite plus raw JSON artifacts stored locally and ignored by Git.
- Real Foundry cloud evaluation with complete paginated item-level output retrieval.
- Local deterministic checks and supported SDK evaluators remain distinguishable from cloud evaluation.
- OTel instrumentation and OTLP export to one user-selected local backend.

## Steps and dependencies

| Step | Work | Prerequisites |
| --- | --- | --- |
| 1 | Prove selected resource access and SDK compatibility | Repository setup |
| 2 | Build local API, UI shell, configuration, job lifecycle, and persistence | 1 |
| 3 | Create synthetic bank knowledge and both RAG targets | 1, 2 |
| 4 | Build reviewed, versioned golden dataset workflow | 3 |
| 5 | Implement real offline and conversation evaluation | 4 |
| 6 | Add bank rules, human review, and bounded safety/red-team evaluation | 5 |
| 7 | Compare matched cases and implement conservative release gates | 5, 6 |
| 8 | Choose one telemetry backend after comparison | 1 |
| 9 | Instrument and persist real OTel telemetry | 3, 8 |
| 10 | Add sampled online evaluation and supported native monitoring | 5, 9 |
| 11 | Complete lifecycle screens and trace-to-regression feedback | 4, 7, 10 |
| 12 | Verify the complete demo and document operation | 11 |

Each step has a GitHub issue. Record meaningful actions, results, decisions, blockers, and associated commits in the relevant issue. Do not close an issue based only on a scaffold or an unverified API assumption.

## Step 1: capability proof

1. Inspect local Python, Azure CLI, GitHub CLI, container tools, and existing SDK versions without modifying global dependencies.
2. Select the intended Azure project, models, agent, search service/index, and tenant. Reuse suitable resources; ask before any mutation or paid action.
3. Pin and verify compatible Python/SDK versions in an isolated local environment.
4. Verify a real model call and native agent invocation using synthetic inputs.
5. Verify cloud evaluation creation, run submission, status retrieval, complete paginated output retrieval, and cancellation support.
6. Inspect evaluator contracts, required inputs, scales, direction, supported levels, preview state, roles, and regional restrictions.
7. Check native continuous evaluation and telemetry requirements without enabling or changing monitors without approval.
8. Publish a sanitized supported/blocked capability matrix. Keep detailed resource settings and raw responses local.

The complete RAG targets and reviewed dataset belong to later steps. The early proof uses a minimal synthetic fixture, not an approved golden dataset.

## Demonstration screens

1. Setup and capabilities.
2. Synthetic bank knowledge and retrieval evidence.
3. Golden dataset generation, human approval, splits, and immutable versions.
4. Live chat with citations and available trace detail.
5. Offline evaluation workbench with real asynchronous progress.
6. Agent/tool and multi-turn conversation evaluation.
7. Custom bank rules and human adjudication.
8. Safety and confirmed bounded red-team scans.
9. Baseline/candidate comparison and release gates.
10. Sampled online quality and production-style telemetry.
11. Failed trace review and promotion into a new regression dataset version.

## Dataset and evaluator contracts

Forty reviewed cases have stable IDs, scenario/risk labels, queries or role-structured messages, reference answers, expected behavior, approved evidence and policy versions, and retrieval relevance labels where required.

Separate development/calibration and held-out cases. Never feed held-out answers into target prompts. Score groundedness against actual retrieved context, not reference evidence substituted after the fact.

Support bank-relevant deterministic, RAG, retrieval, agent/tool, conversation, safety, custom rubric, and human evaluations. List other evaluator families with applicability rather than forcing them into this use case. Required missing inputs produce a blocked or insufficient-evidence result, not a fabricated score.

Persist dataset, corpus/index, prompt, target, evaluator, judge-model, threshold, and run versions. Do not combine incompatible score scales into an unexplained overall score.

## Demo safeguards

- Five-case smoke runs and forty-case full runs.
- At most two active application jobs; separately bound request fan-out.
- Online evaluation samples ten percent of eligible chats and caps at twenty scored turns per hour, persisted across restarts.
- Explicit confirmation and bounded settings for paid red-team scans.
- Pre-submit anticipated call counts and stated cost assumptions.
- Complete/pending/partial/error/unsupported states remain distinct.
- Remote cancellation is not claimed until acknowledged.
- Credentials and tokens never enter frontend assets, source control, logs, or public issues.
- Loopback service bindings, state-changing request protections, escaped rendered content, bounded queues, and content recording controls.

## Telemetry selection gate

Compare before implementing one stack:

| Option | Best fit | Tradeoff |
| --- | --- | --- |
| Collector + Grafana + Tempo + Prometheus | Production-style traces, metrics, latency/error and score trends | More services; custom evaluation score UI; verify Apache-2.0/AGPLv3 components |
| Collector + Jaeger | Focused trace investigation | Not a full quality/metrics dashboard; Apache-2.0 |
| Self-hosted Phoenix | AI-focused traces, datasets, experiments, evaluations | ELv2 source-available, not OSI-approved open source; verify license suitability |

Client-side OTLP export is not equivalent to exporting all remote agent spans. A cloud agent cannot send to a laptop's localhost. Do not expose a public laptop collector or add tunnels by default.

Link asynchronous evaluation spans/results to completed chat spans; do not mutate already exported spans. Keep identifiers out of metric labels. Distinguish missing usage from zero usage, and estimated cost from billing.

## Comparisons and release gates

Use matched held-out cases, fixed evaluator versions/thresholds, and comparable target configurations. Record prompt/retrieval changes explicitly.

Gate on minimum evidence coverage, selected critical bank/safety failures, supported quality/retrieval thresholds, and matched-case regressions. Missing required evidence cannot pass. Explain small-sample limitations and judge disagreement.

## Acceptance

- Real candidate generation, reviewed dataset, and version lineage.
- Actual responses and citations from both target types.
- UI-triggered cloud evaluation with all available row outputs/reasons.
- Supported retrieval, bank, safety, conversation and human-review paths.
- Real baseline/candidate comparison without predetermined scores.
- Persisted real traces and asynchronous score correlation.
- Verified sampling/caps, error behavior, cancellation, reconnection and restart recovery.
- Native continuous evaluation where verified; otherwise an explicit blocker, never simulated coverage.
- Privacy checks, local bindings, artifact persistence, and clean stop controls.
- Unit/contract/browser checks and opt-in paid Azure acceptance checks.

## References

- [Foundry cloud evaluations](https://learn.microsoft.com/azure/foundry/observability/how-to/cloud-evaluation)
- [Model and agent targets](https://learn.microsoft.com/azure/foundry/observability/how-to/cloud-evaluation-targets)
- [Evaluation results](https://learn.microsoft.com/azure/foundry/observability/how-to/cloud-evaluation-results)
- [Built-in evaluators](https://learn.microsoft.com/azure/foundry/concepts/built-in-evaluators)
- [Agent monitoring](https://learn.microsoft.com/azure/foundry/observability/how-to/how-to-monitor-agents-dashboard)
- [Client-side tracing](https://learn.microsoft.com/azure/foundry/observability/how-to/trace-agent-client-side)
- [OpenTelemetry Collector](https://opentelemetry.io/docs/collector/)
- [Grafana Tempo](https://grafana.com/docs/tempo/latest/)
- [Jaeger](https://www.jaegertracing.io/docs/latest/)
- [Phoenix license](https://arize.com/docs/phoenix/self-hosting/license)
