# tflint-ignore: terraform_unused_declarations
variable "project_name" {
  default = "eligibility-signposting-api"
  type    = string
}

variable "environment" {
  default     = "dev"
  description = "Environment"
  type        = string
}

variable "terraform_state_bucket_name" {
  default     = "eligibility-signposting-api-${var.environment}-tfstate"
  description = "S3 bucket for Terraform state"
  type        = string
}
