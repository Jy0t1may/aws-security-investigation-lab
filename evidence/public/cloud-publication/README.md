# Evidence: Cloud Detection Publication and SQS Delivery

## What was tested

Validation of the cloud-hosted detection pipeline:
1. **Lambda Function Execution:** `awslab-detection-runner` executed under its dedicated IAM role in `CLOUD_PUBLISHING` mode.
2. **Athena Detection:** Evaluated candidate findings over Stockholm CloudTrail audit logs.
3. **DynamoDB Publication State:** Enforced duplicate suppression using conditional write claims (`finding_id` hash derived from rule ID and CloudTrail event ID).
4. **SNS Topic Publishing:** Dispatched confirmed new findings to `awslab-detection-findings`.
5. **SQS Inbox Delivery:** Verified receipt and correlation of the message in the `awslab-detection-inbox` queue and acknowledged the message.

---

## Files in this directory

| File | Origin | Description |
| :--- | :--- | :--- |
| `lambda-execution-summary.json` | Lambda invocation return | Summary returned by `handler.py` recording query state (`SUCCEEDED`), finding counts (1), notification outcome (`PUBLISHED_NOW`), and scan volume. |
| `finding-payload.json` | SNS finding message | Machine-readable finding schema containing finding ID `8deaa4d...`, event ID `d373a1f2...`, rule ID `AWSLAB-DET-001`, and Athena query reference. |
| `dynamodb-finding-ledger.json` | DynamoDB `GetItem` | Preserved publication ledger item showing status `PUBLISHED`, SNS message ID, owner request ID, and timestamps. |
| `sqs-notification-receipt.json` | SQS `ReceiveMessage` | Actual SQS envelope containing the SNS notification, message ID `ee5cf2f4...`, subject, and signature. |
| `delivery-verification-summary.json` | `scripts/verify_cloud_delivery.py` | Verification receipt confirming 1 expected finding, 1 correlated finding, 1 acknowledgement accepted, and overall PASS. |
| `checksums.sha256` | Local verification | SHA-256 hashes of all published files in this directory. |

---

## Fields removed or replaced

1. **Actionable Unsubscribe Link:** The `UnsubscribeURL` parameter within the SQS SNS envelope was sanitized to prevent unintended subscription modification (`...SubscriptionArn=[REDACTED]`).
2. **Preserved fields:** Topic ARN, Queue URL, Account ID (`625867802773`), Finding ID (`8deaa4d7345f7fd114e7212cb28e19d78736db294de0f887c92197c564047ea4`), Event ID (`d373a1f2-132e-4e13-a617-02187f6fd14d`), and Athena Query ID (`2f648b30-673b-403d-bcda-b86aff8e763d`) are preserved intact.

---

## Artifact correlation

- **Event to Finding:** Event `d373a1f2-132e-4e13-a617-02187f6fd14d` produced finding `8deaa4d7345f7fd114e7212cb28e19d78736db294de0f887c92197c564047ea4`.
- **Query to Lambda:** Lambda query execution `2f648b30-673b-403d-bcda-b86aff8e763d` is referenced in both `lambda-execution-summary.json` and `finding-payload.json`.
- **SNS to SQS:** SNS message ID `ee5cf2f4-c45d-5cd0-9c6c-91abdaad0a3a` recorded in DynamoDB (`dynamodb-finding-ledger.json`) matches the inner message ID received by SQS (`sqs-notification-receipt.json`).
- **Duplicate Suppression Linkage:** In `evidence/public/scheduled-validation/scheduled-summary.json`, this exact finding (`8deaa4d...`) was detected again during a subsequent run and skipped (`SKIPPED_PUBLISHED`), proving idempotency.

---

## What the evidence establishes

- Proves end-to-end cloud publication from Lambda query to DynamoDB ledger to SNS and SQS inbox.
- Validates the migration safeguard and conditional publication claim mechanism.

---

## What remains outside scope

- Does not establish continuous delivery reliability across arbitrary failure modes.
- Demonstrates at-least-once delivery with ledger-based deduplication, not distributed exactly-once delivery.

