# Evidence: CloudTrail Cryptographic Log Integrity Validation

## What was tested

Validation of CloudTrail log-file integrity and digest signatures using the AWS CLI command `aws cloudtrail validate-logs --verbose`:
- **Target Trail:** `arn:aws:cloudtrail:eu-north-1:625867802773:trail/awslab-management`
- **Region:** `eu-north-1` (Stockholm)
- **Delivery Window:** `2026-10-27T00:00:00Z` to `2026-10-27T04:00:00Z`

---

## Files in this directory

| File | Origin | Description |
| :--- | :--- | :--- |
| `context.txt` | Environment capture | Records CLI version, home region, trail ARN, and requested time boundaries. |
| `exit-code.txt` | Shell exit code | Exit code `0` confirming that all validated files passed cryptographic checks without errors. |
| `validation.txt` | AWS CLI stdout | Full verbose output from `validate-logs` enumerating 5/5 digest files valid and 24/24 referenced log files valid. |
| `checksums.sha256` | Local verification | SHA-256 hashes of all published files in this directory. |

---

## Fields removed or replaced

None. The output reflects the unmodified text emitted by the AWS CLI validation tool.

---

## Artifact correlation

- **Source Log Linkage:** In `validation.txt`, line 15:
  `Log file s3://awslab-audit-c2b8fb5274a4f0eaf19e0a97bd/AWSLogs/625867802773/CloudTrail/eu-north-1/2026/10/27/625867802773_CloudTrail_eu-north-1_20261027T0140Z_ZKinf66FSNOdVER8.json.gz valid`
  This exact file is the source log recorded in:
  - `evidence/public/authorization/athena-permission-test-results.csv`
  - `evidence/public/detection-validation/findings.csv`
  This directly links the least-privilege permission test events (`GetBucketLocation` and `GetBucketTagging`) to a cryptographically validated CloudTrail log object.

---

## What the evidence establishes

- Proves that CloudTrail digest files were properly delivered and cryptographically verified for the documented 4-hour window.
- Establishes that the 24 referenced log files delivered during that period were unmodified since CloudTrail signed their digests.

---

## What remains outside scope

- Bounded to the Stockholm region and the specified 4-hour window; does not prove continuous or account-wide integrity validation.
- Validates only logs referenced by the digest chain; does not establish that every hypothetical event was logged.

