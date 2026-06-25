output "ecr_repository_url" {
  description = "URL du repository ECR"
  value       = aws_ecr_repository.app.repository_url
}

output "ecs_cluster_name" {
  description = "Nom du cluster ECS"
  value       = aws_ecs_cluster.main.name
}

output "cloudwatch_log_group" {
  description = "Groupe de logs CloudWatch"
  value       = aws_cloudwatch_log_group.app.name
}

output "sns_topic_arn" {
  description = "ARN du topic SNS"
  value       = aws_sns_topic.alerts.arn
}