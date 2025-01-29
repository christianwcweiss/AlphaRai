variable "environment" {
  type = string
}
variable "name" {
  type = string
}
variable "source_path" {
  default = ""
  type    = string
}
variable "source_zip" {
  default = ""
  type    = string
}
variable "source_hash" {
  default = ""
  type    = string
}
variable "source_is_file" {
  default = false
  type    = bool
}
variable "handler" {
  type = string
}
variable "timeout" {
  default = 10
  type    = number
}
variable "memory" {
  default = 128
  type    = number
}
variable "reserved_concurrency" {
  default = -1
  type    = number
}
variable "environment_vars" {
  default = {}
  type    = map(string)
}
variable "log_retention" {
  default = 30
  type    = number
}
variable "layers" {
  default = []
  type    = list(string)
}
variable "description" {
  default = ""
  type    = string
}
variable "needs_log_subscription" {
  default = false
  type    = bool
}
variable "alerts_topic_arn" {
  type = string
}
variable "logs_subscription_arn" {
  type    = string
  default = ""
}
variable "role_name" {
  default = ""
  # this is only here for legacy purposes, should be empty for all new lambdas
  type = string
}

variable "alert_on_invocation_errors" {
  default = true
  type    = bool
}
variable "security_group_ids" {
  default = []
  type    = list(string)
}
variable "vpc_name" {
  default     = ""
  type        = string
  description = "Used to determine Security Group and/or subnet IDs for VPC config in case either is not specified."
}
variable "xray_enabled" {
  default = false
  type    = bool
}

variable "publish_lambda" {
  default = false
  type    = bool
}

variable "use_cwd_for_source_dir" {
  default = true
  type    = bool
}

variable "subnet_ids" {
  type    = set(string)
  default = []
}


data "aws_region" "current" {}

data "aws_security_group" "lambda-security-group" {
  count = local.look_up_security_group_ids ? 1 : 0
  tags = {
    vpc-name = var.vpc_name
  }
}


locals {
  vpc_config                 = var.vpc_name != "" || length(var.security_group_ids) > 0 || length(var.subnet_ids) > 0
  look_up_security_group_ids = var.vpc_name != "" && length(var.security_group_ids) == 0
  look_up_subnets            = var.vpc_name != "" && length(var.subnet_ids) == 0

  security_group_ids = local.look_up_security_group_ids ? [data.aws_security_group.lambda-security-group[0].id] : var.security_group_ids
  subnets            = local.look_up_subnets ? toset(data.aws_subnets.private_vpc_subnet_ids[0].ids) : var.subnet_ids

  role_name            = var.role_name == "" ? "${var.name}-${data.aws_region.current.name}" : var.role_name
  should_zip           = var.source_zip == "" && var.source_hash == ""
  path_to_source       = var.use_cwd_for_source_dir ? "${path.cwd}/${var.source_path}" : var.source_path
  namespace_aws_lambda = "AWS/Lambda"
  namespace_cdh_lambda = "CDH/Lambda"
}

data "aws_caller_identity" "caller" {}

data "aws_partition" "current" {}

data "archive_file" "source-file" {
  count       = local.should_zip ? (var.source_is_file ? 1 : 0) : 0
  type        = "zip"
  source_file = var.source_path
  output_path = "/tmp/artifacts/${var.name}.zip"
}

data "external" "source-dir" {
  count = local.should_zip ? (var.source_is_file ? 0 : 1) : 0

  program = [
    "python",
    "package.py",
    "--task",
    "package",
    "--filename",
    var.name,
    "--code_path",
    local.path_to_source,
  ]
  working_dir = "${path.module}/../../../bin/"
}

data "aws_subnet" "lambda-subnet" {
  for_each = local.subnets
  id       = each.key
}

locals {
  dual_stack_ready = alltrue([
    for subnet in data.aws_subnet.lambda-subnet :
    (subnet.ipv6_cidr_block != "")
  ])
}


resource "aws_iam_role_policy_attachment" "ec2-networking" {
  count      = local.vpc_config ? 1 : 0
  role       = aws_iam_role.role.name
  policy_arn = "arn:${data.aws_partition.current.partition}:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

data "aws_vpc" "vpc" {
  count = local.look_up_subnets ? 1 : 0
  tags = {
    Name = var.vpc_name
  }
}

data "aws_subnets" "private_vpc_subnet_ids" {
  count = local.look_up_subnets ? 1 : 0
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.vpc[0].id]
  }
}

resource "aws_lambda_function" "lambda" {
  depends_on = [
    aws_cloudwatch_log_group.logs,
  ]

  description      = var.description
  filename         = local.should_zip ? (var.source_is_file ? data.archive_file.source-file[0].output_path : data.external.source-dir[0].result["file"]) : var.source_zip
  function_name    = var.name
  role             = aws_iam_role.role.arn
  handler          = var.handler
  source_code_hash = local.should_zip ? (var.source_is_file ? data.archive_file.source-file[0].output_base64sha256 : null) : var.source_hash
  runtime          = "python3.11"
  timeout          = var.timeout
  memory_size      = var.memory
  layers           = var.layers
  publish          = var.publish_lambda
  tracing_config {
    mode = var.xray_enabled ? "Active" : "PassThrough"
  }

  dynamic "vpc_config" {
    for_each = local.vpc_config ? [1] : []
    content {
      security_group_ids          = local.security_group_ids
      subnet_ids                  = local.subnets
      ipv6_allowed_for_dual_stack = local.dual_stack_ready
    }
  }

  reserved_concurrent_executions = var.reserved_concurrency

  environment {
    variables = merge({
      LOG_LEVEL                 = "INFO",
      ENVIRONMENT               = var.environment,
      AWS_LAMBDA_TIMEOUT        = var.timeout,
    }, var.environment_vars)
  }

  lifecycle {
    precondition {
      condition     = var.vpc_name != "" || (length(var.security_group_ids) > 0 == length(var.subnet_ids) > 0)
      error_message = "Invalid VPC config. Either provide none of security_group_ids, subnet_ids, and vpc_name for no vpc config, or both security_group_ids and subnet_ids, or vpc_name to look up values that weren't provided."
    }
  }
}

resource "aws_iam_role" "role" {
  name               = local.role_name
  description        = "Role for the ${var.name} lambda"
  assume_role_policy = <<-EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": {
          "Service": ["lambda.amazonaws.com"]
        },
        "Action": "sts:AssumeRole"
      }
    ]
  }
  EOF
}

# logs:CreateLogGroup is not really needed but the AWS console is unhappy without it
resource "aws_iam_role_policy" "write-log-stream" {
  name   = "${local.role_name}-logging-and-kms-decrypt"
  role   = aws_iam_role.role.id
  policy = <<-EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Sid": "Logging",
        "Effect": "Allow",
        "Action": [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        "Resource": ["${aws_cloudwatch_log_group.logs.arn}:*"]
      }
    ]
  }
  EOF
}

resource "aws_cloudwatch_metric_alarm" "errors" {
  count             = var.alert_on_invocation_errors ? 1 : 0
  alarm_name        = "${var.name}-invocation-errors"
  alarm_description = "The lambda function ${var.name} has invocation errors."

  comparison_operator = "GreaterThanThreshold"
  threshold           = 0
  evaluation_periods  = 1
  treat_missing_data  = "notBreaching"

  metric_name = "Errors"
  namespace   = local.namespace_aws_lambda
  period      = "300"
  statistic   = "Sum"

  dimensions = {
    FunctionName = aws_lambda_function.lambda.function_name
  }

  alarm_actions = [var.alerts_topic_arn]
}

resource "aws_cloudwatch_log_metric_filter" "memory" {
  name = "${var.name}-memory"
  # for a log entry like
  # REPORT RequestId: 7fe2df9d-b1cf-4867-8be7-3936a6b9de29 Duration: 2798.92 ms Billed Duration: 2800 ms Memory Size: 196 MB Max Memory Used: 101 MB Init Duration: 463.96 ms
  pattern        = "[a=REPORT, b=\"RequestId:\", c, d=\"Duration:\", e, f, g=Billed, h=\"Duration:\", i, j, k=Memory, l=\"Size:\", m, n, o=Max, p=Memory, q=\"Used:\", maxMemoryUsed, ...]"
  log_group_name = aws_cloudwatch_log_group.logs.name

  metric_transformation {
    name      = "MemoryUtilization ${var.name}"
    namespace = local.namespace_cdh_lambda
    value     = "$maxMemoryUsed"
  }
}

resource "aws_cloudwatch_metric_alarm" "memory-critical" {
  alarm_name        = "${var.name}-memory-critical"
  alarm_description = "The lambda function ${var.name} has dangerously high memory usage"

  comparison_operator = "GreaterThanThreshold"
  threshold           = 0.9 * var.memory
  evaluation_periods  = 1
  treat_missing_data  = "notBreaching"

  metric_name = "MemoryUtilization ${var.name}"
  namespace   = local.namespace_cdh_lambda
  period      = "300"
  statistic   = "Maximum"

  alarm_actions = [var.alerts_topic_arn]
}

resource "aws_cloudwatch_log_group" "logs" {
  name              = "/aws/lambda/${var.name}"
  retention_in_days = var.log_retention
}

resource "aws_cloudwatch_log_subscription_filter" "logs_subscription" {
  count          = var.needs_log_subscription ? 1 : 0
  name           = "${var.name}cdh-logs-subscription-filter"
  log_group_name = aws_cloudwatch_log_group.logs.name
  filter_pattern = "[severity=ERROR || severity=CRITICAL, event]"
  # The following ideal pattern is not sufficient to match on lambda container specific errors:
  #filter_pattern  = "[severity=ERROR || severity=CRITICAL, timestamp=*Z, request_id=*-*, event]"
  destination_arn = var.logs_subscription_arn
}

output "role_name" {
  value = aws_iam_role.role.name
}

output "role_arn" {
  value = aws_iam_role.role.arn
}

output "function_arn" {
  value = aws_lambda_function.lambda.arn
}

output "function_name" {
  value = aws_lambda_function.lambda.function_name
}

output "version" {
  value = aws_lambda_function.lambda.version
}

output "invoke_arn" {
  value = aws_lambda_function.lambda.invoke_arn
}
