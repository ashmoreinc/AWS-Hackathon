# IAM User for application access
resource "aws_iam_user" "app_user" {
  name = "${var.project_name}-${var.environment}-app-user"

  tags = {
    Name        = "${var.project_name}-app-user"
    Environment = var.environment
  }
}

# IAM Policy for S3 and DynamoDB access
resource "aws_iam_policy" "app_policy" {
  name        = "${var.project_name}-${var.environment}-app-policy"
  description = "Policy for application to access S3 and DynamoDB"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.app_bucket.arn,
          "${aws_s3_bucket.app_bucket.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:DeleteItem",
          "dynamodb:Scan",
          "dynamodb:Query",
          "dynamodb:UpdateItem"
        ]
        Resource = aws_dynamodb_table.app_table.arn
      }
    ]
  })
}

# Attach policy to user
resource "aws_iam_user_policy_attachment" "app_user_policy" {
  user       = aws_iam_user.app_user.name
  policy_arn = aws_iam_policy.app_policy.arn
}

# Create access key for the user (use with caution in production)
resource "aws_iam_access_key" "app_user_key" {
  user = aws_iam_user.app_user.name
}
