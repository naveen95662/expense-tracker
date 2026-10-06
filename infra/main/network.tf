# Use the account's default VPC instead of creating a new network.

data "aws_vpc" "default" {
  default = true
}

# Subnets that already belong to the default VPC (used by the Fargate service).
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# App security group: port 8000 from my IP only; all outbound so the task can pull images and call AWS.
resource "aws_security_group" "app" {
  name        = "expense-tracker-app"
  description = "Allow TCP 8000 from my IP only"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "API from my public IP"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = [var.my_ip_cidr]
  }

  egress {
    description = "All outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
