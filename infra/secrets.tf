locals {
  secrets_tags =  {
      origin = "tc-micro-service-1/infra/secrets.tf"
  }

}

resource "aws_kms_key" "ssm_key" {
  description             = "KMS key for SSM Parameter Store encryption"
  deletion_window_in_days = 10
  enable_key_rotation     = true

  tags = merge(
    local.default_tags,
    local.secrets_tags
  )
}

resource "aws_kms_alias" "ssm_key_alias" {
  name          = "alias/ordering-system-ssm"
  target_key_id = aws_kms_key.ssm_key.key_id
}

resource "aws_ssm_parameter" "valid_token_ssm" {
  name        = "/ordering-system/apigateway/token"
  description = "Valid token for integration"
  type        = "SecureString"
  value       = random_password.valid_token.result
  key_id      = aws_kms_key.ssm_key.id

  tags = merge(
    local.default_tags,
    local.secrets_tags
  )
}