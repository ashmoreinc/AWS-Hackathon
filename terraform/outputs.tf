output "s3_bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.app_bucket.id
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.app_bucket.arn
}

output "dynamodb_table_name" {
  description = "Name of the DynamoDB table"
  value       = aws_dynamodb_table.app_table.name
}

output "dynamodb_table_arn" {
  description = "ARN of the DynamoDB table"
  value       = aws_dynamodb_table.app_table.arn
}

output "iam_user_name" {
  description = "Name of the IAM user for application access"
  value       = aws_iam_user.app_user.name
}

output "cloudfront_distribution_id" {
  description = "ID of the CloudFront distribution"
  value       = aws_cloudfront_distribution.app_distribution.id
}

output "cloudfront_domain_name" {
  description = "Domain name of the CloudFront distribution"
  value       = aws_cloudfront_distribution.app_distribution.domain_name
}

output "static_website_bucket_name" {
  description = "Name of the S3 bucket for static website hosting"
  value       = aws_s3_bucket.static_website.id
}
