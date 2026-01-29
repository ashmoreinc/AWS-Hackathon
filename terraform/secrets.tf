# Store sensitive outputs in a separate file
output "iam_access_key_id" {
  description = "Access Key ID for the IAM user (sensitive)"
  value       = aws_iam_access_key.app_user_key.id
  sensitive   = true
}

output "iam_secret_access_key" {
  description = "Secret Access Key for the IAM user (sensitive)"
  value       = aws_iam_access_key.app_user_key.secret
  sensitive   = true
}
