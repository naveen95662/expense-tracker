# Container image repo; scan on push; keep only the last 5 images.
resource "aws_ecr_repository" "expense_tracker" {
  name         = "expense-tracker"
  force_delete = true

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_lifecycle_policy" "expense_tracker" {
  repository = aws_ecr_repository.expense_tracker.name

  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Keep only the last 5 images"
      selection = {
        tagStatus   = "any"
        countType   = "imageCountMoreThan"
        countNumber = 5
      }
      action = { type = "expire" }
    }]
  })
}
