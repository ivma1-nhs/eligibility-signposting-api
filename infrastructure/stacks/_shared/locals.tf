locals {
  # tflint-ignore: terraform_unused_declarations
  environment = var.environment
  # tflint-ignore: terraform_unused_declarations
  workspace = lower(terraform.workspace)
  # tflint-ignore: terraform_unused_declarations
  runtime = "python3.13.1"

  # tflint-ignore: terraform_unused_declarations
  tags = {
    TagVersion      = "1"
    Programme       = "Vaccinations"
    Project         = "EligibilitySignpostingAPI"
    Environment     = var.environment
    ServiceCategory = var.environment == "prod" ? "Bronze" : "N/A"
    Tool            = "Terraform"
  }

  sso_role_patterns = {
    dev  = "AWSReservedSSO_vdselid_dev_*"
    test = "AWSReservedSSO_vdselid_test_*"
  }
}
