-- AWSLAB-DET-001: operational, rolling-window query.
-- Source: date-projected CloudTrail table, eu-north-1.
-- Lookback: 24 hours, evaluated in UTC.
-- Results are candidates for notification, not evidence of compromise.
-- Keep detection conditions aligned with AWSLAB-DET-001.sql.

SELECT DISTINCT
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
FROM awslab_investigation.cloudtrail_management
WHERE log_date BETWEEN
      date_format(
        (current_timestamp AT TIME ZONE 'UTC') - INTERVAL '24' HOUR,
        '%Y/%m/%d'
      )
      AND date_format(
        current_timestamp AT TIME ZONE 'UTC',
        '%Y/%m/%d'
      )
  AND from_iso8601_timestamp(eventtime)
      >= current_timestamp - INTERVAL '24' HOUR
  AND from_iso8601_timestamp(eventtime) < current_timestamp
  AND eventsource = 's3.amazonaws.com'
  AND eventname = 'GetBucketTagging'
  AND errorcode = 'AccessDenied'
  AND useridentity.type = 'AssumedRole'
  AND useridentity.sessioncontext.sessionissuer.username =
      'awslab-location-reader'
ORDER BY eventtime;
