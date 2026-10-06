# Region and the only AWS account this stack is allowed to use.
variable "aws_region" {
  type        = string
  description = "AWS region for main stack resources."
  default     = "ap-south-1"
}

variable "allowed_account_id" {
  type        = string
  description = "AWS account id this stack may target. Set TF_VAR_allowed_account_id."
}

# Your public IP as CIDR (e.g. 203.0.113.10/32). Set TF_VAR_my_ip_cidr.
variable "my_ip_cidr" {
  type        = string
  description = "Public IP allowed to reach the app on port 8000, in /32 CIDR form."
}

# Image tag to run from ECR. Default latest; override when you push a tagged build.
variable "image_tag" {
  type        = string
  description = "ECR image tag for the app container."
  default     = "latest"
}

# Keep at 0 so no Fargate tasks run until you scale the service up.
variable "desired_count" {
  type        = number
  description = "How many Fargate tasks the ECS service should run."
  default     = 0
}
