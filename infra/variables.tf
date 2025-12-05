variable "ENVIRONMENT" {
    description = "The environment to deploy the infrastructure"
    type = string
    default = "dev"
    validation {
        condition = contains(["dev", "test", "prod"], var.ENVIRONMENT)
        error_message = "Environment must be one of: dev, test, prod."
    }
}