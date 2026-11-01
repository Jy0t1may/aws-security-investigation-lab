variable "detection_alert_email" {
  description = "Private email endpoint for controlled lab finding alerts."
  type        = string
  sensitive   = true
}

resource "aws_sns_topic_subscription" "detection_email" {
  topic_arn = aws_sns_topic.detection_findings.arn
  protocol  = "email"
  endpoint  = var.detection_alert_email
}