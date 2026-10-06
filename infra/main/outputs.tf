# Values other stacks (and you) will need after apply.
output "dynamodb_table_name" {
  description = "DynamoDB table for expenses."
  value       = aws_dynamodb_table.expenses.name
}

output "ecr_repository_url" {
  description = "ECR repository URL for the API image."
  value       = aws_ecr_repository.expense_tracker.repository_url
}

output "log_group_name" {
  description = "CloudWatch log group for the ECS service."
  value       = aws_cloudwatch_log_group.ecs.name
}

output "ecs_execution_role_arn" {
  description = "IAM role ECS uses to pull images and write logs."
  value       = aws_iam_role.ecs_execution.arn
}

output "ecs_task_role_arn" {
  description = "IAM role the running app uses to access DynamoDB."
  value       = aws_iam_role.ecs_task.arn
}
