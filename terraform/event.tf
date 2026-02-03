resource "aws_cloudwatch_event_rule" "lotochecker_schedule" {
  name                = "${lookup(local.resource_prefix_map, "event", local.region_alias)}rule-schedule"
  description         = "Triggers the LotoChecker Lambda function"
  schedule_expression = "cron(30 21 ? * SAT *)"
  state               = var.environment == "production" ? "ENABLED" : "DISABLED"
}

resource "aws_cloudwatch_event_target" "lotochecker_target" {
  rule      = aws_cloudwatch_event_rule.lotochecker_schedule.name
  target_id = "${local.project_name}Lambda"
  arn       = aws_lambda_function.lotochecker_function.arn
}

resource "aws_lambda_permission" "allow_events" {
  statement_id  = "AllowCloudWatchInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lotochecker_function.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.lotochecker_schedule.arn
}