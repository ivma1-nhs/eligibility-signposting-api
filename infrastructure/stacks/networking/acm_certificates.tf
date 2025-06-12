resource "aws_acm_certificate" "imported_cert" {
  private_key       = can(data.aws_ssm_parameter.existing_private_key_cert.id) ? data.aws_ssm_parameter.existing_private_key_cert.value : aws_ssm_parameter.mtls_api_private_key_cert[0].value
  certificate_body  = can(data.aws_ssm_parameter.existing_client_cert.id) ? data.aws_ssm_parameter.existing_client_cert.value : aws_ssm_parameter.mtls_api_client_cert[0].value
  certificate_chain = can(data.aws_ssm_parameter.existing_ca_cert.id) ? data.aws_ssm_parameter.existing_ca_cert.value : aws_ssm_parameter.mtls_api_ca_cert[0].value

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Region          = local.region
    Stack           = local.stack_name
    CertificateType = "Imported"
  }
}

resource "aws_acm_certificate" "domain_validation" {
  domain_name       = "${var.environment}.eligibility-signposting-api.nhs.uk"
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Region          = local.region
    Stack           = local.stack_name
    CertificateType = "DomainValidation"
  }
}
