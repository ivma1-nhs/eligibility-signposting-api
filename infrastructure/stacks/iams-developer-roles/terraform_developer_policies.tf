# Trust policy document
data "aws_iam_policy_document" "terraform_developer_assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }

    condition {
      test     = "StringLike"
      variable = "aws:PrincipalArn"
      values   = [
        "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/aws-reserved/sso.amazonaws.com/*/AWSReservedSSO_vdselid_${var.environment}_*"
      ]
    }
  }
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

  # Permissions for the specific resources in our stacks
  statement {
    effect = "Allow"
    actions = [
      # Lambda permissions
      "lambda:*",

      # DynamoDB permissions
      "dynamodb:*",

      # CloudWatch permissions
      "logs:*",
      "cloudtrail:*",
      "cloudwatch:*",

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
