# Trust policy document
data "aws_iam_policy_document" "terraform_developer_assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "AWS"
      identifiers = [for user in var.developer_users : "arn:aws:iam::${data.aws_caller_identity.current.account_id}:user/${user}"]
    }

    # Optional: Add MFA condition for additional security
    condition {
      test     = "Bool"
      variable = "aws:MultiFactorAuthPresent"
      values   = ["true"]
    }
  }
}

# Create the role
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

# Policy document for terraform access
data "aws_iam_policy_document" "terraform_developer_policy" {
  # S3 bucket for Terraform state
  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:ListBucket"
    ]
    resources = [
      "arn:aws:s3:::eligibility-signposting-api-${var.environment}-tfstate",
      "arn:aws:s3:::eligibility-signposting-api-${var.environment}-tfstate/*"
    ]
  }

  # Permissions for the specific resources in your stacks
  statement {
    effect = "Allow"
    actions = [
      # VPC permissions
      "ec2:*Vpc*",
      "ec2:*Subnet*",
      "ec2:*RouteTable*",
      "ec2:*InternetGateway*",
      "ec2:*SecurityGroup*",
      "ec2:*NetworkAcl*",
      "ec2:*VpcEndpoint*",

      # Lambda permissions
      "lambda:*",

      # CloudWatch permissions
      "logs:*",

      # IAM permissions (restricted)
      "iam:Get*",
      "iam:List*",
      "iam:PassRole",

      # KMS permissions
      "kms:Describe*",
      "kms:List*",
      "kms:Get*",

      # SSM permissions
      "ssm:GetParameter*",
      "ssm:PutParameter",

      # S3 permissions for application buckets
      "s3:List*",
      "s3:Get*",
      "s3:Put*",
      "s3:CreateBucket",
      "s3:DeleteObject",

      # API Gateway permissions
      "apigateway:*"
    ]
    resources = ["*"]
  }

  # Read-only permissions for broader resources
  statement {
    effect = "Allow"
    actions = [
      "ec2:Describe*",
      "iam:Get*",
      "iam:List*",
      "s3:List*",
      "kms:List*"
    ]
    resources = ["*"]
  }
}

# Create policy from document
resource "aws_iam_policy" "terraform_developer_policy" {
  name        = "terraform-developer-policy"
  description = "Policy for terraform developers to manage resources"
  policy      = data.aws_iam_policy_document.terraform_developer_policy.json
}

# Attach policy to role
resource "aws_iam_role_policy_attachment" "terraform_developer_attachment" {
  role       = aws_iam_role.terraform_developer.name
  policy_arn = aws_iam_policy.terraform_developer_policy.arn
}
