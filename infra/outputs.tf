output "api_gateway_url" {
  description = "The URL of the API Gateway"
  value       = "${aws_api_gateway_stage.api_stage.invoke_url}"
}

output "api_gateway_id" {
  description = "The ID of the API Gateway"
  value       = aws_api_gateway_rest_api.api.id
}

output "api_gateway_root_resource_id" {
  description = "The root resource ID of the API Gateway"
  value       = aws_api_gateway_rest_api.api.root_resource_id
}

output "authorizer_id" {
  description = "The ID of the Lambda authorizer"
  value       = aws_api_gateway_authorizer.lambda_auth.id
}

output "authorizer_function_name" {
  description = "The name of the Lambda authorizer function"
  value       = aws_lambda_function.authorizer.function_name
}

output "router_function_name" {
  description = "The name of the API router Lambda function"
  value       = aws_lambda_function.router.function_name
}