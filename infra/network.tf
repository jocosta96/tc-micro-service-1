# Network configuration now managed in centralized locals.tf
locals {
    network_tags = {"origin" = "tc-micro-service-1/infra/network.tf"}
    lambda_sg_ids = []
}

resource "aws_vpc" "ordering_vpc" {
  cidr_block           = local.vpc_cidr_block
  enable_dns_hostnames = true
  enable_dns_support   = true

	tags                 = merge(local.default_tags, local.network_tags)
}

resource "aws_subnet" "ordering_subnet" {
  count                   = local.subnet_count
  vpc_id                  = aws_vpc.ordering_vpc.id
  cidr_block              = cidrsubnet(local.vpc_cidr_block, 4, count.index)
  map_public_ip_on_launch = false
  availability_zone       = local.availability_zones[count.index]0

  tags                    = merge(local.default_tags, local.network_tags)
}

# ===== SECURITY GROUPS =====

resource "aws_security_group" "gateway_sg" {
  name_prefix = "gateway-sg"
  vpc_id      = aws_vpc.ordering_vpc.id

  tags = merge(local.default_tags, local.network_tags)
}

## Allow traffic from lambda security groups
#resource "aws_vpc_security_group_ingress_rule" "eks_cluster_ingress_node_https" {
#  security_group_id            = aws_security_group.gateway_sg.id
#  referenced_security_group_id = local.lambda_sg_ids[*]
#  from_port                    = 443
#  ip_protocol                  = "tcp"
#  to_port                      = 443
#
#  tags = merge(local.default_tags, local.network_tags)
#}

# Egress rules - Allow all outbound traffic
resource "aws_vpc_security_group_egress_rule" "gateway_egress" {
  security_group_id = aws_security_group.gateway_sg.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"

  tags = merge(local.default_tags, local.network_tags)
}
