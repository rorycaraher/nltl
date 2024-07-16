terraform {
  backend "s3" {
    bucket  = "nltl-tfstate"
    key     = "terraform/state"
    region  = "eu-west-1"
    encrypt = true
    profile = "tf_user"
  }
}