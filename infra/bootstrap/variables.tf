variable "aws_region" {
  type        = string
  description = "AWS region for bootstrap resources."
  default     = "ap-south-1"
}

variable "github_repo" {
  type        = string
  description = "GitHub repository (owner/name) allowed to assume the deploy role from main."
  default     = "naveen95662/expense-tracker"
}
