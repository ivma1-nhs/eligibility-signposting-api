# Terraform State Management Policy
resource "aws_iam_policy" "terraform_state" {
  name        = "terraform-state-management"
  description = "Policy granting access to S3 bucket for Terraform state"
  path        = "/service-policies/"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "s3:ListBucket",
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ],
        Resource = [
          "${local.terraform_state_bucket_arn}",
          "${local.terraform_state_bucket_arn}/*"
        ]
      }
    ]
  })

  tags = merge(
    local.tags,
    {
      Name = "terraform-state-management"
    }
  )
}

# Lambda Management Policy
resource "aws_iam_policy" "lambda_management" {
  name        = "lambda-management"
  description = "Policy granting permissions to manage Lambda functions for this stack"
  path        = "/service-policies/"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "lambda:CreateFunction",
          "lambda:UpdateFunctionCode",
          "lambda:UpdateFunctionConfiguration",
          "lambda:DeleteFunction",
          "lambda:GetFunction",
          "lambda:GetFunctionConfiguration",
          "lambda:GetFunctionCodeSigningConfig",
          "lambda:ListVersionsByFunction",
          "lambda:TagResource",
          "lambda:UntagResource",
          "lambda:ListTags",
          "lambda:PublishVersion",
          "lambda:CreateAlias",
          "lambda:UpdateAlias",
          "lambda:DeleteAlias",
          "lambda:ListAliases",
          "lambda:AddPermission",
          "lambda:RemovePermission",
          "lambda:GetPolicy"
        ],
        Resource = [
          "arn:aws:lambda:*:${data.aws_caller_identity.current.account_id}:function:*eligibility_signposting_api"
        ]
      }
    ]
  })

  tags = merge(local.tags, { Name = "lambda-management" })
}

# DynamoDB Management Policy
resource "aws_iam_policy" "dynamodb_management" {
  name        = "dynamodb-management"
  description = "Policy granting permissions to manage DynamoDB tables for this stack"
  path        = "/service-policies/"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "dynamodb:DescribeTimeToLive",
          "dynamodb:DescribeTable",
          "dynamodb:DescribeContinuousBackups",
          "dynamodb:ListTables",
          "dynamodb:DeleteTable",
          "dynamodb:CreateTable"
        ],
        Resource = [
          "arn:aws:dynamodb:*:${data.aws_caller_identity.current.account_id}:table:*eligibility_datastore"
        ]
      }
    ]
  })

  tags = merge(local.tags, { Name = "dynamodb-management" })
}

# S3 Management Policy
resource "aws_iam_policy" "s3_management" {
  name        = "s3-management"
  description = "Policy granting permissions to manage S3 buckets"
  path        = "/service-policies/"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "s3:GetLifecycleConfiguration",
          "s3:PutLifecycleConfiguration",
          "s3:GetBucketVersioning",
          "s3:GetEncryptionConfiguration",
          "s3:PutEncryptionConfiguration",
          "s3:GetBucketPolicy",
          "s3:GetBucketObjectLockConfiguration",
          "s3:GetBucketLogging",
          "s3:GetReplicationConfiguration",
          "s3:GetBucketWebsite",
          "s3:GetBucketRequestPayment",
          "s3:GetBucketCORS",
          "s3:GetBucketAcl",
          "s3:PutBucketAcl",
          "s3:GetAccelerateConfiguration",
          "s3:ListBucket",
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:GetBucketLocation",
          "s3:GetBucketPublicAccessBlock",
          "s3:PutBucketCORS",
          "s3:CreateBucket",
          "s3:DeleteBucket"
        ],
        Resource = [
          "arn:aws:s3:::*eligibility-signposting-${var.environment}-eli-rules",
          "arn:aws:s3:::*eligibility-signposting-${var.environment}-eli-rules/*",
          "arn:aws:s3:::*eligibility-signposting-${var.environment}-eli-audit",
          "arn:aws:s3:::*eligibility-signposting-${var.environment}-eli-audit/*",
          "arn:aws:s3:::*eligibility-signposting-${var.environment}-eli-rules-access-logs",
          "arn:aws:s3:::*eligibility-signposting-${var.environment}-eli-rules-access-logs/*",
          "arn:aws:s3:::*eligibility-signposting-${var.environment}-eli-audit-access-logs",
          "arn:aws:s3:::*eligibility-signposting-${var.environment}-eli-audit-access-logs/*"
        ]
      }
    ]
  })

  tags = merge(local.tags, { Name = "s3-management" })
}

# API Infrastructure Management Policy
resource "aws_iam_policy" "api_infrastructure" {
  #checkov:skip=CKV_AWS_355 EC2 permissions allow all actions on all resources
  #checkov:skip=CKV_AWS_288 Role needs access to SSM and logs
  #checkov:skip=CKV_AWS_290 Write access limited to tags and network ACL entries

  name        = "api-infrastructure-management"
  description = "Policy granting permissions to manage API infrastructure"
  path        = "/service-policies/"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [

          # Cloudwatch permissions
          "logs:Describe*",
          "logs:ListTagsForResource",
          "logs:PutRetentionPolicy",
          "logs:AssociateKmsKey",

          #EC2 permissions
          "ec2:Describe*",
          "ec2:CreateTags",
          "ec2:CreateNetworkAclEntry",

          # ssm
          "ssm:GetParameter",
          "ssm:GetParameters",
          "ssm:DescribeParameters",
          "ssm:ListTagsForResource",

          # acm
          "acm:ListCertificates",
          "acm:DescribeCertificate",
          "acm:GetCertificate",
          "acm:ListTagsForCertificate",
        ],


        Resource = "*"
      }
    ]
  })

  tags = merge(
    local.tags,
    {
      Name = "api-infrastructure-management"
    }
  )
}

# IAM Management Policy
resource "aws_iam_policy" "iam_management" {
  name        = "iam-management"
  description = "Policy granting permissions to manage only project-specific IAM roles and policies"
  path        = "/service-policies/"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "iam:Get*",
          "iam:GetPolicy*",
          "iam:GetRole*",
          "iam:List*",
          "iam:CreateRole",
          "iam:DeleteRole",
          "iam:UpdateRole",
          "iam:PutRolePolicy",
          "iam:PutRolePermissionsBoundary",
          "iam:AttachRolePolicy",
          "iam:DetachRolePolicy",
          "iam:CreatePolicyVersion"
        ],
        Resource = [
          # Lambda role
          "arn:aws:iam::*:role/eligibility_lambda-role*",
          # API Gateway role
          "arn:aws:iam::*:role/*-api-gateway-*-role",
          # External write role
          "arn:aws:iam::*:role/eligibility-signposting-api-*-external-write-role",
          # Project policies
          "arn:aws:iam::*:policy/*api-gateway-logging-policy",
          "arn:aws:iam::*:policy/*PermissionsBoundary"
        ]
      }
    ]
  })
  tags = merge(local.tags, { Name = "iam-management" })
}

# Assume role policy document for GitHub Actions
data "aws_iam_policy_document" "github_actions_assume_role" {
  statement {
    sid     = "OidcAssumeRoleWithWebIdentity"
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type = "Federated"
      identifiers = [
        aws_iam_openid_connect_provider.github.arn
      ]
    }

    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values   = ["repo:${var.github_org}/${var.github_repo}:*"]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }
  }
}

# Attach the policies to the role
resource "aws_iam_role_policy_attachment" "terraform_state" {
  role       = aws_iam_role.github_actions.name
  policy_arn = aws_iam_policy.terraform_state.arn
}

resource "aws_iam_role_policy_attachment" "api_infrastructure" {
  role       = aws_iam_role.github_actions.name
  policy_arn = aws_iam_policy.api_infrastructure.arn
}

resource "aws_iam_role_policy_attachment" "lambda_management" {
  role       = aws_iam_role.github_actions.name
  policy_arn = aws_iam_policy.lambda_management.arn
}

resource "aws_iam_role_policy_attachment" "dynamodb_management" {
  role       = aws_iam_role.github_actions.name
  policy_arn = aws_iam_policy.dynamodb_management.arn
}

resource "aws_iam_role_policy_attachment" "s3_management" {
  role       = aws_iam_role.github_actions.name
  policy_arn = aws_iam_policy.s3_management.arn
}

resource "aws_iam_role_policy_attachment" "iam_management" {
  role       = aws_iam_role.github_actions.name
  policy_arn = aws_iam_policy.iam_management.arn
}

data "aws_caller_identity" "current" {}
