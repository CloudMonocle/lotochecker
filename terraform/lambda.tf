# Package Lambda
data "archive_file" "lambda_zip" {
  type       = "zip"
  source_dir = "../lambda"
  excludes = [
    "test_*.py",
  ]
  output_path = "/tmp/lambda.zip"
}

# Lambda Function
resource "aws_lambda_function" "lotochecker_function" {
  function_name    = "${lookup(local.resource_prefix_map, "lambda-function", local.region_alias)}-checker"
  handler          = "main.lambda_handler"
  runtime          = "python3.11"
  role             = aws_iam_role.lambda_role.arn
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  timeout          = 30
  layers = [
    "arn:aws:lambda:${data.aws_region.current.name}:336392948345:layer:AWSSDKPandas-Python311:24",
    "arn:aws:lambda:${data.aws_region.current.name}:519388350760:layer:awssetup-dub-lambda-layer-requests:2",
  ]
  environment {
    variables = {
      SNS_TOPIC_ARN   = var.sns_arn
      DISCORD_CHANNEL = var.discord_channel
      NUMBERS_JSON    = var.check_numbers_file
    }
  }
  dead_letter_config {
    target_arn = var.sns_arn
  }
  tags = local.tags
}