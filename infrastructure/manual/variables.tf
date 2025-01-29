variable "environment" {
    type        = string
    description = "The environment in which the Lambda function will run."

    validation {
        condition     = can(regex("^(DEV|PROD)$", upper(var.environment)))
        error_message = "Environment must be one of DEV or PROD."
    }
}
