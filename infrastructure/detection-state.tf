resource "aws_dynamodb_table" "detection_publications" {
  name         = "awslab-detection-publications"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "finding_id"

  attribute {
    name = "finding_id"
    type = "S"
  }

  server_side_encryption {
    enabled = true
  }

  tags = {
    Project   = "AWSLab"
    ManagedBy = "Terraform"
    Purpose   = "DetectionPublicationState"
  }
}

output "detection_publications_table_name" {
  description = "Shared publication ledger for cloud detection execution."
  value       = aws_dynamodb_table.detection_publications.name
}
