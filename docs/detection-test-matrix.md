# AWSLAB-DET-001 — Synthetic Predicate Test Matrix

## Source and scope

Source: [AWSLAB-DET-001-unit-tests.sql](../queries/tests/AWSLAB-DET-001-unit-tests.sql)

These nine fixtures are synthetic SQL rows, not real CloudTrail records.
They supplement the two recorded-event integration fixtures.

The tests evaluate a flat-field detection predicate. They do not test
CloudTrail ingestion, nested-field parsing, or alert delivery.

## Positive baseline

Unless a row below states otherwise, every fixture uses:

| Field | Value |
| --- | --- |
| eventsource | s3.amazonaws.com |
| eventname | GetBucketTagging |
| errorcode | AccessDenied |
| identity_type | AssumedRole |
| role_name | awslab-location-reader |

The intended match requires all five conditions.

## Test cases

Each negative fixture changes exactly one field from the positive baseline.
SQL NULL values are represented explicitly in the source.

| Case | Input or change from baseline | Expected matches | Historically reported actual matches | Historical result | Purpose |
| --- | --- | ---: | ---: | --- | --- |
| 01_positive | All baseline values | 1 | 1 | PASS | Recognize the intended combination. |
| 02_other_operation | eventname = GetBucketLocation | 0 | 0 | PASS | Exclude a different operation, even with AccessDenied. |
| 03_successful_request | errorcode = CAST(NULL AS VARCHAR) | 0 | 0 | PASS | Exclude a request with no error code. |
| 04_other_role | role_name = another-lab-role | 0 | 0 | PASS | Exclude another role. |
| 05_other_identity_type | identity_type = IAMUser | 0 | 0 | PASS | Exclude a different identity type. |
| 06_other_service | eventsource = iam.amazonaws.com | 0 | 0 | PASS | Exclude a different event source. |
| 07_other_error | errorcode = InternalError | 0 | 0 | PASS | Exclude an error other than AccessDenied. |
| 08_missing_role | role_name = CAST(NULL AS VARCHAR) | 0 | 0 | PASS | Exclude a missing role value. |
| 09_missing_identity_type | identity_type = CAST(NULL AS VARCHAR) | 0 | 0 | PASS | Exclude a missing identity-type value. |

## Result provenance

The project record reports that all nine synthetic cases passed on
2026-10-27. This document enumerates the supplied fixtures and records
those historical outcomes; it does not represent a new test execution.

The stored synthetic-test result CSV was reviewed on November 1, 2026. All nine cases recorded PASS, with expected and actual match counts consistent for every case. This reviews the historical execution archive; it does not represent a fresh run against current SQL or deployed code.

## Interpretation and limitations

- Case 02 retains AccessDenied while changing the operation. It is not
  the successful GetBucketLocation real-event integration fixture.
- Cases 08 and 09 use SQL NULL, not empty strings or malformed JSON.
- The test contains its own copy of the predicate. A PASS does not by
  itself prove that the deployed detection SQL remains identical.
- Regenerate or reconcile these tests after changing the detection SQL.
- These cases do not establish ingestion, nested-field extraction,
  publication, scheduling, or end-to-end pipeline correctness.