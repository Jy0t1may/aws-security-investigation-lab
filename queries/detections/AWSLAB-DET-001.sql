-- AWSLAB-DET-001
-- Detect denied bucket-tag reads by the lab's location-reader role.
-- Scope: existing eu-north-1 CloudTrail table for 2026-10-27.
-- A match indicates an authorization failure, not necessarily malicious activity.

CREATE OR REPLACE VIEW
  awslab_investigation.det_001_denied_bucket_tag_read AS
SELECT
  eventid,
  eventtime,
  eventsource,
  eventname,
  awsregion,
  useridentity.arn AS identity_arn,
  useridentity.sessioncontext.sessionissuer.username AS role_name,
  json_extract_scalar(requestparameters, '$.bucketName') AS bucket_name,
  errorcode,
  "$path" AS source_log
FROM awslab_investigation.cloudtrail_least_privilege_20261027
WHERE eventsource = 's3.amazonaws.com'
  AND eventname = 'GetBucketTagging'
  AND errorcode = 'AccessDenied'
  AND useridentity.type = 'AssumedRole'
  AND useridentity.sessioncontext.sessionissuer.username =
      'awslab-location-reader';
