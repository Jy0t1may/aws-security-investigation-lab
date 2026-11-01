resource "aws_lambda_function" "detection_runner" {
  function_name = "awslab-detection-runner"
  description   = "CloudTrail detector with DynamoDB publication ledger"

  role    = aws_iam_role.detection_runner.arn
  runtime = "python3.12"
  handler = "handler.handler"

  filename         = "${path.module}/build/detection-runner.zip"
  source_code_hash = filebase64sha256("${path.module}/build/detection-runner.zip")

  timeout     = 240
  memory_size = 128

  environment {
    variables = {
      DATABASE           = aws_glue_catalog_database.investigation.name
      WORKGROUP          = aws_athena_workgroup.investigation.name
      TABLE_NAME         = aws_dynamodb_table.detection_publications.name
      TOPIC_ARN          = aws_sns_topic.detection_findings.arn
      PUBLISH_ENABLED    = "true"
      MIGRATION_EVENT_ID = "7d900e24-00d4-45ed-979b-f7b80a0d8850"
    }
  }

  tags = {
    Project   = "AWSLab"
    ManagedBy = "Terraform"
    Purpose   = "DetectionExecution"
  }

  depends_on = [
    aws_iam_role_policy.detection_runner,
    aws_cloudwatch_log_group.detection_runner
  ]
}
