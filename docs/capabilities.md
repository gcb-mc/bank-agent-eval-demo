# Step 1 capability report

**Status: blocked on data-plane DNS resolution; Step 1 is not complete.**

Only synthetic probe content is included in source control. Detailed resource settings, local terminal transcripts, error traces and raw outputs remain local.

| Capability | Status | Evidence and boundary |
| --- | --- | --- |
| Public repository and tracking | Verified | Initial roadmap committed; setup issue and twelve dependent step issues created |
| Dedicated project terminal | Verified | Visible PowerShell window executes queued project commands |
| Azure CLI and azd authentication | Verified | Read-only hosted environment preflight passed |
| Foundry azd extensions | Verified | Required agent/project/Foundry extensions are installed |
| Existing project resolution | Verified, management plane only | Project ARM resource resolved using the official lookup script |
| Model deployment discovery | Verified, management plane only | Existing deployments returned successfully; no new model provisioned |
| Isolated Python environment | Verified | Python 3.13; global packages unchanged |
| SDK versions | Verified locally | azure-ai-projects 2.4.0, openai 2.54.0, azure-identity 1.26.0; transitive dependencies locked |
| Evaluator catalog contract | Inspected locally | `project.beta.evaluators.list(type="builtin")`; requires preview opt-in |
| Evaluation/run/result APIs | Inspected locally, not remotely verified | Create, retrieve, paginated output listing and cancel methods exist |
| Native monitoring API | Inspected locally, not remotely verified | Evaluation-rule create/update/get/list methods exist; no monitor configured or changed |
| Hosted-agent region support | Documented, not deployment-tested | Selected region appears in official hosted-agent availability documentation |
| Local probe contracts | Verified | Seven offline tests passed; dependency consistency check passed |
| Data-plane hostname resolution | Blocked | Repeated default-resolver lookups failed for the project host; control Azure hosts resolved |
| Built-in evaluator discovery | Blocked | The first data-plane catalog request failed before inference |
| Model inference | Not executed | Probe stopped at catalog discovery |
| Cloud evaluation and item scores | Not executed | No evaluation group/run was submitted |
| Hosted demo agent | Not created | User requested a new hosted target; provisioning and live proof remain pending |
| Search/RAG, telemetry and online scoring | Not implemented | Later steps; do not infer readiness from SDK method existence |

## Network findings

Management-plane reads report successful resource provisioning, enabled public access, an allow-default network ACL, and no listed private endpoint connections. The returned account/project configuration was inspected locally; the selected account data-plane hostname still failed the local resolver.

This does not establish whether the root cause is the local/corporate resolver, a required network path, or the resource's DNS publication. Do not claim that the service is down or private-network isolated without further evidence.

No DNS, host-file, firewall, public-access or private-endpoint settings were modified. No alternate public resolver, public tunnel, or insecure fallback endpoint was used.

## Next gates

1. Restore approved DNS/network access to the selected project hostname, or select a different explicitly approved project.
2. Repeat read-only catalog discovery before any billable operation.
3. Run the approved short synthetic model call and one small cloud evaluation; retrieve actual item-level scores/reasons.
4. Prepare and review hosted-agent provisioning scope before deploying a new demo agent and proving its invocation.
5. Verify applicable evaluator/monitoring contracts remotely and update this report with real evidence.

Keep the Step 1 issue open until the required live evidence is available. Later steps depending on Step 1 are not ready.
