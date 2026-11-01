# AWSLAB-DET-001 — Denied bucket-tag read by restricted lab role

## Objective and meaning

Identify S3 GetBucketTagging requests returning AccessDenied when made by the awslab-location-reader assumed role. A match is a candidate finding about an action outside that role's intended permissions. Expected lab exercises can legitimately match; the rule alone does not establish malicious activity or compromise.

The rule began as a retrospective Athena view and later became part of a cloud-hosted, rolling-window detection/publication pipeline. A one-time scheduled execution and a separate manually invoked email exercise were validated. Recurring operation and automated containment are not claimed.

## Detection contract

All five conditions must match:

| Field | Required value |
| --- | --- |
| eventSource | s3.amazonaws.com |
| eventName | GetBucketTagging |
| errorCode | AccessDenied |
| userIdentity.type | AssumedRole |
| sessionContext.sessionIssuer.userName | awslab-location-reader |

The predicate does not constrain a specific event ID, session name, account, or bucket. Source selection bounds the operational data to the configured Stockholm audit location. A matching role name in other available source data is not independently disambiguated by an account condition in the predicate.

## Implementation evolution

| Component | Role |
| --- | --- |
| [Initial rule SQL](../../queries/detections/AWSLAB-DET-001.sql) | Retrospective view/query implementation used for the original recorded-event fixtures. |
| [Rolling-window SQL](../../queries/detections/AWSLAB-DET-001-windowed.sql) | Operational query over awslab_investigation.cloudtrail_management, using a rolling 24-hour window and projected log_date bounds. |
| [Lambda handler](../../cloud/detection_runner/handler.py) | Reads detection.sql from its deployment package, executes Athena, processes candidates, and returns an execution summary. |
| [Package builder](../../scripts/build_detection_package.py) | Supplies the deployment package and SQL input. Source-to-package mapping must remain aligned with the operational query. |
| [Publication logic](../../cloud/detection_runner/publication.py) | Uses the DynamoDB publication ledger and SNS finding publication. |
| [Scheduled-run verifier](../../scripts/verify_scheduled_run.py) | Validates one-time scheduled attribution, not merely function execution. |

The original table awslab_investigation.cloudtrail_least_privilege_20261027 covered the October 27 fixtures. It is historical, not the current operational source. The operational query reads awslab_investigation.cloudtrail_management with event-time and partition-date restrictions. Its configured source is eu-north-1.

## Execution and publication

The handler uses a dedicated Lambda execution role. Publication is controlled by PUBLISH_ENABLED and a prior-publication migration safeguard. Candidate keys derive from the rule ID and CloudTrail event ID. Conditional publication claims suppress routine repeats; completed publications are skipped. Unresolved outcomes require investigation rather than resetting the ledger.

SNS supplies the notification path to SQS and the confirmed email subscription. Earlier SQS delivery and the later email exercise are distinct evidence sets. The successful email test was a manual invocation, not the accepted scheduled execution. Exactly-once delivery is not claimed.

The scheduled validation identified and corrected literal Scheduler context placeholders caused by Terraform JSON encoding. A function success status was insufficient until the verifier accepted its trigger context.

## Validation and evidence

| Exercise | Recorded outcome | Public reference |
| --- | --- | --- |
| Positive recorded event: denied GetBucketTagging | One source row, one match, PASS | [Integration CSV](../../evidence/public/detection-validation/AWSLAB-DET-001-validation.csv) |
| Negative recorded event: allowed GetBucketLocation | One source row, zero matches, PASS | [Authorization correlation](../../evidence/public/authorization/README.md) |
| Nine synthetic predicate cases | Historical record: all nine PASS; no new execution is implied | [Result CSV](../../evidence/public/detection-validation/AWSLAB-DET-001-unit-tests.csv) and [exact test matrix](../detection-test-matrix.md) |
| Cloud publication and SQS correlation | Successful later delivery recorded in project history | [Publication package](../../evidence/public/cloud-publication/README.md) |
| One-time scheduling | Corrected verifier execution recorded as successful | [Verifier receipt](../../evidence/public/scheduled-validation/verifier-receipt.json) and [scheduled summary](../../evidence/public/scheduled-validation/scheduled-execution-summary.json) |
| Controlled email exercise, 2026-10-31 | Two candidates, one new publication, one prior finding skipped; target event at 16:11:24Z; received finding email | [Execution](../../evidence/public/human-alert/lambda-execution-summary.json) and [email payload](../../evidence/public/human-alert/email-alert-payload.json) |

The synthetic matrix includes other operation, null error code, other role, other identity type, other service, other error, missing role, and missing identity type. Fixtures are flat SQL rows, not additional CloudTrail events. They do not test ingestion, nested-field extraction, alert delivery, malformed-record handling, or automatic equivalence with the deployed predicate. Reconcile the fixtures when the rule changes.

A stored result archive is evidence of its historical execution, not proof that changed code passes today. Interpret exported verifier and delivery records against their execution identity, timestamps, and correlation references before strengthening a result claim.

## Initial triage

1. Record event ID, UTC time, identity ARN, issuer role, bucket, error, query reference, and source-log path.
2. Determine whether the event belongs to an authorized lab exercise.
3. Compare role session, resource, and time with the request record.
4. Inspect the original event's errorMessage for the recorded denial explanation.
5. Review related sessions and activity if the request is unexpected.

The detection projection does not include every original field. Retrieve the preserved source event for additional identity, source-IP, user-agent, or request-ID context when needed. Do not infer the individual human solely from a role name.

## Disposition and response safeguards

For an expected exercise, record a successful controlled test with no established compromise. For unexpected configuration or application behavior, establish why the operation was attempted and compare it with intended permissions. Unexplained activity requires corroboration and proportionate escalation, not automatic classification as compromise.

- Do not grant the denied permission merely to make the alert disappear.
- Do not disable the role automatically based on one match.
- Preserve original evidence before changes and separate observations from conclusions.
- Do not reset publication state to force a repeat notification.
- Retest relevant behavior only when a substantive implementation or permission change warrants it.

## Scope and integrity boundaries

- Narrow lab-specific authorization rule, not a general IAM-abuse detector.
- Other actions and roles are outside the predicate; null required identity fields do not satisfy it.
- Source delivery and query availability are asynchronous. The rolling lookback is not a delivery guarantee.
- No broad false-positive rate, complete coverage, recurring reliability, or measured inbox-arrival latency is claimed.
- CloudTrail cryptographic validation succeeded for the documented October 27 regional window: five digests and 24 logs. Whether that set includes the original authorization-test source object remains unlinked in the project record.
- That bounded validation does not validate the October 31 email/object-exercise logs or imply continuous integrity monitoring.
- The separate PutObject/GetObject/DeleteObject exercise demonstrated object-level logging only; it did not extend this rule.

See the [full report](../report.md), [integrity evidence](../../evidence/public/log-integrity/README.md), [object-event evidence](../../evidence/public/object-events/README.md), and [repository index](../repository-index.md).

## Evidence handling

Retain originals locally and publish genuine reviewed exports with documented transformations. Preserve useful correlation consistently; non-secret identifiers may be retained deliberately. Never publish credentials, private input, Terraform state, binary plans, or actionable email links. Local checksums do not replace CloudTrail digest validation, and redacted exports are not byte-identical to their originals.
