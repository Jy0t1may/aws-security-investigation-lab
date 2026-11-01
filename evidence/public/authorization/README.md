# Evidence: Least-Privilege Authorization Testing

## What was tested

A runtime least-privilege verification of the assumed IAM role `awslab-location-reader` against the exercise S3 bucket (`awslab-exercise-32a2346937175b2acdeb4cd420`).
- **Permitted operation:** `s3:GetBucketLocation` was executed via AWS CLI and was expected to succeed.
- **Forbidden operation:** `s3:GetBucketTagging` was executed via AWS CLI and was expected to fail with an explicit client `AccessDenied` error (CLI exit code 254) because no policy grants that action.

---

## Files in this directory

| File | Origin | Description |
| :--- | :--- | :--- |
| `allowed-response.json` | AWS CLI stdout | Result of `aws s3api get-bucket-location`, returning Stockholm region constraint. |
| `allowed-exit-code.txt` | Shell exit code | Exit code `0` confirming successful execution. |
| `denied-error.txt` | AWS CLI stderr | AccessDenied message returned when attempting `get-bucket-tagging`. |
| `denied-exit-code.txt` | Shell exit code | Exit code `254` reflecting client-side failure on authorization rejection. |
| `matched-event-location.json` | CloudTrail S3 audit log | Delivered CloudTrail event record for the successful `GetBucketLocation` API call. |
| `matched-event-tagging.json` | CloudTrail S3 audit log | Delivered CloudTrail event record for the rejected `GetBucketTagging` API call. |
| `athena-permission-test-results.csv` | Athena query export | Athena SQL query results correlating both operations, their event IDs, role ARN, and source log file. |
| `checksums.sha256` | Local verification | SHA-256 hashes of all published files in this directory. |

---

## Fields removed or replaced

1. **Operator Source IP:** `sourceIPAddress` in both CloudTrail event JSON files was replaced with the RFC 5737 documentation IP address `198.51.100.24`.
2. **Temporary Session Key:** `userIdentity.accessKeyId` was masked as `ASIA...[REDACTED]...`.
3. **Preserved fields:** Account ID (`625867802773`), Role ARN (`arn:aws:sts::625867802773:assumed-role/awslab-location-reader/awslab-lp-check-20261021`), Event IDs (`e8a51efe-10f7-497e-9202-271653c1d350` and `7d900e24-00d4-45ed-979b-f7b80a0d8850`), request IDs, timestamps, and error codes were preserved intact to maintain verifiable correlation.

---

## Artifact correlation

- **Allowed call:** Event ID `e8a51efe-10f7-497e-9202-271653c1d350` corresponds to `GetBucketLocation` at `2026-10-27T01:39:37Z`.
- **Denied call:** Event ID `7d900e24-00d4-45ed-979b-f7b80a0d8850` corresponds to `GetBucketTagging` at `2026-10-27T01:39:48Z` with `errorCode = AccessDenied`.
- **Athena correlation:** `athena-permission-test-results.csv` shows both events delivered into the same S3 CloudTrail log: `625867802773_CloudTrail_eu-north-1_20261027T0140Z_ZKinf66FSNOdVER8.json.gz`.
- **Log integrity linkage:** In `evidence/public/log-integrity/validation.txt`, this exact source log (`..._ZKinf66FSNOdVER8.json.gz`) is validated as `valid` by CloudTrail digest signatures.

---

## What the evidence establishes

- Demonstrates runtime enforcement of least-privilege IAM policies.
- Confirms end-to-end auditability: permitted and denied actions both generate CloudTrail management events delivered to S3 and queryable via Athena.

---

## What remains outside scope

- Does not represent exhaustive testing of all S3 API actions.
- Does not test permission boundaries, service control policies (SCPs), or multi-account access.

