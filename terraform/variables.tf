variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "eu-west-2"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "team3-hackathon"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "domain_name" {
  description = "Optional custom domain name"
  type        = string
  default     = ""
}

variable "deployer_role_arns" {
  description = "List of IAM role ARNs that can deploy to the static website bucket"
  type        = list(string)
  default     = []
}
