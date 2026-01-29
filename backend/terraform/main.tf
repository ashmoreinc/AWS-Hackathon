terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region  = var.aws_region
  profile = "AdministratorAccess-851311377237"
}





resource "aws_kinesis_stream" "offer_engagement" {
  name             = "offer-engagement-stream"
  shard_count      = 1
  retention_period = 24
}

resource "aws_iam_role" "lambda_role" {
  name = "offer-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy" "lambda_policy" {
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_lambda_function" "get_offers" {
  filename         = "../lambda/deployment.zip"
  function_name    = "offer-get-offers"
  role            = aws_iam_role.lambda_role.arn
  handler         = "get_offers.lambda_handler"
  runtime         = "python3.11"
  timeout         = 30
  memory_size     = 256
  source_code_hash = filebase64sha256("../lambda/deployment.zip")


}




resource "aws_apigatewayv2_api" "offer_api" {
  name          = "offer-management-api"
  protocol_type = "HTTP"
  
  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["GET", "POST"]
    allow_headers = ["*"]
  }
}

resource "aws_apigatewayv2_stage" "prod" {
  api_id      = aws_apigatewayv2_api.offer_api.id
  name        = "prod"
  auto_deploy = true
}

resource "aws_apigatewayv2_integration" "get_offers" {
  api_id           = aws_apigatewayv2_api.offer_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.get_offers.invoke_arn
  payload_format_version = "2.0"
}



resource "aws_apigatewayv2_route" "get_offers" {
  api_id    = aws_apigatewayv2_api.offer_api.id
  route_key = "POST /offers/recommend"
  target    = "integrations/${aws_apigatewayv2_integration.get_offers.id}"
}



resource "aws_lambda_permission" "api_gateway_get_offers" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.get_offers.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.offer_api.execution_arn}/*/*"
}



output "api_endpoint" {
  value = aws_apigatewayv2_stage.prod.invoke_url
}
