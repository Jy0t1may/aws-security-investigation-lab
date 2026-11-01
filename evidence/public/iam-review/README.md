# Evidence: Scoped IAM Policy Review and Access Analyzer Validation

## What was tested

Validation and review of nine core IAM policy snapshots using AWS IAM Access Analyzer (`validate-policy` / Access Analyzer policy checks) and manual least-privilege analysis:
- **3 Role Trust Policies:**
  1. `awslab-detection-runner-trust.policy.json`: Trust restricted to `lambda.amazonaws.com`.
  2. `awslab-detection-scheduler-trust.policy.json`: Trust restricted to `scheduler.amazonaws.com` with source account condition.
  3. `awslab-location-reader-trust.policy.json`: Trust restricted to the named lab operator role.
- **3 Role Inline Policies:**
  1. `awslab-detection-runner-inline.policy.json`: Permissions scoped strictly to Athena workgroup, Glue database, DynamoDB ledger, SNS findings topic, S3 result prefix, and CloudWatch log group.
  2. `awslab-detection-scheduler-inline.policy.json`: Permissions restricted to invoking the detection runner function and writing dead-letter messages to the failures queue.
  3. `awslab-location-reader-inline.policy.json`: Narrowly granted `s3:GetBucketLocation` on the exercise bucket; no other actions permitted.
- **3 S3 Bucket Policies:**
  1. `bucket-0-policy.policy.json`: Audit bucket policy enforcing TLS and restricting CloudTrail delivery by trail ARN and log prefix.
  2. `bucket-1-policy.policy.json`: Query results bucket policy enforcing TLS and Athena service access.
  3. `bucket-2-policy.policy.json`: Exercise bucket policy enforcing TLS.

---

## Files in this directory

| File Pair | Description | Access Analyzer Result |
| :--- | :--- | :--- |
| `awslab-detection-runner-trust.{policy,findings}.json` | Lambda detector trust policy | `0` findings (PASS) |
| `awslab-detection-runner-inline.{policy,findings}.json` | Lambda detector inline permissions | `0` findings (PASS) |
| `awslab-detection-scheduler-trust.{policy,findings}.json` | Scheduler trust policy | `0` findings (PASS) |
| `awslab-detection-scheduler-inline.{policy,findings}.json` | Scheduler inline permissions | `0` findings (PASS) |
| `awslab-location-reader-trust.{policy,findings}.json` | Test role trust policy | `0` findings (PASS) |
| `awslab-location-reader-inline.{policy,findings}.json` | Test role inline permissions | `0` findings (PASS) |
| `bucket-0-policy.{policy,findings}.json` | Audit S3 bucket resource policy | `0` findings (PASS) |
| `bucket-1-policy.{policy,findings}.json` | Query results S3 bucket resource policy | `0` findings (PASS) |
| `bucket-2-policy.{policy,findings}.json` | Exercise S3 bucket resource policy | `0` findings (PASS) |
| `access-analyzer-summary.json` | Consolidated summary of all 9 policy checks. | All 9 return PASS |
| `checksums.sha256` | SHA-256 hashes of all published files in this directory. | Validated |

---

## Fields removed or replaced

None. Account IDs (`625867802773`), resource ARNs, and role names are preserved as declared in the Terraform configurations.

---

## Artifact correlation

- **Test Role Linkage:** `awslab-location-reader-inline.policy.json` contains only `s3:GetBucketLocation` on `arn:aws:s3:::awslab-exercise-32a2346937175b2acdeb4cd420`. This policy definition is the exact root cause of the `AccessDenied` error when `s3:GetBucketTagging` was executed in `evidence/public/authorization/denied-error.txt`.
- **Detector Scope:** `awslab-detection-runner-inline.policy.json` correlates directly with the resources declared in `infrastructure/detection-execution.tf`.

---

## What the evidence establishes

- Demonstrates that all nine policies conform to AWS IAM policy validation standards with zero security or warning findings.
- Confirms tight scoping: no administrative privileges (`*.*`), no public S3 access, and strict trust boundary conditions.

---

## What remains outside scope

- Evaluated the nine specific supplied policies; did not assess AWS Organizations SCPs, operator effective permissions, or KMS key policies.
- Asynchronous failure delivery permissions were reviewed in source, not validated via live error generation.

