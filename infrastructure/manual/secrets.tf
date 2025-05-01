

data "aws_secretsmanager_secret" "ig_api_secrets" {
  name = "IG_API_SECRETS_${upper(var.environment)}"
}

data "aws_secretsmanager_secret_version" "ig_api_secrets_version" {
  secret_id = data.aws_secretsmanager_secret.ig_api_secrets.id
  version_stage = "AWSCURRENT"
}

data "aws_secretsmanager_secret" "discord_webhook_secrets" {
  name = "DISCORD_WEBHOOKS_${upper(var.environment)}"
}

data "aws_secretsmanager_secret_version" "discord_webhook_secrets_version" {
  secret_id = data.aws_secretsmanager_secret.discord_webhook_secrets.id
  version_stage = "AWSCURRENT"
}

data "aws_secretsmanager_secret" "polygon_secrets" {
  name = "POLYGON_API_KEY"
}

data "aws_secretsmanager_secret_version" "polygon_secrets_version" {
  secret_id = data.aws_secretsmanager_secret.polygon_secrets.id
  version_stage = "AWSCURRENT"
}
