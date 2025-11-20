resource "aws_iam_role" "lambda_role" {
  name = "${lookup(local.resource_prefix_map, "iam-role", local.region_alias)}-lambda"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect    = "Allow",
        Principal = { Service = "lambda.amazonaws.com" }
        Action    = "sts:AssumeRole"
      }
    ]
  })
}

# resource "aws_iam_role_policy" "lambda-pol-sns" {
#   name = "${lookup(local.resource_prefix_map, "iam-policy", "${local.region_alias}")}-sns"
#   role = aws_iam_role.lambda_role.id
#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Effect = "Allow",
#         Action = "sns:Publish",
#         Resource = var.sns_arn
#       }
#     ]
#   })
# }


# Basic Lambda execution policy (logs)
resource "aws_iam_role_policy" "lambda_logs_policy" {
  name = "${lookup(local.resource_prefix_map, "iam-policy", local.region_alias)}-logs"
  role = aws_iam_role.lambda_role.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}