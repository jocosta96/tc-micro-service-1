locals {
    storage_tags = {
        "origin" = "tc-micro-service-1/infra/storage.tf"
    }
}

resource "aws_s3_bucket" "backend_bucket" {
  bucket = "ordering"

  tags = merge(
    local.default_tags,
    local.storage_tags,
    {"name": "ordering"}
  )
}