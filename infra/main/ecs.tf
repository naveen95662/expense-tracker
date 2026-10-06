# Fargate cluster that will host the expense API (no load balancer).
resource "aws_ecs_cluster" "expense_tracker" {
  name = "expense-tracker"
}

# How to run one app container on Fargate. desired_count on the service controls whether any run.
resource "aws_ecs_task_definition" "app" {
  family                   = "expense-tracker"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }

  container_definitions = jsonencode([
    {
      name  = "app"
      image = "${aws_ecr_repository.expense_tracker.repository_url}:${var.image_tag}"
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
          protocol      = "tcp"
        }
      ]
      environment = [
        { name = "STORE_BACKEND", value = "dynamodb" },
        { name = "TABLE_NAME", value = aws_dynamodb_table.expenses.name },
        { name = "AWS_REGION", value = var.aws_region }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "app"
        }
      }
    }
  ])
}

# Service with desired_count 0 by default: definition is ready, but no tasks (and no ALB).
resource "aws_ecs_service" "app" {
  name            = "expense-tracker"
  cluster         = aws_ecs_cluster.expense_tracker.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = data.aws_subnets.default.ids
    security_groups  = [aws_security_group.app.id]
    assign_public_ip = true
  }
}
