locals {
  website_origin_name   = "${var.domain_name}.s3.${var.region}.amazonaws.com"
  website_origin_domain = "${var.domain_name}.s3-website-${var.region}.amazonaws.com"
  archive_origin_name   = "${var.archive_bucket_name}.s3.${var.region}.amazonaws.com"
  archive_origin_domain = "${var.archive_bucket_name}.s3.${var.region}.amazonaws.com"
}

resource "aws_cloudfront_distribution" "nltl_cdn" {

  enabled = true
  aliases = [
    "www.nothinglefttolearn.com",
  ]
  comment         = "NLTL CDN"
  is_ipv6_enabled = true
  origin {
    origin_id   = local.website_origin_name
    domain_name = local.website_origin_domain
    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "http-only"
      origin_ssl_protocols   = ["TLSv1"]
    }
  }

  origin {
    origin_id   = local.archive_origin_name
    domain_name = local.archive_origin_domain

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.nltl_cdn_oai.cloudfront_access_identity_path
    }
  }

  default_cache_behavior {

    target_origin_id = local.website_origin_name
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 0
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  price_class = "PriceClass_All"

}

resource "aws_cloudfront_origin_access_identity" "nltl_cdn_oai" {
  comment = "OAI for my static website bucket"
}
