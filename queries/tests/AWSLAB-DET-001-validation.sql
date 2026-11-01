WITH fixtures (eventid, test_case, expected_matches) AS (
  VALUES
    (
      '7d900e24-00d4-45ed-979b-f7b80a0d8850',
      'positive: denied GetBucketTagging',
      1
    ),
    (
      'e8a51efe-10f7-497e-9202-271653c1d350',
      'negative: allowed GetBucketLocation',
      0
    )
),
source_counts AS (
  SELECT eventid, count(*) AS source_rows
  FROM awslab_investigation.cloudtrail_least_privilege_20261027
  WHERE eventid IN (SELECT eventid FROM fixtures)
  GROUP BY eventid
),
detection_counts AS (
  SELECT eventid, count(*) AS detection_rows
  FROM awslab_investigation.det_001_denied_bucket_tag_read
  WHERE eventid IN (SELECT eventid FROM fixtures)
  GROUP BY eventid
)
SELECT
  f.test_case,
  coalesce(s.source_rows, 0) AS source_rows,
  f.expected_matches,
  coalesce(d.detection_rows, 0) AS actual_matches,
  CASE
    WHEN coalesce(s.source_rows, 0) = 1
      AND coalesce(d.detection_rows, 0) = f.expected_matches
    THEN 'PASS'
    ELSE 'FAIL'
  END AS test_result
FROM fixtures f
LEFT JOIN source_counts s ON f.eventid = s.eventid
LEFT JOIN detection_counts d ON f.eventid = d.eventid
ORDER BY f.expected_matches DESC;
