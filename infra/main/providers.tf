# AWS provider: refuse the wrong account; tag everything like bootstrap.
provider "aws" {
  region              = var.aws_region
  allowed_account_ids = [var.allowed_account_id]

  default_tags {
    tags = {
      Project   = "expense-tracker"
      ManagedBy = "terraform"
    }
  }
}
