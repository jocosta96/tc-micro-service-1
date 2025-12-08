"""
API Gateway Router Lambda Function

This Lambda function acts as a router for incoming API Gateway requests.
It forwards requests to appropriate Lambda functions based on the request path and method.

The router provides a centralized control point for managing request forwarding between
the API Gateway and various microservice Lambda functions.
"""

import json
import os
import logging
from typing import Dict, Any

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Mapping of routes to their handler configurations
# Format: "path_pattern": {"allowed_methods": ["GET", "POST", ...], "handler": "lambda_function_name"}
ROUTE_MAPPING = {
    # Example routes - add your Lambda functions here
    # "orders": {
    #     "allowed_methods": ["GET", "POST", "PUT", "DELETE"],
    #     "handler": "orders-service"
    # },
    # "users": {
    #     "allowed_methods": ["GET", "POST"],
    #     "handler": "users-service"
    # }
}


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main handler for routing API Gateway requests.
    
    Args:
        event: API Gateway proxy event
        context: Lambda context object
    
    Returns:
        API Gateway proxy response
    """
    try:
        logger.info(f"Received request: {json.dumps(event)}")
        
        # Extract request information
        http_method = event.get("httpMethod", "")
        path = event.get("path", "")
        resource_path = event.get("resource", "")
        
        logger.info(f"Method: {http_method}, Path: {path}, Resource: {resource_path}")
        
        # Extract the service name from the path
        # Expected format: /{service_name}/...
        path_parts = path.strip("/").split("/")
        service_name = path_parts[0] if path_parts else None
        
        if not service_name:
            return error_response(400, "Invalid path format")
        
        # Check if the route exists in our mapping
        route_config = ROUTE_MAPPING.get(service_name)
        
        if not route_config:
            logger.warning(f"Route not found: {service_name}")
            return error_response(404, f"Service '{service_name}' not found")
        
        # Check if the HTTP method is allowed for this route
        if http_method not in route_config.get("allowed_methods", []):
            logger.warning(f"Method not allowed: {http_method} for service {service_name}")
            return error_response(
                405,
                f"Method {http_method} not allowed for service '{service_name}'"
            )
        
        # Log the routing decision
        handler_name = route_config.get("handler")
        logger.info(f"Routing request to handler: {handler_name}")
        
        # Return a successful routing response
        # In a production setup, this could actually invoke the target Lambda function
        return success_response(
            {
                "message": f"Request routed to {handler_name}",
                "service": service_name,
                "method": http_method,
                "path": path,
                "environment": os.environ.get("ENVIRONMENT", "dev")
            }
        )
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return error_response(500, "Internal server error")


def success_response(body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format a successful API Gateway response.
    
    Args:
        body: Response body dictionary
    
    Returns:
        API Gateway proxy response format
    """
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(body)
    }


def error_response(status_code: int, message: str) -> Dict[str, Any]:
    """
    Format an error API Gateway response.
    
    Args:
        status_code: HTTP status code
        message: Error message
    
    Returns:
        API Gateway proxy response format
    """
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({"error": message})
    }
