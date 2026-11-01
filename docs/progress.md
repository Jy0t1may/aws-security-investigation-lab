# AWSLab development record

Last updated: 2026-11-01
Region used for the documented investigations: eu-north-1

This is a concise historical checkpoint record, not a second technical report. Earlier checkpoints describe what had been demonstrated at that time. Read the [full report](report.md) for the current explanation and consolidated limitations, the [evidence index](../evidence/README.md) for package provenance, and the [detection test matrix](detection-test-matrix.md) for fixture detail.

Evidence basis: checkpoints distinguish examined outputs from historical completion records. Public exports support traceability; their presence does not by itself establish safe redaction, valid checksums, or Git tracking. Current scope boundaries are consolidated in the report.

## Implementation checkpoints

### 1. Private S3 foundation

Deployed three Terraform-managed buckets for audit logs, query results, and controlled exercises. Configured all four public-access blocks, bucket-owner-enforced ownership, and SSE-S3 AES256 default encryption. The owner reported successful apply, no-change follow-up planning, and API read-back. State, saved plans, and providers were excluded from the intended publication set. A complete read-back transcript is not linked.

### 2. Transport controls and result retention

Added explicit insecure-transport deny policies to all three buckets, with the direct AWS-service exemption documented as an exemption rather than an access grant. Query results received seven-day expiration and one-day incomplete multipart-upload cleanup; audit evidence had no automatic expiration. The checkpoint recorded four additions, no changes/deletions, successful apply, read-back, and a subsequent no-change plan. Live HTTP-denial behavior and actual timed expiration were not exercised; these are scope boundaries, not reopened tasks.

### 3. CloudTrail management-event configuration

Created a multi-region management-event trail with Stockholm as home region, global-service events, read/write management collection, and log-file validation enabled. Restricted S3 delivery to the CloudTrail service, the designated trail, and the account log prefix. Deployment and follow-up logging/selector checks were reported successful. Multi-region configuration is not proof of tested event delivery in every region.

### 4. Initial management-event delivery

Generated a controlled GetBucketLocation request and located a matching successful event in an original delivered Stockholm log. Preserved the compressed source, extracted event, retrieval context, provenance, and local SHA-256. This established one event path. A local hash was not presented as signed CloudTrail digest validation. The later [authorization evidence](../evidence/public/authorization/README.md) is the public correlation entry point.

### 5. Athena environment

Created the dedicated investigation workgroup and Glue database. Enforced the result location and SSE-S3 encryption and set a 100 MiB per-query scan cutoff. Two additions, API read-back, and a no-change follow-up were reported. The query cutoff is not an account spending cap.

### 6. First source-correlated Athena query — 2026-10-21

Retrieved a known October 20 event by event ID using cloudtrail_delivery_day in awslab_investigation. Correlated action, identity context, region, UTC time, request resource, error status, and source-log path with preserved evidence. Wrong workgroup selection, an unregistered table, and a missing local CSV were diagnosed separately; table creation and preservation of the successful result were reported complete. Tables/views were SQL-managed rather than Terraform-managed. This did not demonstrate object-level coverage or a detection rule.

### 7. Least-privilege runtime tests — 2026-10-27

Deployed the location-reader role and inline policy allowing only GetBucketLocation on the exercise bucket; trust was constrained to the existing operator role. Two resources were added and a follow-up plan reported no changes. Used a separate assumed-role CLI profile and renewed expired operator authentication without broadening permissions.

| Operation | Recorded event time, UTC | Result |
| --- | --- | --- |
| GetBucketLocation | 2026-10-27T01:39:37Z | One matching record without errorCode |
| GetBucketTagging | 2026-10-27T01:39:48Z | AccessDenied; CLI exit code 254 |

Event history and Athena returned the same two event IDs, role session, bucket, and source log. This was a two-operation authorization exercise, not exhaustive effective-permissions analysis. See the [authorization package](../evidence/public/authorization/README.md) and [Athena result export](../evidence/public/authorization/athena-permission-test-results.csv).

### 8. First detection validation — 2026-10-27

Implemented AWSLAB-DET-001 for AccessDenied GetBucketTagging by the location-reader assumed role, using issuer-role context without hardcoded fixture event IDs. Recorded-event validation returned one positive match and zero negative matches; both source fixtures were present. The negative fixture was the allowed GetBucketLocation event. Later synthetic fixtures separately covered other predicate variations.

References: [recorded-event validation](../evidence/public/detection-validation/AWSLAB-DET-001-validation.csv), [validation SQL](../queries/tests/AWSLAB-DET-001-validation.sql), and [rule documentation](detections/AWSLAB-DET-001.md).

### 9. Local detection and notification pipeline — 2026-10-27

Validated the date-projected source table and rolling 24-hour query. Nine synthetic predicate cases were historically reported PASS; the fixture SQL defines their inputs and expected results; no fresh execution is implied. These were not additional real CloudTrail events and did not validate ingestion or delivery.

The Python runner completed with one finding and 162,853 bytes scanned and preserved SQL/hash/query/execution/result/manifest evidence. Terraform supplied SNS, SQS, subscription, and a source-constrained queue policy. Local publication, repeat suppression through SQLite, and matching-message acknowledgement were reported successful; exact final notification counts were not recorded. This checkpoint was manually launched and used local state.

References: [detection package](../evidence/public/detection-validation/README.md), [synthetic CSV](../evidence/public/detection-validation/AWSLAB-DET-001-unit-tests.csv), and [cloud-publication package](../evidence/public/cloud-publication/README.md).

### 10. Cloud-hosted publication — 2026-10-30

Moved detection to Lambda under a dedicated execution role with no operator credentials inside the function. Migrated prior publication state into DynamoDB before enabling cloud publication. An earlier evaluation returned one finding and 214,251 scanned bytes without publication.

A new controlled denial was generated. The first publishing invocation returned zero findings and zero publications with 277,860 scanned bytes; delivery delay was suspected, not established. A later invocation and SQS delivery correlation were reported successful. Publication safeguards used rule/event-derived keys, conditional claims, completed-publication suppression, and preserved ambiguous outcomes rather than automatic resets. Exactly-once delivery was not claimed.

References: [execution summary](../evidence/public/cloud-publication/lambda-execution-summary.json), [ledger export](../evidence/public/cloud-publication/dynamodb-finding-ledger.json), and [delivery summary](../evidence/public/cloud-publication/delivery-verification-summary.json). Historical claims should be upgraded only when the linked records establish their execution and outcome.

### 11. One-time scheduled validation — 2026-10-31

A scheduled execution ran but failed attribution checks because context placeholders remained literal. Its one-finding/zero-publication/one-skipped counters belong to the rejected execution. Root cause was Terraform jsonencode escaping angle brackets. Corrected the target input, checked the saved plan for literal tokens, and introduced a timing safeguard without changing detection logic, IAM, or ledger state.

The corrected verifier run at configured target 2026-10-31T00:42:15 UTC was reported successful. Its final counters were not supplied. This established one-time scheduling, not recurring operation.

References: [scheduled-validation explanation](../evidence/public/scheduled-validation/README.md), [verifier export](../evidence/public/scheduled-validation/verifier-receipt.json), and [before/after target exports](../evidence/public/scheduled-validation/schedule-target-remediated.json).

### 12. Bounded log-integrity validation — 2026-10-31

Validated the existing regional trail for 2026-10-27T00:00:00Z–04:00:00Z using verbose CloudTrail validation. Requested and found windows matched; exit code was zero, with 5/5 digests and 24/24 logs valid. The summary was reviewed. Explicit inclusion of the original authorization-test source object was not recorded. This window does not validate October 31 source objects or continuous logging completeness.

References: [validation context](../evidence/public/log-integrity/context.txt), [exit code](../evidence/public/log-integrity/exit-code.txt), [transcript](../evidence/public/log-integrity/validation.txt), and [package scope](../evidence/public/log-integrity/README.md).

### 13. Scoped policy validation and review — 2026-10-31

Reviewed three trust policies, three inline role policies, and three bucket policies. Each validation response contained an empty findings array. Inspected trust constraints, actions, resource scope, and prefix/log-stream wildcards. No required narrowing was identified within these supplied snapshots. Retrieval provenance and validation request parameters were not independently inspected. Operator effective permissions, PassRole controls, boundaries, and SCP interactions were outside scope. The SQS inbox policy was later reviewed separately in Terraform source.

References: [IAM scope](../evidence/public/iam-review/README.md), [validation summary](../evidence/public/iam-review/access-analyzer-summary.json), and the [complete policy-file index](repository-index.md).

### 14. Human alert and investigation — 2026-10-31

Added and confirmed an email subscription alongside SQS, with the endpoint in private local input. Generated a new denied GetBucketTagging event at 16:11:24Z using the restricted role and preserved exit code 254. Matched the event in Event history and the original S3 log; compared the local ZIP with the deployed preflight code hash and inspected packaged SQL/projection.

The initial query completed around 16:14:22Z; the source object's last-modified timestamp was 16:16:20Z. After source presence was confirmed, a separate invocation succeeded in CLOUD_PUBLISHING mode with two findings, one new publication, and one skipped prior finding. Exactly one target event matched and was PUBLISHED_NOW. The owner supplied the received email payload; inbox-arrival time was not measured. Disposition: expected controlled lab denial, no established compromise, no containment warranted.

References: [event](../evidence/public/human-alert/cloudtrail-event.json), [execution](../evidence/public/human-alert/lambda-execution-summary.json), [email payload](../evidence/public/human-alert/email-alert-payload.json), and [correlation explanation](../evidence/public/human-alert/README.md). The payload does not prove fresh SQS receipt or acknowledgement for this notification.

### 15. Bounded object-event visibility — 2026-10-31

Temporarily selected only PutObject, GetObject, and DeleteObject beneath the exercise prefix while preserving management events. One harmless object was uploaded, downloaded, and deleted; downloaded SHA-256 matched the original. No uploaded version ID was returned, so deletion used the unique key without a version ID.

A later scan found one Data event per operation at 20:00:20Z, 20:00:21Z, and 20:00:22Z, respectively. Bucket/key, caller, region, request timing, and no-error checks matched. The early empty scan was preserved and operations were not repeated.

The cleanup apply reported an API error during selector-format transition. Live read-back showed management-only selection, no data resources or advanced selectors, no excluded management sources, and logging enabled. A fresh no-change plan was subsequently reported successful. Actual billed cost and credit application were not measured. This was logging visibility, not a new detection or source-log digest validation.

References: [matched records](../evidence/public/object-events/matched-events.json), [operation summary](../evidence/public/object-events/operation-summary.json), [cleanup selectors](../evidence/public/object-events/selectors-after-cleanup.json), [final-plan transcript](../evidence/public/object-events/terraform-final-plan.txt), and [package explanation](../evidence/public/object-events/README.md).

### 16. Evidence packaging and documentation — 2026-11-01

Organized eight evidence packages with package explanations and checksum manifests, while retaining originals privately. The packaging record describes preservation of useful correlation identifiers, redaction of client IPs and session access-key identifiers, and removal of actionable email links. Those handling decisions do not substitute for inspecting the final exported bytes.

Separated the landing README, technical report, chronological record, rule reference, test matrix, and [repository index](repository-index.md). Preserved source and build paths. The report links execution artifacts directly; the standalone index carries the detailed individual-file descriptions. Removed stale liftoff/next-step scaffolding and reconciled the detection reference with the cloud pipeline and rolling-window query.

Publication controls distinguish eligible files from already-tracked files. Public payload inspection, checksum verification, tracked-file review, and repository-history exposure remain separate controls; no blanket publication clearance is claimed. No additional AWS operation is needed to improve documentation.

## Continuing evidence boundaries

Failure-capture delivery, the one-time schedule's final disposition, and investigation-specific digest linkage retain the qualifications in the report. Earlier budget-notification trouble was subsequently reported resolved by the owner; it is not an active implementation task. Public evidence links and the intended tracked publication set must be checked locally before publication. No new cloud test is required merely to package the repository.
