variable "aws_account_id" {
  type        = string
  description = "Account Nubmer to deploy in"
}

variable "aws_role_name" {
  type        = string
  description = "Role to deploy with"
}

variable "environment" {
  type        = string
  description = "environment the code being deplyed"
}

variable "sns_arn" {
  type = string
}

variable "check_numbers_file" {
  type        = string
  description = "Path to the JSON file containing the numbers to check"
  default     = "loto_numers.json.example"
}