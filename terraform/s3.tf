# S3 Bucket for application data
resource "aws_s3_bucket" "app_bucket" {
  bucket = "${var.project_name}-${var.environment}-app-bucket"

  tags = {
    Name        = "${var.project_name}-app-bucket"
    Environment = var.environment
  }
}

# Enable versioning for the app bucket
resource "aws_s3_bucket_versioning" "app_bucket_versioning" {
  bucket = aws_s3_bucket.app_bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}

# S3 Bucket for static website hosting
resource "aws_s3_bucket" "static_website" {
  bucket = "${var.project_name}-${var.environment}-static-website"

  tags = {
    Name        = "${var.project_name}-static-website"
    Environment = var.environment
  }
}

# Website configuration
resource "aws_s3_bucket_website_configuration" "static_website" {
  bucket = aws_s3_bucket.static_website.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "404.html"
  }
}

# Block public access for app bucket (will use CloudFront)
resource "aws_s3_bucket_public_access_block" "app_bucket" {
  bucket = aws_s3_bucket.app_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Block public access for static website bucket (CloudFront OAI only)
resource "aws_s3_bucket_public_access_block" "static_website" {
  bucket = aws_s3_bucket.static_website.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
