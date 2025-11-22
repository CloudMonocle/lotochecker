terraform {
  required_version = ">= 1.0.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5" # Use a suitable version for your needs
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2" # Use a suitable version for your needs
    }
  }
  backend "s3" {
    encrypt = true
  }
}