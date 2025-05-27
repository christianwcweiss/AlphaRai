
data "aws_secretsmanager_secret" "polygon_secrets" {
  name = "POLYGON_API_KEY"
}

data "aws_secretsmanager_secret_version" "polygon_secrets_version" {
  secret_id = data.aws_secretsmanager_secret.polygon_secrets.id
  version_stage = "AWSCURRENT"
}
