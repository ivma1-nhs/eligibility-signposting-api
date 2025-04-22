resource "aws_iam_role" "terraform_developer" {
  name               = "terraform-developer-role"
  description        = "Role for developers to plan and apply Terraform changes"
  assume_role_policy = data.aws_iam_policy_document.terraform_developer_assume_role.json
  max_session_duration = 14400  # 4 hours

  tags = merge(
    local.tags,
    {
      Name = "terraform-developer-role"
    }
  )
}
