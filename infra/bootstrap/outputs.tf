output "state_bucket_name" {
  description = "S3 bucket that will hold Terraform remote state."
  value       = aws_s3_bucket.tfstate.id
}

output "github_actions_role_arn" {
  description = "IAM role GitHub Actions on main can assume via OIDC."
  value       = aws_iam_role.github_actions_deploy.arn
}
