module "tfstate" {
  source = "../../modules/bootstrap/tfstate"

  project_name = var.project_name
  environment  = var.environment
  workspace    = var.workspace
  stack_name   = local.stack_name
}
