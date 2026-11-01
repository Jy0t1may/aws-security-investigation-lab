resource "aws_sqs_queue" "detection_failures" {
  name                      = "awslab-detection-failures"
  message_retention_seconds = 604800
  receive_wait_time_seconds = 20
  sqs_managed_sse_enabled   = true

  tags = {
    Project   = "AWSLab"
    ManagedBy = "Terraform"
    Purpose   = "DetectionExecutionFailures"
  }
}

resource "aws_iam_role_policy" "detection_failure_delivery" {
  name = "deliver-asynchronous-failure-records"
  role = aws_iam_role.detection_runner.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid      = "SendFailureRecordsToDedicatedQueue"
      Effect   = "Allow"
      Action   = "sqs:SendMessage"
      Resource = aws_sqs_queue.detection_failures.arn
    }]
  })
}

resource "aws_lambda_function_event_invoke_config" "detection_runner" {
  function_name = aws_lambda_function.detection_runner.function_name

  maximum_retry_attempts       = 0
  maximum_event_age_in_seconds = 3600

  destination_config {
    on_failure {
      destination = aws_sqs_queue.detection_failures.arn
    }
  }

  depends_on = [
    aws_iam_role_policy.detection_failure_delivery
  ]
}

output "detection_failures_queue_url" {
  description = "Inbox for failed asynchronous detector invocation records."
  value       = aws_sqs_queue.detection_failures.url
}
