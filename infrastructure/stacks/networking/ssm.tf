# resource "aws_ssm_parameter" "proxygen_private_key" {
#   count = var.environment == "dev" ? 1 : 0
#   name  = "/proxygen/private_key"
#   type  = "SecureString"
#   value = var.PROXYGEN_PRIVATE_KEY
#   tier  = "Advanced"
#
#   tags = {
#     Stack = local.stack_name
#   }
# }
#
data "aws_ssm_parameter" "existing_ca_cert" {
  name = "/${var.environment}/mtls/api_ca_cert"
}

data "aws_ssm_parameter" "existing_client_cert" {
  name = "/${var.environment}/mtls/api_client_cert"
}

data "aws_ssm_parameter" "existing_private_key_cert" {
  name = "/${var.environment}/mtls/api_private_key_cert"
}


resource "aws_ssm_parameter" "mtls_api_ca_cert" {
  count  = can(data.aws_ssm_parameter.existing_ca_cert.id) ? 0 : 1
  name   = "/${var.environment}/mtls/api_ca_cert"
  type   = "SecureString"
  key_id = aws_kms_key.networking_ssm_key.id
  value  = var.API_CA_CERT
  tier   = "Advanced"
  tags = {
    Stack = local.stack_name
  }
  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "mtls_api_client_cert" {
  count  = can(data.aws_ssm_parameter.existing_client_cert.id) ? 0 : 1
  name   = "/${var.environment}/mtls/api_client_cert"
  type   = "SecureString"
  key_id = aws_kms_key.networking_ssm_key.id
  value  = var.API_CLIENT_CERT
  tier   = "Advanced"
  tags = {
    Stack = local.stack_name
  }
  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "mtls_api_private_key_cert" {
  count  = can(data.aws_ssm_parameter.existing_private_key_cert.id) ? 0 : 1
  name   = "/${var.environment}/mtls/api_private_key_cert"
  type   = "SecureString"
  key_id = aws_kms_key.networking_ssm_key.id
  value  = var.API_PRIVATE_KEY_CERT
  tier   = "Advanced"
  tags = {
    Stack = local.stack_name
  }

  lifecycle {
    ignore_changes = [value]
  }
}
