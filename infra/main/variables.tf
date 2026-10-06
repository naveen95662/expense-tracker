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
