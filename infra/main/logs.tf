# ECS app logs; retain 7 days.
resource "aws_cloudwatch_log_group" "ecs" {
  name              = "/ecs/expense-tracker"
  retention_in_days = 7
}
