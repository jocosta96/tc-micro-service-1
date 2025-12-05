# Get current AWS caller identity
data "aws_caller_identity" "current" {}

# Get current AWS region
data "aws_region" "current" {}

# Get genral purpose role
#data "aws_iam_role" "lab_role" {name = "LabRole"}

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/scripts/lambda_authorizer.py"
  output_path = "${path.module}/scripts/lambda_authorizer.zip"
}

data "archive_file" "router_zip" {
  type        = "zip"
  source_file = "${path.module}/scripts/router.py"
  output_path = "${path.module}/scripts/router.zip"
}