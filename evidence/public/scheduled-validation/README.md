# Evidence: Scheduled Execution Validation and Encoding Fault Diagnosis

## What was tested

Validation of unattended execution using Amazon EventBridge Scheduler targeting the Lambda detection runner:
1. **Initial Fault Diagnosis:** An initial scheduled execution failed verification because context placeholders arrived at Lambda as literal strings instead of resolved runtime metadata. Investigation showed that Terraform's `jsonencode` had escaped `<` and `>` into `\u003c` and `\u003e`, preventing EventBridge Scheduler from evaluating context expressions.
2. **Targeted Remediation:** The schedule target's input template in Terraform was corrected to pass raw unescaped placeholders (`<aws.scheduler.schedule-arn>`, `<aws.scheduler.scheduled-time>`, and `<aws.scheduler.execution-id>`).
3. **Verified Execution & Duplicate Suppression:** The corrected schedule executed at `2026-10-31T00:42:15Z`. Lambda received the resolved context values, executed the Athena detection query, found the existing finding in DynamoDB, and skipped publication (`SKIPPED_PUBLISHED`), verifying idempotency during scheduled operation.

---

## Files in this directory

| File | Origin | Description |
| :--- | :--- | :--- |
| `schedule-target-escaped.json` | EventBridge Scheduler API | Original schedule definition showing `\u003c` and `\u003e` escaping caused by Terraform `jsonencode`. |
| `schedule-target-remediated.json` | EventBridge Scheduler API | Remediated schedule definition with unescaped `<aws.scheduler...>` placeholders. |
| `deployment-diagnostic.json` | Local preflight diagnostic | Diagnostic check verifying that the packaged Lambda code hash matched the live deployment before diagnosing the schedule input fault. |
| `scheduled-execution-summary.json` | CloudWatch Logs / Lambda return | Lambda execution summary showing resolved `trigger_context`, query status `SUCCEEDED`, and duplicate suppression (`notifications_skipped: 1`, `notifications_published: 0`). |
| `verifier-receipt.json` | `scripts/verify_scheduled_run.py` | Verification receipt confirming 1 matching completed execution with expected scenario `PASS`. |
| `checksums.sha256` | Local verification | SHA-256 hashes of all published files in this directory. |

---

## Fields removed or replaced

None. Account IDs (`625867802773`), schedule ARNs, execution IDs, and query IDs are preserved to demonstrate exact technical correlation and root-cause evidence.

---

## Artifact correlation

- **Execution ID:** Scheduler execution ID `b16ae539-6766-48de-b6c5-cea4a7031cef` matches the Lambda `request_id` in `scheduled-execution-summary.json` and `verifier-receipt.json`.
- **Duplicate Suppression Linkage:** The finding detected during this scheduled run (`8deaa4d7345f7fd114e7212cb28e19d78736db294de0f887c92197c564047ea4`) matches the earlier manual publication in `evidence/public/cloud-publication/dynamodb-finding-ledger.json`. Because the DynamoDB ledger already held a `PUBLISHED` record, the scheduled runner skipped publishing a duplicate notification.

---

## What the evidence establishes

- Demonstrates the EventBridge Scheduler trigger pathway and diagnostic troubleshooting of IaC encoding artifacts.
- Proves scheduled duplicate suppression over persistent DynamoDB state.

---

## What remains outside scope

- A one-time scheduled run was validated; recurring automated execution was intentionally not enabled in this lab.

