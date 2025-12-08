resource "aws_lambda_function" "authorizer" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "api-authorizer"
  role             = local.lambda_role_arn
  handler          = "lambda_authorizer.lambda_handler"
  runtime          = "python3.9"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  tracing_config {
    mode = "Active" # Enable X-Ray tracing
  }

  environment {
    variables = {
      TOKEN = aws_ssm_parameter.valid_token_ssm.value
    }
  }
}

resource "aws_lambda_function" "router" {
  filename         = data.archive_file.router_zip.output_path
  function_name    = "api-router"
  role             = local.lambda_role_arn
  handler          = "router.lambda_handler"
  runtime          = "python3.9"
  source_code_hash = data.archive_file.router_zip.output_base64sha256

  tracing_config {
    mode = "Active" # Enable X-Ray tracing
  }

  environment {
    variables = {
      ENVIRONMENT = var.ENVIRONMENT
    }
  }
}
