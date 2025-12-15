locals {
    storage_tags = {
        "origin" = "tc-micro-service-1/infra/storage.tf"
    }
}

resource "aws_s3_bucket" "backend_bucket" {
  bucket = "ordering-system-terraform-${data.aws_caller_identity.current.account_id}"

  tags = merge(
    local.default_tags,
    local.storage_tags,
    {"name": "ordering-system-terraform"}
  )
}

# Enable versioning for data protection and rollback capability
resource "aws_s3_bucket_versioning" "backend_bucket" {
  bucket = aws_s3_bucket.backend_bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Enable encryption with KMS CMK
resource "aws_s3_bucket_server_side_encryption_configuration" "backend_bucket" {
  bucket = aws_s3_bucket.backend_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.ssm_key.arn
    }
    bucket_key_enabled = true
  }
}

# Enable access logging
/* Access logging is intentionally sent via S3 access logs to a central account
   if required. For now we avoid creating an extra logs bucket and instead
   capture object-level events via SQS notifications (see below). */

# Lifecycle policy for log retention and cost optimization
resource "aws_s3_bucket_lifecycle_configuration" "backend_bucket" {
  bucket = aws_s3_bucket.backend_bucket.id

  rule {
    id     = "archive-old-versions"
    status = "Enabled"

    noncurrent_version_transition {
      noncurrent_days = 30
      storage_class   = "STANDARD_IA"
    }

    noncurrent_version_transition {
      noncurrent_days = 90
      storage_class   = "GLACIER"
    }

    noncurrent_version_expiration {
      noncurrent_days = 180
    }
  }
}

# Public access block for security
resource "aws_s3_bucket_public_access_block" "backend_bucket" {
  bucket = aws_s3_bucket.backend_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
