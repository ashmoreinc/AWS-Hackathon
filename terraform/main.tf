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

resource "aws_dynamodb_table" "offers" {
  name           = "Offers"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "PK"
  range_key      = "SK"
  stream_enabled = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

  attribute {
    name = "PK"
    type = "S"
  }
  attribute {
    name = "SK"
    type = "S"
  }
  attribute {
    name = "category"
    type = "S"
  }
  attribute {
    name = "priority"
    type = "N"
  }

  global_secondary_index {
    name            = "category-priority-index"
    hash_key        = "category"
    range_key       = "priority"
    projection_type = "ALL"
  }

  ttl {
    enabled        = true
    attribute_name = "expiration_timestamp"
  }
}

resource "aws_dynamodb_table" "user_activity" {
  name           = "UserActivity"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "PK"
  range_key      = "SK"

  attribute {
    name = "PK"
    type = "S"
  }
  attribute {
    name = "SK"
    type = "S"
  }
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
        Action = ["dynamodb:*"]
        Resource = [
          aws_dynamodb_table.offers.arn,
          aws_dynamodb_table.user_activity.arn,
          "${aws_dynamodb_table.offers.arn}/*",
          "${aws_dynamodb_table.user_activity.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = ["kinesis:*"]
        Resource = aws_kinesis_stream.offer_engagement.arn
      },
      {
        Effect = "Allow"
        Action = ["logs:*"]
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
  memory_size     = 512
  source_code_hash = filebase64sha256("../lambda/deployment.zip")

  environment {
    variables = {
      OFFERS_TABLE = aws_dynamodb_table.offers.name
      USER_ACTIVITY_TABLE = aws_dynamodb_table.user_activity.name
      KINESIS_STREAM = aws_kinesis_stream.offer_engagement.name
    }
  }
}

resource "aws_lambda_function" "track_event" {
  filename         = "../lambda/deployment.zip"
  function_name    = "offer-track-event"
  role            = aws_iam_role.lambda_role.arn
  handler         = "track_event.lambda_handler"
  runtime         = "python3.11"
  timeout         = 10
  memory_size     = 256
  source_code_hash = filebase64sha256("../lambda/deployment.zip")

  environment {
    variables = {
      KINESIS_STREAM = aws_kinesis_stream.offer_engagement.name
      USER_ACTIVITY_TABLE = aws_dynamodb_table.user_activity.name
    }
  }
}

resource "aws_lambda_function" "inventory_monitor" {
  filename         = "../lambda/deployment.zip"
  function_name    = "offer-inventory-monitor"
  role            = aws_iam_role.lambda_role.arn
  handler         = "inventory_monitor.lambda_handler"
  runtime         = "python3.11"
  timeout         = 30
  memory_size     = 256
  source_code_hash = filebase64sha256("../lambda/deployment.zip")

  environment {
    variables = {
      OFFERS_TABLE = aws_dynamodb_table.offers.name
    }
  }
}

resource "aws_lambda_event_source_mapping" "dynamodb_trigger" {
  event_source_arn  = aws_dynamodb_table.offers.stream_arn
  function_name     = aws_lambda_function.inventory_monitor.arn
  starting_position = "LATEST"
  batch_size        = 10
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

resource "aws_apigatewayv2_integration" "track_event" {
  api_id           = aws_apigatewayv2_api.offer_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.track_event.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "get_offers" {
  api_id    = aws_apigatewayv2_api.offer_api.id
  route_key = "POST /offers/recommend"
  target    = "integrations/${aws_apigatewayv2_integration.get_offers.id}"
}

resource "aws_apigatewayv2_route" "track_event" {
  api_id    = aws_apigatewayv2_api.offer_api.id
  route_key = "POST /events/track"
  target    = "integrations/${aws_apigatewayv2_integration.track_event.id}"
}

resource "aws_lambda_permission" "api_gateway_get_offers" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.get_offers.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.offer_api.execution_arn}/*/*"
}

resource "aws_lambda_permission" "api_gateway_track_event" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.track_event.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.offer_api.execution_arn}/*/*"
}

output "api_endpoint" {
  value = aws_apigatewayv2_stage.prod.invoke_url
}
