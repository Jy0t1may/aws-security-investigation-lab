# Evidence: S3 Object-Level Event Logging and Cleanup Verification

## What was tested

Validation of CloudTrail S3 Data event logging visibility for specific object operations, followed by verified restoration of management-only logging:
1. **Narrowly Scoped Selector Enablement:** Advanced event selectors were configured on the trail to capture `Data` events (`PutObject`, `GetObject`, `DeleteObject`) restricted strictly to the exercise bucket prefix `object-event-exercise/`.
2. **Controlled Operations:** Performed `put-object` (uploading `sample.txt`, 66 bytes, SSE-S3 AES256), `get-object` (verifying content SHA-256 matches `c8f091c9...`), and `delete-object`.
3. **Log Delivery & Correlation:** Confirmed delivery of exactly three matching CloudTrail Data event records in Stockholm audit logs.
4. **Cleanup & Restoration:** Restored management-only logging, verified live selectors via AWS API read-back, and ran a follow-up `terraform plan` confirming zero configuration drift or lingering data selectors.

---

## Files in this directory

| File | Origin | Description |
| :--- | :--- | :--- |
| `operation-summary.json` | Local execution manifest | Details the 4 API operations (`get-caller-identity`, `put-object`, `get-object`, `delete-object`), timestamps, and SHA-256 payload verification. |
| `selectors-enabled.json` | CloudTrail API | Advanced event selectors active during the exercise, showing management events preserved and temporary data events scoped to the exercise prefix. |
| `matched-events.json` | CloudTrail S3 audit logs | The 3 delivered CloudTrail Data event records corresponding to `PutObject`, `GetObject`, and `DeleteObject`. |
| `selectors-after-cleanup.json` | CloudTrail API (`GetEventSelectors`) | Live API read-back verifying restoration of default management-only collection (`DataResources: []`). |
| `terraform-final-plan.txt` | Terraform CLI stdout | Full transcript of the post-cleanup `terraform plan` showing `No changes. Your infrastructure matches the configuration.` |
| `checksums.sha256` | Local verification | SHA-256 hashes of all published files in this directory. |

---

## Fields removed or replaced

1. **Operator Client IP:** `sourceIPAddress` in `matched-events.json` was replaced with RFC 5737 documentation IP `198.51.100.24`.
2. **Session Key & SSO Metadata:** `accessKeyId` was masked as `ASIA...[REDACTED]...` and internal Identity Center instance ARNs in `onBehalfOf` were sanitized.
3. **Preserved fields:** Account ID (`625867802773`), Bucket Name (`awslab-exercise-32a2346937175b2acdeb4cd420`), Object Key (`object-event-exercise/20261031T200019Z-718df57cc9524b9dbfbad9bdf36597c0/sample.txt`), Event Names, timestamps, request IDs, and encryption metadata are preserved intact.

---

## Artifact correlation

- **Payload Integrity:** In `operation-summary.json`, the uploaded sample text hash `c8f091c95d0e32101bb0aede66e56142638e3089d8f923aef98146c1406e7065` matches the downloaded object hash before deletion.
- **Audit Records:** `matched-events.json` captures all three operations targeting this exact key within the exercise bucket.
- **Cleanup Guarantee:** `selectors-after-cleanup.json` and `terraform-final-plan.txt` demonstrate that temporary data-logging configuration was completely removed, returning the environment to its low-cost baseline.

---

## What the evidence establishes

- Demonstrates logging visibility and CloudTrail Data event schema capture for object-level interactions.
- Proves rigorous cleanup discipline: temporary collection was removed and verified through both API inspection and Terraform plan comparison.

---

## What remains outside scope

- This was a logging visibility test for one sample object; it did not implement or claim an automated object-access detection rule.
- Does not represent permanent or account-wide S3 data event collection.

