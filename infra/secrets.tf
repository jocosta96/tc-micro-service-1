resource "aws_ssm_parameter" "valid_token_ssm" {
  name        = "/ordering-system/apigateway/token"
  description = "Valid token for integration"
  type        = "SecureString"
  value       = random_password.valid_token.result
}