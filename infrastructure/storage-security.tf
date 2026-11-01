resource "aws_s3_bucket_policy" "lab" {
  for_each = aws_s3_bucket.lab

  bucket = each.value.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = concat([
      {
        Sid       = "DenyInsecureTransport"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:*"
        Resource = [
          each.value.arn,
          "${each.value.arn}/*"
        ]
        Condition = {
          Bool = {
            "aws:SecureTransport"       = "false"
            "aws:PrincipalIsAWSService" = "false"
          }
        }
      }
    ], each.key == "audit" ? local.cloudtrail_bucket_statements : [])
  })

  depends_on = [aws_s3_bucket_public_access_block.lab]
}

resource "aws_s3_bucket_lifecycle_configuration" "query_results" {
  bucket = aws_s3_bucket.lab["query-results"].id

  rule {
    id     = "ExpireTemporaryQueryResults"
    status = "Enabled"

    filter {
      prefix = ""
    }

    expiration {
      days = 7
    }

    abort_incomplete_multipart_upload {
      days_after_initiation = 1
    }
  }
}
