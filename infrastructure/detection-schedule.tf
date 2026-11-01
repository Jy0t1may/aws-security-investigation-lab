variable "detection_validation_time_utc" {
  description = "One-time scheduled validation timestamp in UTC, without Z."
  type        = string
}

resource "aws_scheduler_schedule_group" "detection" {
  name = "awslab-detection"

  tags = {
    Project   = "AWSLab"
    ManagedBy = "Terraform"
  }
}

resource "aws_iam_role" "detection_scheduler" {
  name = "awslab-detection-scheduler"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "scheduler.amazonaws.com"
      }
      Action = "sts:AssumeRole"
      Condition = {
        StringEquals = {
          "aws:SourceAccount" = data.aws_caller_identity.current.account_id
          "aws:SourceArn"     = aws_scheduler_schedule_group.detection.arn
        }
      }
    }]
  })

  tags = {
    Project   = "AWSLab"
    ManagedBy = "Terraform"
  }
}

resource "aws_iam_role_policy" "detection_scheduler" {
  name = "invoke-detector-and-record-delivery-failures"
  role = aws_iam_role.detection_scheduler.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "InvokeOnlyLabDetector"
        Effect   = "Allow"
        Action   = "lambda:InvokeFunction"
        Resource = aws_lambda_function.detection_runner.arn
      },
      {
        Sid      = "RecordSchedulerDeliveryFailures"
        Effect   = "Allow"
        Action   = "sqs:SendMessage"
        Resource = aws_sqs_queue.detection_failures.arn
      }
    ]
  })
}

resource "aws_scheduler_schedule" "detection_validation" {
  name       = "awslab-detection-validation"
  group_name = aws_scheduler_schedule_group.detection.name

  description                  = "One-time unattended detection validation"
  state                        = "ENABLED"
  schedule_expression          = "at(${var.detection_validation_time_utc})"
  schedule_expression_timezone = "UTC"
  action_after_completion      = "NONE"

  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn      = aws_lambda_function.detection_runner.arn
    role_arn = aws_iam_role.detection_scheduler.arn

    input = replace(replace(jsonencode({
      trigger                = "SCHEDULED_VALIDATION"
      schedule_arn           = "<aws.scheduler.schedule-arn>"
      scheduled_time         = "<aws.scheduler.scheduled-time>"
      scheduler_execution_id = "<aws.scheduler.execution-id>"
    }), "\\u003c", "<"), "\\u003e", ">")

    retry_policy {
      maximum_retry_attempts       = 0
      maximum_event_age_in_seconds = 3600
    }

    dead_letter_config {
      arn = aws_sqs_queue.detection_failures.arn
    }
  }

  depends_on = [
    aws_iam_role_policy.detection_scheduler,
    aws_lambda_function_event_invoke_config.detection_runner
  ]
}

output "detection_validation_time_utc" {
  value = var.detection_validation_time_utc
}
