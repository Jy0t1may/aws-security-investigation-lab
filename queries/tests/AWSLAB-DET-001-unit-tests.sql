-- AWSLAB-DET-001: synthetic predicate tests.
-- These fixtures are not real CloudTrail records.
-- Regenerate after changing the detection SQL.
-- Does not test ingestion, nested-field parsing, or alert delivery.

WITH fixtures (
  test_case,
  eventsource,
  eventname,
  errorcode,
  identity_type,
  role_name,
  expected_matches
) AS (
  VALUES
    ('01_positive', 's3.amazonaws.com', 'GetBucketTagging', 'AccessDenied', 'AssumedRole', 'awslab-location-reader', 1),
    ('02_other_operation', 's3.amazonaws.com', 'GetBucketLocation', 'AccessDenied', 'AssumedRole', 'awslab-location-reader', 0),
    ('03_successful_request', 's3.amazonaws.com', 'GetBucketTagging', CAST(NULL AS VARCHAR), 'AssumedRole', 'awslab-location-reader', 0),
    ('04_other_role', 's3.amazonaws.com', 'GetBucketTagging', 'AccessDenied', 'AssumedRole', 'another-lab-role', 0),
    ('05_other_identity_type', 's3.amazonaws.com', 'GetBucketTagging', 'AccessDenied', 'IAMUser', 'awslab-location-reader', 0),
    ('06_other_service', 'iam.amazonaws.com', 'GetBucketTagging', 'AccessDenied', 'AssumedRole', 'awslab-location-reader', 0),
    ('07_other_error', 's3.amazonaws.com', 'GetBucketTagging', 'InternalError', 'AssumedRole', 'awslab-location-reader', 0),
    ('08_missing_role', 's3.amazonaws.com', 'GetBucketTagging', 'AccessDenied', 'AssumedRole', CAST(NULL AS VARCHAR), 0),
    ('09_missing_identity_type', 's3.amazonaws.com', 'GetBucketTagging', 'AccessDenied', CAST(NULL AS VARCHAR), 'awslab-location-reader', 0)
),
evaluated AS (
  SELECT
    test_case,
    expected_matches,
    CASE WHEN (
      eventsource = 's3.amazonaws.com'
  AND eventname = 'GetBucketTagging'
  AND errorcode = 'AccessDenied'
  AND identity_type = 'AssumedRole'
  AND role_name =
      'awslab-location-reader'
    ) THEN 1 ELSE 0 END AS actual_matches
  FROM fixtures
)
SELECT
  test_case,
  expected_matches,
  actual_matches,
  CASE
    WHEN actual_matches = expected_matches THEN 'PASS'
    ELSE 'FAIL'
  END AS test_result
FROM evaluated
ORDER BY test_case;
