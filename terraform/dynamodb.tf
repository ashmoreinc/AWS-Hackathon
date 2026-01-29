# DynamoDB Table
resource "aws_dynamodb_table" "app_table" {
  name           = "${var.project_name}-${var.environment}-items"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"
  }

  tags = {
    Name        = "${var.project_name}-items-table"
    Environment = var.environment
  }

  # Enable point-in-time recovery
  point_in_time_recovery {
    enabled = true
  }
}
