# Resolve the existing operator role without guessing its IAM path.
data "aws_iam_role" "lab_operator" {
  name = "AccountFullAccessRole"
}

resource "aws_iam_role" "location_reader" {
  name                 = "awslab-location-reader"
  description          = "Controlled exercise: read only the exercise bucket location"
  max_session_duration = 3600

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid    = "TrustLabOperatorOnly"
      Effect = "Allow"
      Principal = {
        AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
      }
      Action = "sts:AssumeRole"
      Condition = {
        ArnEquals = {
          "aws:PrincipalArn" = data.aws_iam_role.lab_operator.arn
        }
      }
    }]
  })

  tags = {
    Project   = "AWSLab"
    ManagedBy = "Terraform"
    Purpose   = "LeastPrivilegeExercise"
  }
}

resource "aws_iam_role_policy" "location_reader" {
  name = "exercise-bucket-location-only"
  role = aws_iam_role.location_reader.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid      = "ReadExerciseBucketLocationOnly"
      Effect   = "Allow"
      Action   = "s3:GetBucketLocation"
      Resource = aws_s3_bucket.lab["exercise"].arn
    }]
  })
}
