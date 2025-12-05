
resource "aws_iam_role" "lambda_exec" {
  name = "lambda_user"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}


locals {
    lambda_role_arn = aws_iam_role.lambda_exec.arn

    iam_tags = {"origin" = "tc-micro-service-1/infra/iam.tf"}
}