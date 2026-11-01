locals {
  bucket_purposes = toset([
    "audit",
    "query-results",
    "exercise"
  ])
}

resource "aws_s3_bucket" "lab" {
  for_each = local.bucket_purposes

  bucket_prefix = "awslab-${each.key}-"
  force_destroy = false

  tags = {
    Project   = "AWSLab"
    ManagedBy = "Terraform"
    Purpose   = each.key
  }
}

resource "aws_s3_bucket_public_access_block" "lab" {
  for_each = aws_s3_bucket.lab

  bucket = each.value.id

  block_public_acls       = true
  ignore_public_acls      = true
  block_public_policy     = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "lab" {
  for_each = aws_s3_bucket.lab

  bucket = each.value.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "lab" {
  for_each = aws_s3_bucket.lab

  bucket = each.value.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
