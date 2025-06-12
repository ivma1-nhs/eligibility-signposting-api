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
data "aws_ssm_parameters_with_values" "existing_client_cert" {
  names = ["/${var.environment}/mtls/api_client_cert"]
}

data "aws_ssm_parameters_with_values" "existing_ca_cert" {
  names = ["/${var.environment}/mtls/api_ca_cert"]
}

data "aws_ssm_parameters_with_values" "existing_private_key_cert" {
  names = ["/${var.environment}/mtls/api_private_key_cert"]
}


resource "aws_ssm_parameter" "mtls_api_ca_cert" {
  count  = length(data.aws_ssm_parameters_with_values.existing_ca_cert.names) == 0 ? 1 : 0
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
  count  = length(data.aws_ssm_parameters_with_values.existing_client_cert.names) == 0 ? 1 : 0
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
  count  = length(data.aws_ssm_parameters_with_values.existing_private_key_cert.names) == 0 ? 1 : 0
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
