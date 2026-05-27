terraform {
  required_version = ">=1.0.0"
  required_providers {
    aws = {
        source = "hashicorp/aws"
        #source = "hashicorp/archive"
        version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}