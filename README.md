# AWSLab: Cloud Security Logging, Investigation and Detection

A Terraform-managed AWS homelab demonstrating how to investigate controlled authorization failures, validate a SQL detection, and deliver evidence-backed findings through a cloud-hosted pipeline.

The project connects S3 security controls, CloudTrail audit records, Athena investigation, IAM authorization testing, and Python automation. Findings are published using Lambda, DynamoDB, SNS, and SQS, with a separately validated email notification path.

[Read the full project report](docs/report.md) for implementation, results, troubleshooting, and limitations. Browse the [evidence index](evidence/README.md) and the [development record](docs/progress.md) for supporting exports and historical checkpoints.

## What this project demonstrates

- Private S3 storage with public-access blocks, ownership controls, encryption, and transport-deny policies.
- Correlation of allowed and denied AWS requests across CLI responses, CloudTrail Event history, and S3-backed Athena queries.
- A lab-specific SQL detection, `AWSLAB-DET-001`, with recorded-event fixtures and supplementary synthetic predicate tests.
- A dedicated Lambda execution role and shared DynamoDB publication state for duplicate suppression.
- Finding publication through SNS, earlier SQS delivery verification, and a subsequent controlled finding received by email.
- A separately verified one-time scheduled execution, including diagnosis of escaped Scheduler context placeholders.
- Bounded CloudTrail integrity validation: 5/5 digest files and 24/24 referenced logs valid for the documented window.
- A scoped nine-policy review with empty IAM Access Analyzer findings arrays.
- Selected `PutObject`, `GetObject`, and `DeleteObject` data-event logging for one test object, followed by verified restoration of management-only collection.

These are controlled lab results, not evidence of compromise or a claim of production readiness. The report distinguishes inspected output from historically owner-reported outcomes.

## Architecture

```text
Controlled AWS request -> CloudTrail -> S3 audit logs
                                          |
                                     read by Athena
                                          ^
One-time Scheduler validation --+          |
                               +-> Lambda query -> candidate findings
Manual operator invocation ----+                       |
                                              DynamoDB publication ledger
                                                       |
                                                      SNS
                                                 +-----+-----+
                                                 |           |
                                                SQS        Email
```

The invocation paths and log-delivery path are separate. S3 log delivery does not trigger the function. The scheduled validation and the successful email exercise were separate executions; recurring operation is not claimed.

The object-event exercise demonstrated logging visibility only. It did not extend the authorization-denial detection.

## Repository guide

Source, documentation, and public execution evidence are organized separately. Public location is not a substitute for content review or checking what Git tracks.

| Path | Purpose |
| --- | --- |
| [`infrastructure/`](infrastructure/) | Terraform configuration for storage, logging, IAM, Athena, the cloud detection pipeline, notifications, state, and scheduled validation. |
| [`cloud/detection_runner/`](cloud/detection_runner/) | Lambda handler and publication logic. |
| [`queries/`](queries/) | SQL for investigation, table/view definitions, detections, and validation fixtures. |
| [`scripts/`](scripts/) | Local execution, package-building, evidence collection, migration, notification, and verification utilities. |
| [`evidence/public/`](evidence/public/) | Reviewed machine-readable evidence exports from real executions across authorization, detections, publication, scheduling, log integrity, IAM review, alerting, and object events. |
| [`docs/report.md`](docs/report.md) | Main explanatory report and evidence-qualified results. |
| [`docs/repository-index.md`](docs/repository-index.md) | Detailed individual-file repository and evidence navigation. |
| [`docs/progress.md`](docs/progress.md) | Historical checkpoint record; earlier entries describe the state at their original checkpoint. |
| [`docs/detections/AWSLAB-DET-001.md`](docs/detections/AWSLAB-DET-001.md) | Rule-specific reference; read alongside the implementation SQL. |
| [`docs/detection-test-matrix.md`](docs/detection-test-matrix.md) | Exact synthetic fixtures, expectations, historical outcomes, and test boundaries. |

Generated packages, private evidence, local configuration, Terraform state, and saved plans are not public source artifacts.

## Reading and using the project

1. Start with the full report and its evidence-basis table.
2. Review the Terraform source and the SQL definitions before deployment.
3. Read a script's arguments and implementation before running it; some scripts invoke workloads, publish findings, migrate state, or acknowledge queue messages.
4. Supply your own authenticated AWS configuration and private input values. Do not copy account-specific resource names, email endpoints, or historical validation timestamps from another deployment.

This README is not a one-command deployment guide. The project includes SQL-managed tables and views in addition to Terraform-managed infrastructure. Local variable files, permissions, build inputs, and execution order need to be understood before applying it in another account.

Do not run `terraform apply`, publication-state migration, or message acknowledgement merely to browse or validate the repository. Any AWS use may incur charges; credits and budget alerts are not a hard spending limit.

## Detection and evidence boundaries

`AWSLAB-DET-001` identifies denied S3 `GetBucketTagging` requests by the `awslab-location-reader` assumed role. Its operational query uses a rolling 24-hour window over Stockholm audit logs and returns source-log references for investigation.

- Synthetic predicate cases supplement real-event tests; they do not establish ingestion or delivery correctness.
- Conditional publication claims and duplicate suppression do not establish exactly-once delivery.
- Selected cryptographic log validation does not establish continuous integrity monitoring or logging completeness.
- Email was exercised with one controlled finding and one recipient.
- Failure-destination delivery and the one-time schedule's final disposition retain the qualifications documented in the report.

## Private data and generated artifacts

Keep the following out of commits:

- Original/unreviewed material under `evidence/private/` and `downloads/`; publish reviewed event, query, receipt, and manifest exports separately when safe.
- `infrastructure/build/`, provider downloads, Python caches, and local ledgers.
- Terraform state and state backups, saved plans, and private variable files.
- Credentials, tokens, email confirmation/unsubscribe links, private email configuration, and unredacted screenshots.

Track Terraform source and `infrastructure/.terraform.lock.hcl`. Execution exports intended for publication are organized under [`evidence/public/`](evidence/public/). Review their contents, transformations, correlation, and checksums before committing. Keep originals, credentials, Terraform state, and operational configuration private. Non-secret identifiers may be retained deliberately; do not confuse them with credentials.

## Public evidence navigation

| Evidence | Package |
| --- | --- |
| Authorization | [Explanation and artifacts](evidence/public/authorization/README.md) |
| Detection validation | [Explanation and artifacts](evidence/public/detection-validation/README.md) |
| Cloud publication | [Explanation and artifacts](evidence/public/cloud-publication/README.md) |
| Scheduled validation | [Explanation and artifacts](evidence/public/scheduled-validation/README.md) |
| Log integrity | [Explanation and artifacts](evidence/public/log-integrity/README.md) |
| IAM review | [Explanation and artifacts](evidence/public/iam-review/README.md) |
| Human alert | [Explanation and artifacts](evidence/public/human-alert/README.md) |
| Object events | [Explanation and artifacts](evidence/public/object-events/README.md) |

The [full report](docs/report.md) links selected artifacts, while the [repository index](docs/repository-index.md) provides individual-file navigation. Read package provenance before interpreting results. An email payload is not an inbox timestamp; a checksum is not proof of AWS origin; file presence is not a passing test. If exports substantiate older owner-reported results, update their evidence basis only after inspecting those exports.

## Technologies and skills

AWS S3, CloudTrail, Athena, Glue Data Catalog, IAM and IAM Access Analyzer, Lambda, DynamoDB, SNS, SQS, and EventBridge Scheduler; Terraform, Python, SQL, AWS CLI, and Git.

Practiced skills include infrastructure as code, least-privilege authorization testing, audit investigation, detection validation, evidence correlation, publication safeguards, root-cause analysis, and secure repository hygiene.
