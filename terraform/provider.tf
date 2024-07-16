terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.58.0"
    }
  }
}
provider "aws" {
  region  = var.region
  profile = "tf_user"
}