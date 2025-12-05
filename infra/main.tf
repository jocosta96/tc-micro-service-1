locals {

#General
  default_tags = {
    project     = "ordering-system"
    environment = var.ENVIRONMENT
    created_by  = "terraform"
    team        = "fiap"
  }

  availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]

# Network
  vpc_cidr_block =  "10.0.0.0/16"
	subnet_cidr_block = "10.0.1.0/24"
	subnet_count = 2

}