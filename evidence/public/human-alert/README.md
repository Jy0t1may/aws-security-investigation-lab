# Evidence: Human-Facing Alert and Manual Investigation

## What was tested

Validation of end-to-end human alerting and alert correlation:
1. **Controlled Authorization Failure:** A new denied `s3:GetBucketTagging` call was generated using the `awslab-location-reader` role against the exercise bucket on October 31, 2026.
2. **Audit Logging & Athena Query:** The event was logged by CloudTrail (Event ID `31c83772-eb90-4c6d-9fee-a36c7cedb678`) and delivered to S3.
3. **Cloud Lambda Invocation:** Upon confirmation of log delivery, the detection runner executed in `CLOUD_PUBLISHING` mode. It evaluated findings, skipped the previous finding (`8deaa4d...`), and published the newly detected finding (`11150f8a...`).
4. **Email Notification:** The finding was delivered via SNS to the project owner's subscribed email endpoint.

---

## Files in this directory

| File | Origin | Description |
| :--- | :--- | :--- |
| `request-error.txt` | AWS CLI stderr | AccessDenied message and exit code `254` from the controlled tagging attempt. |
| `request-exit-code.txt` | Shell exit code | Exit code `254`. |
| `cloudtrail-event.json` | CloudTrail Event history | Complete audit record for Event ID `31c83772-eb90-4c6d-9fee-a36c7cedb678`. |
| `lambda-execution-summary.json` | Lambda return | Handler summary recording `finding_count: 2`, `notifications_skipped: 1`, `notifications_published: 1`, and `PUBLISHED_NOW` for finding `11150f8a...`. |
| `email-alert-payload.json` | SNS Notification message | The exact finding message delivered to the human recipient via SNS email subscription. |
| `checksums.sha256` | Local verification | SHA-256 hashes of all published files in this directory. |

---

## Fields removed or replaced

1. **Personal Email Endpoint:** Personal email addresses and subscription confirmation/unsubscribe links were omitted.
2. **Operator Client IP:** `sourceIPAddress` in `cloudtrail-event.json` was replaced with RFC 5737 documentation IP `198.51.100.24`.
3. **Session Access Key ID:** Masked as `ASIA...[REDACTED]...`.
4. **Preserved fields:** Account ID (`625867802773`), Role ARN, Event ID (`31c83772-eb90-4c6d-9fee-a36c7cedb678`), Finding ID (`11150f8a161caa8d86643754cff194f6e070b3cc4d1421c44173b1093444244d`), and Athena Query ID (`74668ef9-4d01-47fa-8851-8ebf05af9e8a`) are preserved.

---

## Artifact correlation

- **Controlled Event:** Event ID `31c83772-eb90-4c6d-9fee-a36c7cedb678` at `2026-10-31T16:11:24Z`.
- **Lambda Detection:** In `lambda-execution-summary.json`, this event generated finding `11150f8a161caa8d86643754cff194f6e070b3cc4d1421c44173b1093444244d` under Query ID `74668ef9-4d01-47fa-8851-8ebf05af9e8a`.
- **Email Delivery:** The email payload (`email-alert-payload.json`) carries the exact same finding and query IDs.
- **Idempotency Proof:** `lambda-execution-summary.json` also shows finding `8deaa4d...` from the earlier October 30 test marked as `SKIPPED_PUBLISHED`, confirming that previously published findings are not re-sent.

---

## What the evidence establishes

- Proves that a newly detected authorization denial successfully triggers a human-facing alert via email while suppressing prior duplicate findings.
- Validates end-to-end trace correlation from CLI request failure to CloudTrail, Athena, Lambda, DynamoDB, and email.

---

## What remains outside scope

- One controlled finding and one recipient were exercised; this does not establish continuous notification reliability, on-call paging, or automated incident response.

