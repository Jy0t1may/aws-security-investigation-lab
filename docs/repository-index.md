# AWSLab repository index

A technical navigation reference for the implementation, documentation, and evidence packages. Read the [technical report](report.md) for results and evidence qualifications, and the [project README](../README.md) for an introduction. A filename or checksum is not proof of successful execution or safe publication; interpret evidence through its package explanation.

### Root and documentation

| Public path | Purpose and relationship |
| --- | --- |
| [README.md](../README.md) | Landing page, architecture summary, and evidence/documentation navigation. |
| [.gitignore](../.gitignore) | Publication boundary for private originals, credentials, state, plans, local inputs, caches, and generated packages. It does not remove already-tracked content. |
| [docs/](./) | Narrative report, checkpoint history, and detection references. |
| [report.md](report.md) | Full technical explanation, results, evidence references, and limitations. |
| [repository-index.md](repository-index.md) | This individual-file navigation reference. |
| [progress.md](progress.md) | Chronological checkpoints with historical evidence boundaries; not a duplicate report. |
| [detection-test-matrix.md](detection-test-matrix.md) | Exact fixture inputs, expectations, historical results, and synthetic-test limitations. |
| [docs/detections/](detections/) | Rule-specific documentation. |
| [AWSLAB-DET-001.md](detections/AWSLAB-DET-001.md) | Rule documentation; consult the linked SQL for the implementation and the evidence packages for outcomes. Includes the rule predicate, implementation evolution, triage, and response safeguards. |

### Cloud runtime

| Public path | Purpose and relationship |
| --- | --- |
| [cloud/](../cloud/) | Cloud-executed application source. |
| [cloud/detection_runner/](../cloud/detection_runner/) | Detection and publication components packaged for Lambda. |
| [handler.py](../cloud/detection_runner/handler.py) | Reads packaged detection.sql, runs Athena, evaluates publication state, and returns an execution summary under the dedicated execution role. |
| [publication.py](../cloud/detection_runner/publication.py) | Shared-ledger claim and finding-publication implementation; ambiguous outcomes must not be silently reset. |

### Terraform infrastructure

[infrastructure/](../infrastructure/) contains the existing Terraform root. Do not rename resource addresses or move files merely to match documentation. SQL-managed tables/views are a separate configuration surface.

| Public file | Responsibility |
| --- | --- |
| [main.tf](../infrastructure/main.tf) | Root Terraform configuration and shared setup; exact provider, backend, and variable details require source inspection. |
| [storage.tf](../infrastructure/storage.tf) | S3 bucket definitions for the audit, query-result, and exercise roles. |
| [storage-security.tf](../infrastructure/storage-security.tf) | Storage-security controls and related policies; the report documents public-access, ownership, encryption, transport, and retention checks. |
| [cloudtrail.tf](../infrastructure/cloudtrail.tf) | Trail, delivery-policy statements, and event-selection configuration; the object-event exercise restored management-only selection. |
| [athena.tf](../infrastructure/athena.tf) | Terraform-managed investigation workgroup and catalog-database configuration. |
| [least-privilege.tf](../infrastructure/least-privilege.tf) | Restricted location-reader test-role configuration. |
| [detection-execution.tf](../infrastructure/detection-execution.tf) | Detection execution-role configuration and scoped permissions. |
| [detection-function.tf](../infrastructure/detection-function.tf) | Cloud detection function configuration and runtime wiring. |
| [detection-state.tf](../infrastructure/detection-state.tf) | Shared publication-state infrastructure. |
| [notifications.tf](../infrastructure/notifications.tf) | Findings topic, SQS inbox, queue policy, subscription, and notification outputs. |
| [detection-email.tf](../infrastructure/detection-email.tf) | Email subscription configuration; the endpoint is supplied through private local input. |
| [detection-failures.tf](../infrastructure/detection-failures.tf) | Failure-capture infrastructure/configuration; file presence is not proof of destination delivery. |
| [detection-schedule.tf](../infrastructure/detection-schedule.tf) | One-time validation schedule, Scheduler execution role, trust, and invocation permission. |

The provider lock file should be version-controlled when present. Dotfiles can be omitted by ordinary directory listings; confirm the lock file separately. Directory names do not establish backend configuration. Generated provider directories, state, inputs, and binary plans are described under locally retained artifacts below, not linked as public files.

### SQL definitions and tests

[queries/](../queries/) holds SQL rather than Python runtime code. [queries/detections/](../queries/detections/) contains the rule and rolling-window query; [queries/tests/](../queries/tests/) contains validation SQL.

| Public file | Responsibility |
| --- | --- |
| [detections/AWSLAB-DET-001.sql](../queries/detections/AWSLAB-DET-001.sql) | Detection view/query definition for the controlled authorization-denial scenario. |
| [detections/AWSLAB-DET-001-windowed.sql](../queries/detections/AWSLAB-DET-001-windowed.sql) | Operational rolling-window detection source; the handler reads the packaged detection.sql. Build-time equivalence must be checked from source. |
| [tests/AWSLAB-DET-001-validation.sql](../queries/tests/AWSLAB-DET-001-validation.sql) | Positive/negative recorded-event validation with source-row presence checks. |
| [tests/AWSLAB-DET-001-unit-tests.sql](../queries/tests/AWSLAB-DET-001-unit-tests.sql) | Nine synthetic flat-field predicate fixtures, not additional real audit events. |

The build process packages the operational SQL as detection.sql beside the handler. A standalone checked-in detection.sql is not required in the runtime directory when the build supplies it; do not add a duplicate solely to match a diagram. Confirm the build script's mapping when auditing source.

### Local execution and verification utilities

[scripts/](../scripts/) contains operator-side utilities. File presence is not permission to execute them; publication, migration, invocation, and acknowledgement may change external state.

| Public file | Responsibility |
| --- | --- |
| [run_detection.py](../scripts/run_detection.py) | Submits the operational Athena detection, waits for results, and preserves execution evidence. |
| [publish_findings.py](../scripts/publish_findings.py) | Local finding publication and duplicate-publication control. |
| [ack_notifications.py](../scripts/ack_notifications.py) | Preserves receipt evidence and acknowledges matching notifications; not a harmless inspection command. |
| [build_detection_package.py](../scripts/build_detection_package.py) | Builds the Lambda deployment package and supplies its SQL input. |
| [migrate_publication_state.py](../scripts/migrate_publication_state.py) | Migrates earlier publication state to the shared ledger; do not rerun casually. |
| [verify_cloud_delivery.py](../scripts/verify_cloud_delivery.py) | Correlates cloud publication and queue delivery and may acknowledge matching messages. |
| [verify_scheduled_run.py](../scripts/verify_scheduled_run.py) | Checks scheduled-run attribution and preserves verifier evidence. |

### Public evidence: index and package files

[evidence/](../evidence/) separates public derivatives from originals. [evidence/README.md](../evidence/README.md) should provide collection-wide provenance and navigation. [evidence/public/](../evidence/public/) organizes eight evidence packages. Review their payloads, provenance, redactions, and checksums before publication; location under this directory is not a safety guarantee.

#### Authorization

[authorization/](../evidence/public/authorization/) groups the following files.

| Public file | Evidentiary purpose |
| --- | --- |
| [README.md](../evidence/public/authorization/README.md) | Scope, source relationships, and redactions for the allowed/denied authorization exercise. |
| [allowed-exit-code.txt](../evidence/public/authorization/allowed-exit-code.txt) | Recorded allowed-request CLI exit code. |
| [allowed-response.json](../evidence/public/authorization/allowed-response.json) | Allowed GetBucketLocation response export. |
| [athena-permission-test-results.csv](../evidence/public/authorization/athena-permission-test-results.csv) | Athena correlation of the controlled allowed and denied requests. |
| [denied-error.txt](../evidence/public/authorization/denied-error.txt) | Recorded denial text; review identity and request metadata before publication. |
| [denied-exit-code.txt](../evidence/public/authorization/denied-exit-code.txt) | Recorded denied-request CLI exit code. |
| [matched-event-location.json](../evidence/public/authorization/matched-event-location.json) | Extracted CloudTrail record for the allowed request. |
| [matched-event-tagging.json](../evidence/public/authorization/matched-event-tagging.json) | Extracted CloudTrail record for the denied request. |
| [checksums.sha256](../evidence/public/authorization/checksums.sha256) | Checksums for published artifacts; recompute and compare after final sanitization. They do not independently authenticate AWS origin. |

#### Detection validation

[detection-validation/](../evidence/public/detection-validation/) groups the following files.

| Public file | Evidentiary purpose |
| --- | --- |
| [README.md](../evidence/public/detection-validation/README.md) | Fixture and execution provenance, test scope, and transformations. |
| [athena-execution.json](../evidence/public/detection-validation/athena-execution.json) | Athena query execution metadata export. |
| [AWSLAB-DET-001-unit-tests.csv](../evidence/public/detection-validation/AWSLAB-DET-001-unit-tests.csv) | Saved synthetic predicate-test results; inspect rows before upgrading historical PASS claims. |
| [AWSLAB-DET-001-validation.csv](../evidence/public/detection-validation/AWSLAB-DET-001-validation.csv) | Recorded-event fixture validation results. |
| [findings.csv](../evidence/public/detection-validation/findings.csv) | Finding rows from the recorded operational evaluation. |
| [run-manifest.json](../evidence/public/detection-validation/run-manifest.json) | Execution provenance and artifact relationships; inspect embedded references. |
| [checksums.sha256](../evidence/public/detection-validation/checksums.sha256) | Checksums for published artifacts; recompute and compare after final sanitization. They do not independently authenticate AWS origin. |

#### Cloud publication

[cloud-publication/](../evidence/public/cloud-publication/) groups the following files.

| Public file | Evidentiary purpose |
| --- | --- |
| [README.md](../evidence/public/cloud-publication/README.md) | Cloud publication, ledger, and receipt correlation method. |
| [delivery-verification-summary.json](../evidence/public/cloud-publication/delivery-verification-summary.json) | Saved delivery-verifier result export. |
| [dynamodb-finding-ledger.json](../evidence/public/cloud-publication/dynamodb-finding-ledger.json) | Selected publication-ledger item, not a complete live database. |
| [finding-payload.json](../evidence/public/cloud-publication/finding-payload.json) | Actual finding notification payload export. |
| [lambda-execution-summary.json](../evidence/public/cloud-publication/lambda-execution-summary.json) | Cloud execution summary and publication counters. |
| [sqs-notification-receipt.json](../evidence/public/cloud-publication/sqs-notification-receipt.json) | Actual notification receipt export; remove actionable receipt handles and unnecessary personal metadata. |
| [checksums.sha256](../evidence/public/cloud-publication/checksums.sha256) | Checksums for published artifacts; recompute and compare after final sanitization. They do not independently authenticate AWS origin. |

#### Scheduled validation

[scheduled-validation/](../evidence/public/scheduled-validation/) groups the following files.

| Public file | Evidentiary purpose |
| --- | --- |
| [README.md](../evidence/public/scheduled-validation/README.md) | One-time validation scope and distinction between rejected and accepted executions. |
| [deployment-diagnostic.json](../evidence/public/scheduled-validation/deployment-diagnostic.json) | Diagnostic export used in the Scheduler investigation. |
| [schedule-target-escaped.json](../evidence/public/scheduled-validation/schedule-target-escaped.json) | Earlier target input showing literal/escaped context placeholders. |
| [schedule-target-remediated.json](../evidence/public/scheduled-validation/schedule-target-remediated.json) | Corrected target input export. |
| [scheduled-execution-summary.json](../evidence/public/scheduled-validation/scheduled-execution-summary.json) | Selected execution summary; identify its execution before using counters. |
| [verifier-receipt.json](../evidence/public/scheduled-validation/verifier-receipt.json) | Saved verifier outcome; inspect the actual result before upgrading reported-success claims. |
| [checksums.sha256](../evidence/public/scheduled-validation/checksums.sha256) | Checksums for published artifacts; recompute and compare after final sanitization. They do not independently authenticate AWS origin. |

#### Log integrity

[log-integrity/](../evidence/public/log-integrity/) groups the following files.

| Public file | Evidentiary purpose |
| --- | --- |
| [README.md](../evidence/public/log-integrity/README.md) | Validation window, provenance, redactions, and the boundaries of cryptographic validation. |
| [context.txt](../evidence/public/log-integrity/context.txt) | CLI context and requested validation window export. |
| [exit-code.txt](../evidence/public/log-integrity/exit-code.txt) | Recorded validator CLI exit code. |
| [validation.txt](../evidence/public/log-integrity/validation.txt) | Actual verbose validation transcript export; distinguish original cryptographic results from redacted bytes. |
| [checksums.sha256](../evidence/public/log-integrity/checksums.sha256) | Checksums for published artifacts; recompute and compare after final sanitization. They do not independently authenticate AWS origin. |

#### IAM review

[iam-review/](../evidence/public/iam-review/) groups the following files.

| Public file | Evidentiary purpose |
| --- | --- |
| [README.md](../evidence/public/iam-review/README.md) | Nine-policy scope, collection method, transformations, and interpretation of validation findings. |
| [access-analyzer-summary.json](../evidence/public/iam-review/access-analyzer-summary.json) | Aggregate summary; compare it with each individual response. |
| [awslab-detection-runner-inline.policy.json](../evidence/public/iam-review/awslab-detection-runner-inline.policy.json) | Policy snapshot for awslab-detection-runner-inline. |
| [awslab-detection-runner-inline.findings.json](../evidence/public/iam-review/awslab-detection-runner-inline.findings.json) | Corresponding policy-validation response; empty findings do not establish exhaustive least privilege. |
| [awslab-detection-runner-trust.policy.json](../evidence/public/iam-review/awslab-detection-runner-trust.policy.json) | Policy snapshot for awslab-detection-runner-trust. |
| [awslab-detection-runner-trust.findings.json](../evidence/public/iam-review/awslab-detection-runner-trust.findings.json) | Corresponding policy-validation response; empty findings do not establish exhaustive least privilege. |
| [awslab-detection-scheduler-inline.policy.json](../evidence/public/iam-review/awslab-detection-scheduler-inline.policy.json) | Policy snapshot for awslab-detection-scheduler-inline. |
| [awslab-detection-scheduler-inline.findings.json](../evidence/public/iam-review/awslab-detection-scheduler-inline.findings.json) | Corresponding policy-validation response; empty findings do not establish exhaustive least privilege. |
| [awslab-detection-scheduler-trust.policy.json](../evidence/public/iam-review/awslab-detection-scheduler-trust.policy.json) | Policy snapshot for awslab-detection-scheduler-trust. |
| [awslab-detection-scheduler-trust.findings.json](../evidence/public/iam-review/awslab-detection-scheduler-trust.findings.json) | Corresponding policy-validation response; empty findings do not establish exhaustive least privilege. |
| [awslab-location-reader-inline.policy.json](../evidence/public/iam-review/awslab-location-reader-inline.policy.json) | Policy snapshot for awslab-location-reader-inline. |
| [awslab-location-reader-inline.findings.json](../evidence/public/iam-review/awslab-location-reader-inline.findings.json) | Corresponding policy-validation response; empty findings do not establish exhaustive least privilege. |
| [awslab-location-reader-trust.policy.json](../evidence/public/iam-review/awslab-location-reader-trust.policy.json) | Policy snapshot for awslab-location-reader-trust. |
| [awslab-location-reader-trust.findings.json](../evidence/public/iam-review/awslab-location-reader-trust.findings.json) | Corresponding policy-validation response; empty findings do not establish exhaustive least privilege. |
| [bucket-0-policy.policy.json](../evidence/public/iam-review/bucket-0-policy.policy.json) | Policy snapshot for bucket-0-policy. |
| [bucket-0-policy.findings.json](../evidence/public/iam-review/bucket-0-policy.findings.json) | Corresponding policy-validation response; empty findings do not establish exhaustive least privilege. |
| [bucket-1-policy.policy.json](../evidence/public/iam-review/bucket-1-policy.policy.json) | Policy snapshot for bucket-1-policy. |
| [bucket-1-policy.findings.json](../evidence/public/iam-review/bucket-1-policy.findings.json) | Corresponding policy-validation response; empty findings do not establish exhaustive least privilege. |
| [bucket-2-policy.policy.json](../evidence/public/iam-review/bucket-2-policy.policy.json) | Policy snapshot for bucket-2-policy. |
| [bucket-2-policy.findings.json](../evidence/public/iam-review/bucket-2-policy.findings.json) | Corresponding policy-validation response; empty findings do not establish exhaustive least privilege. |
| [checksums.sha256](../evidence/public/iam-review/checksums.sha256) | Checksums for published artifacts; recompute and compare after final sanitization. They do not independently authenticate AWS origin. |

#### Human alert

[human-alert/](../evidence/public/human-alert/) groups the following files.

| Public file | Evidentiary purpose |
| --- | --- |
| [README.md](../evidence/public/human-alert/README.md) | Controlled-event, invocation, and email correlation; distinguish payload creation from inbox arrival. |
| [cloudtrail-event.json](../evidence/public/human-alert/cloudtrail-event.json) | Extracted controlled denial event. |
| [email-alert-payload.json](../evidence/public/human-alert/email-alert-payload.json) | Received finding payload export; does not by itself prove an independently measured delivery timestamp. |
| [lambda-execution-summary.json](../evidence/public/human-alert/lambda-execution-summary.json) | Publishing-mode execution result for the controlled event. |
| [request-error.txt](../evidence/public/human-alert/request-error.txt) | Expected denied-request response export. |
| [request-exit-code.txt](../evidence/public/human-alert/request-exit-code.txt) | Expected denied-request exit code. |
| [checksums.sha256](../evidence/public/human-alert/checksums.sha256) | Checksums for published artifacts; recompute and compare after final sanitization. They do not independently authenticate AWS origin. |

#### Object events

[object-events/](../evidence/public/object-events/) groups the following files.

| Public file | Evidentiary purpose |
| --- | --- |
| [README.md](../evidence/public/object-events/README.md) | Temporary collection scope, operation correlation, and cleanup qualification. |
| [matched-events.json](../evidence/public/object-events/matched-events.json) | Extracted PutObject, GetObject, and DeleteObject data records. |
| [operation-summary.json](../evidence/public/object-events/operation-summary.json) | Operation timings, results, and content-hash comparison export. |
| [selectors-after-cleanup.json](../evidence/public/object-events/selectors-after-cleanup.json) | Restored management-only selector response export. |
| [selectors-enabled.json](../evidence/public/object-events/selectors-enabled.json) | Temporary prefix- and operation-scoped selector response export. |
| [terraform-final-plan.txt](../evidence/public/object-events/terraform-final-plan.txt) | Readable final-plan transcript, not a binary plan; final no-change result is recorded in checkpoint history; inspect the transcript for independent confirmation. |
| [checksums.sha256](../evidence/public/object-events/checksums.sha256) | Checksums for published artifacts; recompute and compare after final sanitization. They do not independently authenticate AWS origin. |

### Locally retained originals and generated artifacts

The following locations are intentionally not GitHub links. They are local artifacts, not omitted public proof. Useful derivatives are linked in the packages above. Preserve originals and their relationships; do not move or edit them to tidy the tree.

| Local artifact group | Purpose and publication treatment |
| --- | --- |
| Private audit-delivery and authorization evidence | Original request/identity output, source logs, extracted events, provenance, historical SQL, and Athena CSVs. This includes the original allowed/denied exercise and source-table migration checks. Publish reviewed event/result exports, not arbitrary bulk originals. |
| Private detection and cloud-publication runs | Execution metadata, SQL snapshots, manifests, invocation responses, publication migration items, notification payloads, ledger receipts, acknowledgements, and SQS receipts. Retain distinct attempts and unresolved outcomes. |
| Private scheduled runs and adjustments | Six inventoried run snapshots plus deployment diagnostics, target configuration, verifier results, and timestamp/configuration backups. Keep failed-context and accepted runs distinguishable. |
| Private integrity and IAM review | Full validator context/transcript and the original nine policy/response pairs. Redacted public output is not byte-identical to the source cryptographic evidence. |
| Private human-alert exercise | Request context, initial and later invocation results, Event history snapshot, table scope, original compressed logs, matched source, and query timing. An email payload export is not a complete mailbox-delivery transcript. |
| Private object-event exercise | Baseline/enabled selectors, original object/download and hashes, request responses, failed/accepted scans, compressed source logs, source manifests, source backups, cleanup-recovery read-back, and final-plan transcript/exit code. A second preflight snapshot is preserved separately. |
| Private publication database | Original SQLite publication ledger. It is operational state, not a public evidence dump; use reviewed item/CSV exports where needed. |
| Downloaded query export | One original UUID-named CSV in the local downloads directory. Its query, content, and overlap with curated exports require inspection before publication. |
| Terraform local state and backup | Operational resource state; never publish. Do not delete or rewrite as part of documentation cleanup. |
| Saved Terraform plans | All inventoried binary plan files, including historical component deployments and object-event enable/cleanup attempts. Keep private; a reviewed textual plan is a different artifact. |
| Local variable files | Email endpoint and scheduled-validation input. Keep private; use deliberately sanitized example inputs only if separately prepared. |
| Generated Lambda package and provider files | Build ZIP and any downloaded provider/module working directories. Rebuildable artifacts, not authoritative source. |
| Python caches | Compiled bytecode and cache directories; exclude from publication. |

### Unpopulated directories

Top-level directories named `reports`, `scenarios`, and `tests` may be present without files. No report, scenario, or test coverage is inferred from those names. Empty directories are not useful GitHub destinations, so no broken public links or placeholder files are added. The populated SQL-test directory is linked above. No directory deletion is authorized by this index.
