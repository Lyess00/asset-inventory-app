# SNS Topic pour les alertes
resource "aws_sns_topic" "alerts" {
  name = "${var.app_name}-alerts"
}

resource "aws_sns_topic_subscription" "email" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = "Lyess_boufaden@yahoo.com"
}

# Alarme sur les erreurs 5xx
resource "aws_cloudwatch_metric_alarm" "errors_5xx" {
  alarm_name          = "${var.app_name}-5xx-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Sum"
  threshold           = 5
  alarm_description   = "Trop d'erreurs 5xx sur le Load Balancer"
  treat_missing_data  = "notBreaching"
  dimensions = {
    LoadBalancer = aws_lb.main.arn_suffix
  }
  alarm_actions = [aws_sns_topic.alerts.arn]
  ok_actions    = [aws_sns_topic.alerts.arn]
}

# Alarme sur l'arrêt des tâches ECS
resource "aws_cloudwatch_metric_alarm" "ecs_no_tasks" {
  alarm_name          = "${var.app_name}-no-running-tasks"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 1
  metric_name         = "RunningTaskCount"
  namespace           = "ECS/ContainerInsights"
  period              = 60
  statistic           = "Average"
  threshold           = 1
  alarm_description   = "Aucune tâche ECS en cours d'exécution"
  treat_missing_data  = "breaching"
  dimensions = {
    ClusterName = aws_ecs_cluster.main.name
    ServiceName = aws_ecs_service.app.name
  }
  alarm_actions = [aws_sns_topic.alerts.arn]
  ok_actions    = [aws_sns_topic.alerts.arn]
}

# Dashboard CloudWatch
resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = var.app_name
  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        properties = {
          title  = "Requêtes par minute"
          region = var.aws_region
          period = 60
          stat   = "Sum"
          metrics = [
            ["AWS/ApplicationELB", "RequestCount",
             "LoadBalancer", aws_lb.main.arn_suffix]
          ]
        }
      },
      {
        type = "metric"
        properties = {
          title  = "Latence moyenne (ms)"
          region = var.aws_region
          period = 60
          stat   = "Average"
          metrics = [
            ["AWS/ApplicationELB", "TargetResponseTime",
             "LoadBalancer", aws_lb.main.arn_suffix]
          ]
        }
      },
      {
        type = "metric"
        properties = {
          title  = "Erreurs 5xx"
          region = var.aws_region
          period = 60
          stat   = "Sum"
          metrics = [
            ["AWS/ApplicationELB", "HTTPCode_Target_5XX_Count",
             "LoadBalancer", aws_lb.main.arn_suffix]
          ]
        }
      },
      {
        type = "metric"
        properties = {
          title  = "Tâches ECS en cours"
          region = var.aws_region
          period = 60
          stat   = "Average"
          metrics = [
            ["ECS/ContainerInsights", "RunningTaskCount",
             "ClusterName", aws_ecs_cluster.main.name,
             "ServiceName", aws_ecs_service.app.name]
          ]
        }
      }
    ]
  })
}