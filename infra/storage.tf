locals {
    storage_tags = {
        "origin" = "tc-micro-service-1/infra/storage.tf"
    }
}

resource "aws_s3_bucket" "backend_bucket" {
  bucket = "ordering-system-terraform"

  tags = merge(
    local.default_tags,
    local.storage_tags,
    {"name": "ordering-system-terraform"}
  )
}

resource "aws_s3_bucket_public_access_block" "backend_bucket" {
  bucket = aws_s3_bucket.backend_bucket.id
  block_public_acls   = true
  block_public_policy = true
}
