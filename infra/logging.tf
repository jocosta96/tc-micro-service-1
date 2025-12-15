
# Enable bucket notifications for monitoring
resource "aws_sqs_queue" "s3_events_queue" {
  name = "ordering-system-s3-events"
  kms_master_key_id = aws_kms_key.ssm_key.arn

  tags = merge(
    local.default_tags,
    local.storage_tags,
    {"name": "ordering-system-s3-events-queue"}
  )
}

resource "aws_sqs_queue_policy" "s3_events_policy" {
  queue_url = aws_sqs_queue.s3_events_queue.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid = "AllowS3SendMessage",
        Effect = "Allow",
        Principal = "*",
        Action = "SQS:SendMessage",
        Resource = aws_sqs_queue.s3_events_queue.arn,
        Condition = {
          ArnEquals = {
            "aws:SourceArn" = aws_s3_bucket.backend_bucket.arn
          }
        }
      }
    ]
  })
}

resource "aws_s3_bucket_notification" "backend_bucket" {
  bucket = aws_s3_bucket.backend_bucket.id

  queue {
    queue_arn = aws_sqs_queue.s3_events_queue.arn
    events    = ["s3:ObjectCreated:*", "s3:ObjectRemoved:*"]
    filter_suffix = "tfstate"
  }
}

/* Removed a dedicated logs bucket and Lambda monitor as per preference to
   use SQS for notifications instead. Access logs can still be enabled to a
   centralized logging account bucket if desired; that can be added later. */