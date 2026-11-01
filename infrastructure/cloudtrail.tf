locals {
  trail_name = "awslab-management"
  trail_arn  = "arn:aws:cloudtrail:eu-north-1:${data.aws_caller_identity.current.account_id}:trail/${local.trail_name}"

  cloudtrail_bucket_statements = [
    {
      Sid       = "CloudTrailAclCheck"
      Effect    = "Allow"
      Principal = { Service = "cloudtrail.amazonaws.com" }
      Action    = "s3:GetBucketAcl"
      Resource  = aws_s3_bucket.lab["audit"].arn

      Condition = {
        StringEquals = {
          "aws:SourceArn" = local.trail_arn
        }
      }
    },
    {
      Sid       = "CloudTrailLogDelivery"
      Effect    = "Allow"
      Principal = { Service = "cloudtrail.amazonaws.com" }
      Action    = "s3:PutObject"
      Resource  = "${aws_s3_bucket.lab["audit"].arn}/AWSLogs/${data.aws_caller_identity.current.account_id}/*"

      Condition = {
        StringEquals = {
          "aws:SourceArn" = local.trail_arn
          "s3:x-amz-acl"  = "bucket-owner-full-control"
        }
      }
    }
  ]
}

resource "aws_cloudtrail" "management" {
  name                          = local.trail_name
  s3_bucket_name                = aws_s3_bucket.lab["audit"].id
  is_multi_region_trail         = true
  include_global_service_events = true
  enable_logging                = true
  enable_log_file_validation    = true

  event_selector {
    read_write_type           = "All"
    include_management_events = true
  }

  tags = {
    Project   = "AWSLab"
    ManagedBy = "Terraform"
    Purpose   = "ManagementEventInvestigation"
  }

  depends_on = [
    aws_s3_bucket_policy.lab,
    aws_s3_bucket_ownership_controls.lab,
    aws_s3_bucket_server_side_encryption_configuration.lab
  ]
}
