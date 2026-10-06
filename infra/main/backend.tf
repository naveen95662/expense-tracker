# Remote state in S3. Bucket name is passed at init via -backend-config.
terraform {
  backend "s3" {
    key          = "expense-tracker/main.tfstate"
    region       = "ap-south-1"
    use_lockfile = true
    encrypt      = true
  }
}
