resource "aws_cloudwatch_log_group" "api_gateway" {
  name              = "/aws/apigateway/${var.workspace}-${var.api_gateway_name}"
  retention_in_days = 14
  tags              = var.tags
  kms_key_id        = aws_kms_key.api_gateway.arn

}

resource "aws_iam_policy_document" "api_gateway_logging" {
  statement {
    sid    = "AllowCloudWatchLogging"
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:DescribeLogGroups",
      "logs:DescribeLogStreams",
      "logs:PutLogEvents",
      "logs:GetLogEvents",
      "logs:FilterLogEvents"
    ]
    resources = [aws_cloudwatch_log_group.api_gateway.arn]
  }
}
