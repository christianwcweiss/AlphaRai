terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.26"
    }
  }
}

data "aws_region" "current" {}

data "external" "code_zip" {
  program     = ["python", "package.py", "--task", "layer", "--filename", var.context, "--code_path", abspath("${path.module}/../../../code/quant_core")]
  working_dir = "${path.module}/../../bin/"
}

variable "layer_name" {
  type = string
}
variable "layers_bucket_name" {
  type = string
}
variable "context" {
  type        = string
  default     = "quant-core"
  description = "Describe the context in which the layer is to be used. The cached S3 object can be shared across stacks if the same 'context' is used."
}
variable "fetch_custom_credentials" {
  type        = string
  default     = "notset"
  description = "Absolute path to a file that creates custom credentials."
}
variable "docker_build" {
  type        = bool
  default     = true
  description = "If true, this will use Docker to build the dependencies layer. Set to true when having binary dependencies"
}

module "layer" {
  source = "../technical/lambda_layer"

  bucket_name              = var.layers_bucket_name
  context                  = var.context
  layer_name               = var.layer_name
  requirements_file_path   = abspath("${path.module}/../../../code/quant_core/requirements.txt")
  fetch_custom_credentials = var.fetch_custom_credentials
  include_zip              = data.external.code_zip.result.file
  docker_build             = var.docker_build
}

output "lambda_layer_arn" {
  value = module.layer.lambda_layer_arn
}
