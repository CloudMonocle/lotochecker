data "aws_region" "current" {}

locals {
  project_name = "lotochecker"
  tags = {
    environment = var.environment,
    project     = local.project_name
  }
  region_alias_map = {
    "eu-west-1" = "dub"
    "eu-west-2" = "lon"
    "us-east-1" = "vir"
    "us-west-2" = "pdx"
  }
  env_map = {
    "development" = "dev"
    "production"  = "prod"
  }
  region_alias      = lookup(local.region_alias_map, data.aws_region.current.name, "other")
  environment_alias = lookup(local.env_map, var.environment, "other")
  resource_prefix_map = {
    "iam-role"        = "${local.project_name}-${local.environment_alias}-glo-iam-role"
    "iam-policy"      = "${local.project_name}-${local.environment_alias}-iam-poli"
    "s3"              = "${local.project_name}-${local.environment_alias}-glo-s3-"
    "lambda-function" = "${local.project_name}-${local.environment_alias}-${local.region_alias}-lambda-function"
    "sns"             = "${local.project_name}-${local.environment_alias}-${local.region_alias}-sns-"
    "ec2"             = "${local.project_name}-${local.environment_alias}-${local.region_alias}-ec2-"
    "dynamodb"        = "${local.project_name}-${local.environment_alias}-${local.region_alias}-dynamodb-"
    "event"           = "${local.project_name}-${local.environment_alias}-${local.region_alias}-event-"
  }
}