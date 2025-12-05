terraform {
  backend "s3" {
    bucket = "ordering-system-terraform"
    key    = "tc-micro-service-1.state"
    region = "us-east-1"
  }
}
