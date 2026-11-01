# AWSLab: Cloud Security Logging, Investigation and Detection Lab

## Overview

AWSLab is a Terraform-managed cloud-security investigation and detection lab built on a hardened private S3 foundation and CloudTrail audit logging. It correlates controlled authorization tests with CloudTrail audit records, evaluates an Athena SQL detection (`AWSLAB-DET-001`), and publishes findings through a Lambda-based pipeline to SNS, an SQS inbox, and email. A one-time scheduled execution was validated separately. A subsequent manually invoked execution delivered a newly detected finding to an email recipient.

**Last updated:** 2026-11-01
**Region:** Europe (Stockholm), `eu-north-1`
**Scope note:** This is a learning and practice project. Original evidence is retained privately. Public exports from real executions are organized separately for evidence review and publication. Each package should document its actual sources and transformations. Credentials, operational state, private configuration, and unreviewed material are excluded. Public evidence packages document execution artifacts; their inclusion is not a claim of repository-wide security clearance.

---

## Evidence Basis

Claims are supported by configuration, recorded outputs, or historical completion records as labelled below. Evidence links support traceability; filenames alone do not establish a result.

This report distinguishes:

- **Configuration reviewed:** source or policy configuration was inspected.
- **Output reviewed:** relevant command output or result content was examined.
- **Historical completion record:** completion is recorded in the project history without a separate revalidation of the associated export.
- **Not established:** the available record does not support the claim.

Private retention and public availability are recorded separately. Public exports are linked separately from locally retained originals.

| Claim | Basis | Qualification |
| --- | --- | --- |
| Storage controls and no-change plans | Historical verification record | A complete configuration read-back transcript is not linked. |
| Initial authorization correlation | Recorded CLI, Event history, and Athena results | Two controlled operations, not exhaustive authorization testing. |
| Nine synthetic tests | Fixture SQL plus historically reported PASS results | Historical PASS results; no new execution is implied. |
| Earlier SNS-to-SQS delivery | Delivery-verifier summary reviewed | Records one expected finding, one correlated finding, one matching message copy, one accepted acknowledgement, zero failed acknowledgements, and PASS. Underlying receipt and ledger records were not independently rechecked. |
| Corrected scheduled execution | Historical verifier-success record | **The accepted scheduled execution was correlated with its verifier receipt using matching request and query references. It completed successfully with one finding, zero new publications, and one previously published finding skipped. The verifier recorded one matching completed execution and an expected-scenario PASS.**|
| Bounded integrity validation | Validation summary reviewed | One regional window and its referenced files only. |
| IAM validation | Nine policy documents and empty findings arrays reviewed | Collection provenance and validation parameters were not inspected. |
| Email exercise | Invocation output and received email content reviewed | One controlled event and one recipient. |
| S3 object-event exercise | Operation summary and delivered-event correlation output reviewed | One controlled object; one matching Data event per selected operation; source-log digest validation not performed. |
| Object-event cleanup | Live selector and logging read-back reviewed; final no-change plan recorded in checkpoint history | Management-only selection restored; the cleanup apply itself returned an error. |


On November 1, 2026, six stored evidence exports were reviewed for result consistency and cross-artifact relationships. The review confirmed nine synthetic PASS results, the accepted scheduled execution and its counters, a passing delivery-verifier summary, and exact linkage of the October 27 authorization source object to the integrity-validation transcript. This was a review of recorded evidence, not a new execution of the tests or CloudTrail validator. It does not constitute a complete public-evidence security audit or verification of the live Git publication set.

---

## Architecture

The pipeline has a data path and two separate invocation paths. The function queries delivered logs when invoked; new S3 log delivery does not itself trigger it.

```
Data path:
Controlled request → CloudTrail → S3 audit logs
                                      ↑
                                Athena reads logs

Invocation paths:
One-time Scheduler validation ─┐
                               ├→ Lambda (dedicated role) → Athena query
Manual operator invocation ────┘             ↓
                                      Candidate findings
                                             ↓
                                DynamoDB publication ledger
                                             ↓
                                            SNS
                                      ┌──────┴──────┐
                                  SQS inbox       Email
```

---

## Achievements

- **Hardened storage:** three Terraform-managed S3 buckets with all four public-access blocks, bucket-owner-enforced ownership, SSE-S3 (AES256) default encryption, and explicit insecure-transport deny policies.
- **Audit logging with integrity validation:** a multi-region CloudTrail management-event trail with log-file validation. Digest and referenced-log integrity were validated for a documented window (5/5 digest files and 24/24 log files valid).
- **Investigation workflow:** an Athena workgroup with an enforced result location, SSE-S3 encryption, and a 100 MiB per-query scan cutoff. Known events were retrieved by event ID and correlated to their S3 source-log objects.
- **Least-privilege testing:** a narrowly scoped IAM role was allowed `s3:GetBucketLocation` and denied `s3:GetBucketTagging`. Both outcomes were correlated across CLI results, CloudTrail Event history, and Athena.
- **Evidence-backed detection:** `AWSLAB-DET-001` was validated with one positive and one negative recorded-event fixture, both PASS, supplemented by nine synthetic predicate cases with historically reported PASS results.
- **Cloud detection pipeline:** a Lambda function under a dedicated execution role runs the bounded detection, records publications in a DynamoDB ledger with conditional claims, and publishes to SNS.
- **Scheduled execution:** a one-time scheduled run was validated by a verifier script that caught and helped diagnose a configuration fault.
- **Policy review:** nine policy documents were checked with IAM Access Analyzer (no findings) and reviewed manually.
- **Human-facing alert:** in a separate, manually invoked execution, one controlled finding reached an email recipient and was investigated against the original S3-delivered log.
- **Bounded object-level visibility:** validated `PutObject`, `GetObject`, and `DeleteObject` for one controlled object using narrowly scoped CloudTrail data-event collection, then verified restoration of management-only logging.

---

## Implementation and Results

### 1. Private S3 foundation and transport controls
- Deployed three Terraform-managed buckets for audit logs, query results, and controlled exercises.
- Configured all four public-access blocks, bucket-owner-enforced ownership, and S3-managed AES256 default encryption.
- Added explicit insecure-transport deny policies to all three buckets. Direct AWS service principals are exempted from this deny condition; the exemption does not grant access.
- Configured query-result expiration after seven days and incomplete multipart-upload cleanup after one day. Audit evidence is retained without automatic expiration.
- Kept Terraform state, saved plans, and downloaded providers excluded from Git.
- **Verification:** successful applies, no-change follow-up plans, and AWS API read-back of bucket controls, policies, and lifecycle settings. The transport-control plan showed four additions with no changes or deletions. The complete original read-back outputs are not linked.

### 2. CloudTrail audit logging
- Created a multi-region management-event trail with Stockholm as its home region and global-service event collection enabled.
- Enabled read/write management events and log-file validation.
- Restricted S3 delivery permissions to the CloudTrail service, the specific trail ARN, and this account's log prefix, while preserving the existing transport-deny controls.
- Generated a read-only `GetBucketLocation` request against the exercise bucket and located a matching successful event in a delivered Stockholm CloudTrail log. Preserved the original compressed log, the extracted event, the source location, the retrieval time, and a SHA-256 hash under ignored private evidence.

**Cryptographic integrity validation**
- Validated the `awslab-management` trail in `eu-north-1` using `aws cloudtrail validate-logs` with verbose output.
- Requested window: 2026-10-27T00:00:00Z to 2026-10-27T04:00:00Z. The results-found window matched.
- CLI exit code 0; digest files 5/5 valid; referenced log files 24/24 valid; no invalid files reported.
- Command context, full verbose output, and exit code are preserved under ignored `evidence/private/log-integrity/`.

### 3. Athena investigation environment
- Created a dedicated workgroup with an enforced S3 query-result location, SSE-S3 encryption, and a 100 MiB per-query scan cutoff.
- Created a Glue catalog database for investigation metadata. Both resources were added with no changes to existing resources, and settings were read back through AWS APIs.
- Registered an external table over the source log's region and UTC-day prefix (`cloudtrail_delivery_day`) and retrieved a known, controlled management event by event ID. The result was compared with the preserved original event and provenance record.
- The investigation answered which action occurred, when and in which region, which identity context performed it, which bucket the request referenced, whether the record contained an error, and which S3 log object supplied the result.

| Component | Value |
| --- | --- |
| AWS region | Europe (Stockholm), `eu-north-1` |
| Athena workgroup | `awslab-investigation` |
| Catalog / database | `AwsDataCatalog` / `awslab_investigation` |
| External table | `cloudtrail_delivery_day` |
| Local evidence directory | `evidence/private/cloudtrail-delivery/` (private, not committed) |

### 4. Least-privilege authorization testing
- Deployed the `awslab-location-reader` role and its inline policy with Terraform. The policy allows only `s3:GetBucketLocation` on the exercise bucket, and trust is restricted to the existing lab operator role. The apply added 2 resources and the follow-up plan reported no changes.
- Used a separate role-assumption CLI profile.
- `GetBucketTagging` with the restricted role returned CLI exit code 254 and `AccessDenied`, because no identity-based policy allows the action.
- Retrieved and filtered CloudTrail Event history by recorded identity, exercise bucket, action, and test time window.

| Action | Time (UTC) | Outcome |
| --- | --- | --- |
| `GetBucketLocation` | 2026-10-27T01:39:37Z | No `errorCode` (1 match) |
| `GetBucketTagging` | 2026-10-27T01:39:48Z | `AccessDenied` (1 match) |

- Athena (table `awslab_investigation.cloudtrail_least_privilege_20261027`) returned both exact event IDs previously found in Event history. Both records identified the restricted role session and the exercise bucket, and both rows referenced the same S3-delivered CloudTrail `.json.gz` object.

Evidence: [Authorization evidence](../evidence/public/authorization/README.md).

### 5. Detection `AWSLAB-DET-001`
- **Detection contract:** `AWSLAB-DET-001` identifies S3 (`s3.amazonaws.com`) `GetBucketTagging` events with `AccessDenied`, an `AssumedRole` identity, and the issuer role `awslab-location-reader` (`sessionContext.sessionIssuer.userName`). The operational query evaluates a rolling 24-hour window over the date-projected `cloudtrail_management` table in `eu-north-1` and returns the source-log path for investigation. Matches represent the controlled lab authorization-failure scenario, not confirmed compromise.
- **Design:** does not hardcode fixture event IDs. Implemented as an Athena view, later run as a rolling 24-hour query over a date-projected `cloudtrail_management` table.

| Fixture | Source rows | Expected matches | Actual matches | Result |
| --- | --- | --- | --- | --- |
| Positive: denied `GetBucketTagging` | 1 | 1 | 1 | PASS |
| Negative: allowed `GetBucketLocation` | 1 | 0 | 0 | PASS |

- Source-row presence is checked so that missing data cannot pass the negative test.
- Nine synthetic predicate cases were historically reported PASS. The fixture SQL defines those cases; no fresh test execution is implied. These are supplementary predicate tests, not additional real CloudTrail events.
- The date-projected table was validated with both recorded events, and the rolling 24-hour query returned the expected denied event.

Evidence: [Detection validation evidence](../evidence/public/detection-validation/README.md).

### 6. Programmatic execution and notification
- `scripts/run_detection.py` submits the query, waits for completion, retrieves results, and preserves execution evidence (SQL snapshot, SHA-256, query ID, execution metadata, raw results, findings CSV, and manifest, kept private). Observed run: `SUCCEEDED`, 1 finding, 162,853 bytes scanned.
- Terraform deployed an SNS topic, SQS inbox, queue policy, and subscription. The queue policy is constrained to the designated topic and account.
- `scripts/publish_findings.py` published a real recorded finding. SNS publication and SQS delivery were correlated by publication and finding IDs.
- A local SQLite ledger suppressed routine repeat publication, and `scripts/ack_notifications.py` preserved receipt evidence and acknowledged only messages matching recorded publications.
- Detailed Athena results and runner statistics were reviewed. Later publication, repeat-suppression, and acknowledgement outcomes were reported successful by the operator; exact final counts were not recorded.

Evidence: [Detection validation evidence](../evidence/public/detection-validation/README.md); [Cloud publication evidence](../evidence/public/cloud-publication/README.md).

### 7. Cloud-hosted pipeline
- A Lambda function runs the bounded Athena detection under the dedicated `awslab-detection-runner` execution role. No operator profile or static credentials are used inside the function, and permissions are scoped to lab query, data, metadata, state, notification, and logging resources.
- An earlier cloud evaluation succeeded under the dedicated role: 1 finding, 214,251 bytes scanned, no publication.
- Existing local publication state was migrated to DynamoDB as a required safeguard before cloud publication was enabled.
- A new `GetBucketTagging` request from the restricted role returned `AccessDenied`. The first publishing invocation succeeded but returned 0 findings (277,860 bytes scanned, 0 publications). Delivery delay was suspected but not independently measured as the confirmed cause. The stored [delivery-verifier summary](../evidence/public/cloud-publication/delivery-verification-summary.json) was reviewed and records one expected finding, one correlated finding, one matching message copy, one accepted acknowledgement, zero failed acknowledgements, and PASS. The underlying SQS receipt, ledger item, and acknowledgement response were not independently rechecked in that review.

**Publication safeguards**
- Finding key derived from rule ID and CloudTrail event ID.
- Conditional claim before publication; completed publications are skipped.
- Unresolved claims require investigation rather than automatic reset.
- SNS acceptance is recorded before the final ledger update.
- No atomic transaction or exactly-once delivery claim.

**Delivery verification**
- Correlation checks include topic, SNS message ID, finding ID, event ID, and Athena query ID.
- Raw receipt and ledger evidence is retained before acknowledgement, and only matching SQS messages are acknowledged.

Evidence: [Cloud publication evidence](../evidence/public/cloud-publication/README.md).

### 8. Scheduled execution and root-cause analysis
- Added an EventBridge Scheduler group, invocation role and policy, one-time validation schedule, and trigger-context input. A deployment timing safeguard was added.
- An earlier scheduled execution completed: the Lambda function ran successfully and logged its trigger context, found one finding, published zero notifications, and skipped one previously published finding.
- The verifier rejected that execution because the schedule ARN and scheduled-time placeholders arrived as literal strings.
- **Root cause:** Terraform `jsonencode` escaped the angle brackets around the Scheduler context tokens.
- **Correction:** updated only the schedule input expression to restore literal angle brackets after JSON encoding. The saved plan was checked for all three literal Scheduler context tokens before applying. No IAM, detection-logic, or publication-ledger changes were required.
- After the correction, the scheduled-run verifier succeeded (final configured execution time 2026-10-31T00:42:15 UTC; verification was reported after the collection window). Raw execution evidence is kept locally under `evidence/private/scheduled-runs/`.
- The one-finding, zero-publication counts above belong to the earlier rejected execution. Final-run counts are not reproduced here.

Evidence: [Scheduled validation evidence](../evidence/public/scheduled-validation/README.md).

### 9. IAM policy validation and manual review
Reviewed nine policy documents: three role trust policies, three inline role policies, and three S3 bucket policies.
- IAM Access Analyzer returned an empty findings array for all nine. The policy documents and validation responses are preserved together under ignored `evidence/private/iam-review/`.
- Manual review findings:
  - The test-role trust is constrained to the named lab operator role.
  - The test role allows only `GetBucketLocation` on the exercise bucket.
  - The detection execution role is scoped to the lab Athena workgroup, Glue metadata, audit and result prefixes, publication table, notification topic, and function log group.
  - Scheduler trust is constrained by source account and schedule-group ARN, and Scheduler permissions target one function and one failure queue.
  - CloudTrail delivery is constrained by trail ARN and account log prefix.
  - Bucket transport-deny statements do not grant public access.
  - Resource-prefix and log-stream wildcards were reviewed and justified.
- No policy changes were identified as necessary within the reviewed scope.

Evidence: [IAM review evidence](../evidence/public/iam-review/README.md).

### 10. Human-facing alert and manual investigation
- Added a Terraform-managed email subscription to the findings topic, alongside the SQS subscription. The subscription was confirmed before the test event was generated, and the endpoint is kept in ignored local configuration.
- Issued `GetBucketTagging` with the `awslab-location-reader` role against the exercise bucket. It returned the expected `AccessDenied` (CLI exit code 254). CloudTrail event time: 2026-10-31T16:11:24Z.

**Investigation**
- Located exactly one matching event in CloudTrail Event history and confirmed the role, bucket, operation, and error.
- Confirmed that the local deployment ZIP matched the code hash recorded during the function preflight, and reviewed the packaged rolling-window SQL and table partition projection.
- Located the exact event ID in the original S3-delivered log, and preserved the original compressed log and source-object metadata.

**Delivery timing**
- The first query completed at approximately 16:14:22 UTC, and the source object's last-modified timestamp was 16:16:20 UTC. The first execution returned only an older, already-published finding.
- The query completion time precedes the object's last-modified time. After S3 presence was confirmed, a subsequent invocation detected and published the new event. No detection, IAM, schedule, or publication-ledger changes were needed.

**Final execution:** mode `CLOUD_PUBLISHING`, query state `SUCCEEDED`. The execution returned two candidates: one new finding was published and one previously published finding was skipped. Exactly one finding matched the controlled event ID, with target publication result `PUBLISHED_NOW`. This was a manually invoked execution, separate from the scheduled validation.

**Human delivery:** the project owner received the finding email. The email body carries a `created_at` value, not a recipient delivery timestamp, so inbox-arrival time was not measured. It identified `AWSLAB-DET-001`, the controlled event time, `GetBucketTagging`, `AccessDenied`, the restricted role, and the exercise bucket.

**Disposition:** expected controlled authorization denial. No evidence from this exercise established malicious activity, no containment action was warranted, and the investigation was closed as a successful lab validation. Private artifacts are retained under ignored `evidence/private/human-alert/`.

Evidence: [Human alert evidence](../evidence/public/human-alert/README.md).

### 11. Bounded S3 object-level audit logging
The earlier investigations covered bucket-management operations. This exercise extended the demonstrated visibility to selected S3 object-level activity without enabling broad data-event collection.

**Collection scope**
- Temporarily configured advanced CloudTrail selectors to preserve all management events and to collect only `PutObject`, `GetObject`, and `DeleteObject` for objects beneath a dedicated prefix in the exercise bucket.
- The audit and query-results buckets were not selected for data-event collection.
- No additional trail, bucket, IAM permission, or detection rule was required.

**Controlled operations**
- Using the lab operator identity, created one uniquely named object containing harmless text, downloaded it, and deleted it.
- The downloaded content's SHA-256 hash matched the original. Request timestamps, responses, exit codes, identity, and object references are preserved privately.
- The upload response did not supply a version ID, so the deletion targeted the unique object key without one. This observation does not independently establish the bucket's versioning configuration.

**Audit correlation**
- An initial bounded scan did not locate the records. The object operations were not repeated, and a subsequent scan found one unique CloudTrail event for each operation:

| Operation | Event time (UTC) | Unique matching events |
| --- | --- | ---: |
| `PutObject` | 2026-10-31T20:00:20Z | 1 |
| `GetObject` | 2026-10-31T20:00:21Z | 1 |
| `DeleteObject` | 2026-10-31T20:00:22Z | 1 |

- Each record matched the exact exercise bucket and object key, the recorded caller, `eu-north-1`, and the request-time window. All three were classified as Data events and contained no error code.
- Original compressed logs, extracted matching records, source-object metadata, and local SHA-256 hashes are preserved privately.

**Cleanup and reconciliation**
- Removed the temporary object-event collection and restored the original management-only selector.
- The cleanup apply returned an API error during the selector-format transition. Live AWS read-back was inspected before any retry and showed that the intended configuration had already been restored: logging enabled, all read/write management events included, no data-event resources, no excluded management-event sources, and no advanced selectors.
- The checkpoint records a subsequent fresh Terraform consistency check with no proposed changes.

**Interpretation**
- This exercise demonstrates selected object-level audit visibility and evidence correlation for one controlled object. It does not establish comprehensive S3 monitoring, an object-access detection rule, or cryptographic validation of these source logs. `AWSLAB-DET-001` was not extended and still detects the earlier bucket-management authorization-denial scenario.
- The narrow collection scope was intended to limit additional data-event logging costs. Actual billed cost and credit application were not measured.

Evidence: [Object events evidence](../evidence/public/object-events/README.md).

---

## Engineering Findings

- **Verifiers catch what a success status hides.** The scheduled run completed without error, but the verifier rejected it because the trigger context was wrong. The cause was Terraform `jsonencode` escaping angle brackets, not an AWS fault.
- **An empty or unchanged detection result is not necessarily a failure.** Two initial executions returned no new finding. For the October 30 attempt, delivery delay remained an unverified explanation. For the October 31 exercise, the source object's last-modified timestamp (16:16:20 UTC) followed the initial query's completion (about 16:14:22 UTC); the exact event was then located in S3 and published on the next invocation. This is an observed chronology, not a general delivery guarantee.
- **A failed apply does not establish the final remote state.** After the selector-transition error, live AWS read-back showed that the intended cleanup had already occurred. The read-back was inspected before any retry; the checkpoint then records a successful fresh Terraform consistency check.
- **Duplicate suppression needs shared state in the cloud.** Local SQLite state is not shared between cloud invocations, so publication state was migrated to DynamoDB before cloud publication was enabled.
- **Evidence benefits from a documented publication boundary.** Originals remain private; reviewed execution exports can retain non-secret correlation identifiers. A directory named public is not a substitute for content inspection and a recorded transformation policy.

---

## Skills Demonstrated

| Area | What was practiced in this project |
| --- | --- |
| **Infrastructure as code** | Terraform initialization, provider locking, validation, saved-plan review, apply, and no-change follow-up plans. Also `for_each`, resource references, `jsonencode`, dependencies, and safe modification of existing policies. |
| **Cloud storage security** | S3 public-access blocks, ownership controls, default encryption, explicit-deny transport policies, lifecycle design, and evidence-retention tradeoffs. |
| **IAM and access control** | Resource-based policies, service-principal and source-ARN restrictions, narrowly scoped inline policies, constrained role trust, separate operator and test identities, and temporary role authentication with session renewal. |
| **Authorization testing** | Runtime allowed-versus-denied testing and interpretation of an implicit denial (CLI exit code 254, `AccessDenied`). |
| **IAM policy review** | IAM Access Analyzer validation plus manual review of trust conditions, resource scope, and wildcard justification. |
| **Audit logging (CloudTrail)** | Multi-region trail coverage design, management versus data event distinctions, log-file validation, delivery verification, and digest validation with the AWS CLI. |
| **Log investigation (Athena/SQL)** | Workgroup isolation and cost controls, Glue catalog versus source table versus query result, filtering by event ID, selecting nested struct fields, extracting values from JSON request parameters, and partition-projected queries over a bounded window. |
| **Evidence handling** | Preserving original files, SHA-256 hashing, provenance records, correlation by action, identity, resource, region, and time, and separating private raw evidence from a redacted public report. |
| **Detection engineering** | SQL detection rule without hardcoded fixture event IDs, positive and negative validation that checks source-row presence so missing data cannot pass the negative test, and real-event integration tests kept distinct from synthetic predicate tests. |
| **Detection pipeline** | Programmatic query execution with evidence capture (SQL snapshot, SHA-256, query ID, manifest), SNS/SQS notification delivery, and message correlation by publication and finding IDs. |
| **Cloud workload security** | Dedicated Lambda execution role with no operator profile or static credentials inside the function, scoped to lab query, data, metadata, state, notification, and logging resources. |
| **State and duplicate control** | DynamoDB publication ledger with finding keys derived from rule ID and CloudTrail event ID, conditional claims before publication, and no automatic reset of unresolved claims. |
| **Scheduled execution and root-cause analysis** | EventBridge Scheduler validation with a verifier that rejected a run whose context values were wrong. Traced the fault to Terraform `jsonencode` escaping and applied a minimal correction. |
| **Alert handling and investigation** | Email alert delivery, event confirmation in Event history, retrieval of the exact event ID from the original S3 log, and a documented disposition. |
| **Troubleshooting** | Athena workgroup context, table-registration dependencies, and log-delivery timing. |
| **Secure repository hygiene** | Separating private originals and operational artifacts from reviewed public evidence; checking ignore rules and tracked paths separately. |

---

## Tools and Technologies

- **Cloud:** AWS S3, IAM, IAM Access Analyzer, CloudTrail, Athena, AWS Glue Data Catalog, AWS Lambda, Amazon EventBridge Scheduler, Amazon DynamoDB, Amazon SNS, Amazon SQS, AWS Organizations SCP (encountered as a constraint)
- **IaC:** Terraform
- **Tooling:** AWS CLI, Git, SQLite (local publication ledger in the early local pipeline)
- **Languages/formats:** SQL (Athena), Python, HCL, JSON, CSV

---

## Public evidence reference guide

Eight evidence packages group the execution records used to explain the project. The links below identify their scope and key artifacts. Historical outcomes remain labelled; a linked filename does not independently establish a passing result or safe redaction.

Start with the [evidence index](../evidence/README.md). Each package README should explain actual sources, transformations, correlation, and scope. Redacted exports remain derivatives of genuine executions; they must not be described as synthetic fixtures or as cryptographically identical to the originals.

| Claim area | Package explanation | Selected artifacts |
| --- | --- | --- |
| Authorization | [Package README](../evidence/public/authorization/README.md) | [allowed-exit-code.txt](../evidence/public/authorization/allowed-exit-code.txt); [denied-error.txt](../evidence/public/authorization/denied-error.txt); [athena-permission-test-results.csv](../evidence/public/authorization/athena-permission-test-results.csv); [matched-event-location.json](../evidence/public/authorization/matched-event-location.json); [matched-event-tagging.json](../evidence/public/authorization/matched-event-tagging.json) |
| Detection validation | [Package README](../evidence/public/detection-validation/README.md) | [AWSLAB-DET-001-validation.csv](../evidence/public/detection-validation/AWSLAB-DET-001-validation.csv); [AWSLAB-DET-001-unit-tests.csv](../evidence/public/detection-validation/AWSLAB-DET-001-unit-tests.csv); [athena-execution.json](../evidence/public/detection-validation/athena-execution.json); [findings.csv](../evidence/public/detection-validation/findings.csv) |
| Cloud publication | [Package README](../evidence/public/cloud-publication/README.md) | [lambda-execution-summary.json](../evidence/public/cloud-publication/lambda-execution-summary.json); [finding-payload.json](../evidence/public/cloud-publication/finding-payload.json); [dynamodb-finding-ledger.json](../evidence/public/cloud-publication/dynamodb-finding-ledger.json); [sqs-notification-receipt.json](../evidence/public/cloud-publication/sqs-notification-receipt.json); [delivery-verification-summary.json](../evidence/public/cloud-publication/delivery-verification-summary.json) |
| Scheduled validation | [Package README](../evidence/public/scheduled-validation/README.md) | [schedule-target-escaped.json](../evidence/public/scheduled-validation/schedule-target-escaped.json); [schedule-target-remediated.json](../evidence/public/scheduled-validation/schedule-target-remediated.json); [scheduled-execution-summary.json](../evidence/public/scheduled-validation/scheduled-execution-summary.json); [verifier-receipt.json](../evidence/public/scheduled-validation/verifier-receipt.json) |
| Log integrity | [Package README](../evidence/public/log-integrity/README.md) | [context.txt](../evidence/public/log-integrity/context.txt); [exit-code.txt](../evidence/public/log-integrity/exit-code.txt); [validation.txt](../evidence/public/log-integrity/validation.txt) |
| IAM review | [Package README](../evidence/public/iam-review/README.md) | [access-analyzer-summary.json](../evidence/public/iam-review/access-analyzer-summary.json); [awslab-detection-runner-inline.policy.json](../evidence/public/iam-review/awslab-detection-runner-inline.policy.json); [awslab-detection-runner-inline.findings.json](../evidence/public/iam-review/awslab-detection-runner-inline.findings.json) |
| Human alert | [Package README](../evidence/public/human-alert/README.md) | [request-exit-code.txt](../evidence/public/human-alert/request-exit-code.txt); [cloudtrail-event.json](../evidence/public/human-alert/cloudtrail-event.json); [lambda-execution-summary.json](../evidence/public/human-alert/lambda-execution-summary.json); [email-alert-payload.json](../evidence/public/human-alert/email-alert-payload.json) |
| Object events | [Package README](../evidence/public/object-events/README.md) | [operation-summary.json](../evidence/public/object-events/operation-summary.json); [matched-events.json](../evidence/public/object-events/matched-events.json); [selectors-enabled.json](../evidence/public/object-events/selectors-enabled.json); [selectors-after-cleanup.json](../evidence/public/object-events/selectors-after-cleanup.json); [terraform-final-plan.txt](../evidence/public/object-events/terraform-final-plan.txt) |

Publication rules: preserve originals locally; retain meaningful timestamps, conditions, outcomes, and correlation. Review each export for credentials, personal metadata, actionable links, and SQS receipt handles. Account IDs and resource identifiers are not automatically credentials; disclose or consistently alias them according to the owner's documented policy. Do not publish private-to-public alias mappings if they defeat redaction. Checksums of exports establish byte consistency, not AWS origin or cryptographic validation of transformed records.

---

## Limitations

**Scope and environment**
- This is a lab environment; results demonstrate practice, not production readiness.
- The trail was configured for multi-region management-event collection. The investigations, detection query, and runtime validations described here were scoped to one account and `eu-north-1`; equivalent coverage in other regions was not demonstrated.
- The detection uses a rolling 24-hour window, which is not a delivery-delay guarantee.
- The Athena tables and views are SQL-managed, not Terraform-managed.
- The Athena scan cutoff is not an account spending cap.
- Earlier project notes described an SCP-related obstacle to budget-notification verification. The project owner subsequently reported that budget notifications were working. Supporting verification output is not included in this report.

**Detection and testing**
- Initial real-event rule validation used one denied `GetBucketTagging` positive fixture and one successful `GetBucketLocation` negative fixture. The synthetic-test SQL defines nine predicate cases, including another role, another error, and a null error code. The project record reports that all nine previously passed; no fresh execution is implied by the historical results. Equivalent additional real-event negative scenarios were not demonstrated.
- Synthetic tests evaluate a copied, flat-field predicate. They do not validate ingestion, nested-field extraction, alert delivery, or automatic equivalence with the deployed detection.
- Two bucket-management actions were tested for authorization; this is not exhaustive authorization coverage.
- The expected lab denials are not evidence of malicious activity. No compromise was detected or demonstrated.
- Selected fields identify role context, not necessarily the individual human behind a session.
- Correlation of the initial test event did not use a client-captured request ID.

**Logging and integrity**
- Cryptographic integrity validation covers the digest-referenced files in one regional delivery window, 2026-10-27T00:00:00Z to 04:00:00Z (5/5 digest files and 24/24 log files valid). It does not establish account-wide logging completeness or continuous integrity monitoring, and it does not establish that every possible event was logged.
- The source-log URI shared by the October 27 allowed and denied authorization-test events was matched exactly to a valid log-file entry in the CloudTrail validation transcript. This establishes that the investigation’s source object was included in the documented validation results.
- The October 31 alert investigation used an original S3-delivered log outside the October 27 validation window. The October 27 validation does not establish cryptographic integrity for that object, and no separate validation result for it is included here.
- Selected S3 object-level activity was validated for one controlled object: `PutObject`, `GetObject`, and `DeleteObject` were correlated with delivered CloudTrail Data events, and the temporary collection was removed afterward. Comprehensive object-level monitoring and an object-access detection rule were not implemented. The preserved source-log copies were locally hashed but were not separately validated against CloudTrail digests.

**Policy review**
- The review covers nine policy snapshots. Retrieval provenance and validation-request parameters are not established by the recorded policy/result pairs alone; no exhaustive effective-permissions conclusion is drawn.
- The nine-policy validation did not include SNS or SQS resource policies. Separately, the SQS inbox policy was reviewed in Terraform source and restricts SNS delivery by topic ARN and source account. Its deployed-state equivalence was not independently established in that review.
- Operator permissions, `iam:PassRole` controls, permissions boundaries, SCP interactions, and exhaustive effective permissions were not assessed.

**Pipeline and operations**
- Scheduled execution was validated with a one-time schedule. The final disposition of that schedule is not recorded in this report, and recurring operation is not claimed.
- A failure-queue configuration exists (`detection-failures.tf`). No delivery-test evidence was reviewed for Scheduler delivery-failure capture or Lambda asynchronous failure destinations. The synchronous email exercise does not establish behavior on either failure path.
- Human-facing delivery was exercised with one controlled finding and one email recipient. The October 31 output establishes publication and email receipt; it does not establish fresh SQS receipt and acknowledgement for that notification. Continuous delivery reliability, automated containment, and production incident-response capability were not demonstrated.
- No exactly-once delivery claim. Ambiguous publication states require manual reconciliation.
- Runtime-provided SDK dependencies in the Lambda function are not pinned.
- The migration safeguard remains in the deployed configuration.

**Controls not tested live**
- HTTP-denial behavior of the transport-deny policies and timed lifecycle expiration were not tested.

---

## Repository navigation

See the [complete repository index](repository-index.md) for individual source files, Terraform configuration, query/test artifacts, public evidence packages, and the purpose of locally retained materials. The [rule reference](detections/AWSLAB-DET-001.md) describes the detection and triage workflow; the [evidence index](../evidence/README.md) organizes supporting exports.
