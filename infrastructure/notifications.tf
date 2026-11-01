resource "aws_sns_topic" "detection_findings" {
  name = "awslab-detection-findings"

  tags = {
    Project   = "AWSLab"
    ManagedBy = "Terraform"
    Purpose   = "DetectionNotifications"
  }
}

resource "aws_sqs_queue" "detection_inbox" {
  name                       = "awslab-detection-inbox"
  message_retention_seconds  = 604800
  visibility_timeout_seconds = 60
  receive_wait_time_seconds  = 20
  sqs_managed_sse_enabled    = true

  tags = {
    Project   = "AWSLab"
    ManagedBy = "Terraform"
    Purpose   = "DetectionNotificationEvidence"
  }
}

resource "aws_sqs_queue_policy" "detection_inbox" {
  queue_url = aws_sqs_queue.detection_inbox.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid    = "AllowDeliveryFromDetectionTopic"
      Effect = "Allow"
      Principal = {
        Service = "sns.amazonaws.com"
      }
      Action   = "sqs:SendMessage"
      Resource = aws_sqs_queue.detection_inbox.arn
      Condition = {
        ArnEquals = {
          "aws:SourceArn" = aws_sns_topic.detection_findings.arn
        }
        StringEquals = {
          "aws:SourceAccount" = data.aws_caller_identity.current.account_id
        }
      }
    }]
  })
}

resource "aws_sns_topic_subscription" "detection_inbox" {
  topic_arn            = aws_sns_topic.detection_findings.arn
  protocol             = "sqs"
  endpoint             = aws_sqs_queue.detection_inbox.arn
  raw_message_delivery = false

  depends_on = [aws_sqs_queue_policy.detection_inbox]
}

output "detection_topic_arn" {
  description = "SNS topic used to publish lab detection findings."
  value       = aws_sns_topic.detection_findings.arn
}

output "detection_inbox_url" {
  description = "SQS inbox used to inspect delivered lab notifications."
  value       = aws_sqs_queue.detection_inbox.url
}
