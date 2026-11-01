terraform {
  required_version = ">= 1.6.0, < 2.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region  = "eu-north-1"
  profile = "investigation-lab"
}

# Read-only identity check; no managed resources.
data "aws_caller_identity" "current" {}

output "expected_role_in_use" {
  description = "Whether the caller uses the expected account-access role."
  value       = can(regex(":assumed-role/AccountFullAccessRole/", data.aws_caller_identity.current.arn))
}
