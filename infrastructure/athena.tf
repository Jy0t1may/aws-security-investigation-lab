resource "aws_athena_workgroup" "investigation" {
  name          = "awslab-investigation"
  description   = "Controlled SQL investigations of lab audit evidence"
  state         = "ENABLED"
  force_destroy = false

  configuration {
    enforce_workgroup_configuration    = true
    bytes_scanned_cutoff_per_query     = 104857600
    publish_cloudwatch_metrics_enabled = false

    result_configuration {
      output_location       = "s3://${aws_s3_bucket.lab["query-results"].id}/athena/"
      expected_bucket_owner = data.aws_caller_identity.current.account_id

      encryption_configuration {
        encryption_option = "SSE_S3"
      }
    }
  }

  tags = {
    Project   = "AWSLab"
    ManagedBy = "Terraform"
  }
}

resource "aws_glue_catalog_database" "investigation" {
  name        = "awslab_investigation"
  description = "Metadata for AWSLab investigation tables"
}
