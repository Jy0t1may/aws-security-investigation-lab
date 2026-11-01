locals {
  detector_region = "eu-north-1"

  detector_audit_prefix = "AWSLogs/${data.aws_caller_identity.current.account_id}/CloudTrail/${local.detector_region}/"

  detector_glue_root = "arn:aws:glue:${local.detector_region}:${data.aws_caller_identity.current.account_id}"
}

resource "aws_cloudwatch_log_group" "detection_runner" {
  name              = "/aws/lambda/awslab-detection-runner"
  retention_in_days = 7

  tags = {
    Project   = "AWSLab"
    ManagedBy = "Terraform"
    Purpose   = "DetectionExecutionLogs"
  }
}

resource "aws_iam_role" "detection_runner" {
  name        = "awslab-detection-runner"
  description = "Execution role for the cloud-hosted lab detector"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })

  tags = {
    Project   = "AWSLab"
    ManagedBy = "Terraform"
    Purpose   = "DetectionExecution"
  }
}

resource "aws_iam_role_policy" "detection_runner" {
  name = "scoped-detection-execution"
  role = aws_iam_role.detection_runner.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "ExecuteQueriesInLabWorkgroup"
        Effect = "Allow"
        Action = [
          "athena:StartQueryExecution",
          "athena:GetQueryExecution",
          "athena:GetQueryResults",
          "athena:StopQueryExecution",
          "athena:GetWorkGroup"
        ]
        Resource = aws_athena_workgroup.investigation.arn
      },
      {
        Sid    = "ReadCloudTrailTableMetadata"
        Effect = "Allow"
        Action = [
          "glue:GetDatabase",
          "glue:GetTable",
          "glue:GetPartitions",
          "glue:BatchGetPartition"
        ]
        Resource = [
          "${local.detector_glue_root}:catalog",
          "${local.detector_glue_root}:database/${aws_glue_catalog_database.investigation.name}",
          "${local.detector_glue_root}:table/${aws_glue_catalog_database.investigation.name}/cloudtrail_management"
        ]
      },
      {
        Sid    = "LocateLabBuckets"
        Effect = "Allow"
        Action = "s3:GetBucketLocation"
        Resource = [
          aws_s3_bucket.lab["audit"].arn,
          aws_s3_bucket.lab["query-results"].arn
        ]
      },
      {
        Sid      = "ListStockholmAuditPrefix"
        Effect   = "Allow"
        Action   = "s3:ListBucket"
        Resource = aws_s3_bucket.lab["audit"].arn
        Condition = {
          StringLike = {
            "s3:prefix" = "${local.detector_audit_prefix}*"
          }
        }
      },
      {
        Sid      = "ReadStockholmAuditObjects"
        Effect   = "Allow"
        Action   = "s3:GetObject"
        Resource = "${aws_s3_bucket.lab["audit"].arn}/${local.detector_audit_prefix}*"
      },
      {
        Sid      = "ListQueryResultPrefix"
        Effect   = "Allow"
        Action   = "s3:ListBucket"
        Resource = aws_s3_bucket.lab["query-results"].arn
        Condition = {
          StringLike = {
            "s3:prefix" = "athena/*"
          }
        }
      },
      {
        Sid    = "ReadAndWriteQueryResults"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:AbortMultipartUpload",
          "s3:ListMultipartUploadParts"
        ]
        Resource = "${aws_s3_bucket.lab["query-results"].arn}/athena/*"
      },
      {
        Sid    = "MaintainPublicationLedger"
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem"
        ]
        Resource = aws_dynamodb_table.detection_publications.arn
      },
      {
        Sid      = "PublishDetectionFindings"
        Effect   = "Allow"
        Action   = "sns:Publish"
        Resource = aws_sns_topic.detection_findings.arn
      },
      {
        Sid    = "WriteDetectorLogs"
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "${aws_cloudwatch_log_group.detection_runner.arn}:*"
      }
    ]
  })
}

output "detection_runner_role_arn" {
  description = "Execution role for the cloud detector."
  value       = aws_iam_role.detection_runner.arn
}
