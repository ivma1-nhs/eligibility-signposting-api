module "eligibility_signposting_api_gateway" {
  source                   = "../../modules/api_gateway"
  api_gateway_name         = "eligibility-signposting-api"
  disable_default_endpoint = var.environment == "dev" && local.workspace != "dev" ? false : true
  workspace                = local.workspace
  stack_name               = local.stack_name
  environment              = var.environment
  tags                     = local.tags
}

resource "aws_api_gateway_resource" "_status" {
  rest_api_id = module.eligibility_signposting_api_gateway.rest_api_id
  parent_id   = module.eligibility_signposting_api_gateway.root_resource_id
  path_part   = "_status"
}

resource "aws_api_gateway_resource" "patient_check" {
  rest_api_id = module.eligibility_signposting_api_gateway.rest_api_id
  parent_id   = module.eligibility_signposting_api_gateway.root_resource_id
  path_part   = "patient-check"
}

resource "aws_api_gateway_resource" "id" {
  rest_api_id = module.eligibility_signposting_api_gateway.rest_api_id
  parent_id   = aws_api_gateway_resource.patient_check.id
  path_part   = "{id}"
}
