resource "aws_s3_bucket" "nltl_tfstate" {
  bucket = var.state_bucket_name
  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.nltl_tfstate.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket" "nltl_website" {
  bucket = var.domain_name
}
resource "aws_s3_bucket_website_configuration" "nltl_website" {
  bucket = aws_s3_bucket.nltl_website.id
  index_document {
    suffix = "index.html"
  }
  error_document {
    key = "error.html"
  }
}

resource "aws_s3_bucket_public_access_block" "website_access" {
  bucket                  = aws_s3_bucket.nltl_website.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}


resource "aws_s3_bucket" "nltl_archive" {
  bucket = var.archive_bucket_name
}

resource "aws_s3_bucket_public_access_block" "archive_access" {
  bucket                  = aws_s3_bucket.nltl_archive.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}