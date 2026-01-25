# CloudWatch Dashboard for Shield and NLB metrics
resource "aws_cloudwatch_dashboard" "shield" {
  dashboard_name = "${var.project_name}-shield-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "text"
        x      = 0
        y      = 0
        width  = 24
        height = 1
        properties = {
          markdown = "# AWS Shield Layer 4 Protection Dashboard"
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 1
        width  = 12
        height = 6
        properties = {
          title  = "NLB - Active Flow Count"
          region = var.aws_region
          metrics = [
            ["AWS/NetworkELB", "ActiveFlowCount", "LoadBalancer", aws_lb.network.arn_suffix]
          ]
          period = 60
          stat   = "Average"
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 1
        width  = 12
        height = 6
        properties = {
          title  = "NLB - New Flow Count"
          region = var.aws_region
          metrics = [
            ["AWS/NetworkELB", "NewFlowCount", "LoadBalancer", aws_lb.network.arn_suffix]
          ]
          period = 60
          stat   = "Sum"
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 7
        width  = 12
        height = 6
        properties = {
          title  = "NLB - Processed Bytes"
          region = var.aws_region
          metrics = [
            ["AWS/NetworkELB", "ProcessedBytes", "LoadBalancer", aws_lb.network.arn_suffix]
          ]
          period = 60
          stat   = "Sum"
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 7
        width  = 12
        height = 6
        properties = {
          title  = "NLB - TCP Client Reset Count"
          region = var.aws_region
          metrics = [
            ["AWS/NetworkELB", "TCP_Client_Reset_Count", "LoadBalancer", aws_lb.network.arn_suffix]
          ]
          period = 60
          stat   = "Sum"
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 13
        width  = 12
        height = 6
        properties = {
          title  = "EC2 - Network In (bytes)"
          region = var.aws_region
          metrics = [
            ["AWS/EC2", "NetworkIn", "AutoScalingGroupName", aws_autoscaling_group.app.name]
          ]
          period = 60
          stat   = "Sum"
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 13
        width  = 12
        height = 6
        properties = {
          title  = "EC2 - Network Out (bytes)"
          region = var.aws_region
          metrics = [
            ["AWS/EC2", "NetworkOut", "AutoScalingGroupName", aws_autoscaling_group.app.name]
          ]
          period = 60
          stat   = "Sum"
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 19
        width  = 24
        height = 6
        properties = {
          title  = "Target Group - Healthy/Unhealthy Hosts"
          region = var.aws_region
          metrics = [
            ["AWS/NetworkELB", "HealthyHostCount", "TargetGroup", aws_lb_target_group.tcp.arn_suffix, "LoadBalancer", aws_lb.network.arn_suffix],
            [".", "UnHealthyHostCount", ".", ".", ".", "."]
          ]
          period = 60
          stat   = "Average"
        }
      }
    ]
  })
}

# SNS Topic for Shield Alerts
resource "aws_sns_topic" "shield_alerts" {
  name = "${var.project_name}-shield-alerts"

  tags = {
    Name = "${var.project_name}-shield-alerts"
  }
}

# CloudWatch Alarm for DDoS detection (high new connection rate)
resource "aws_cloudwatch_metric_alarm" "ddos_new_flows" {
  alarm_name          = "${var.project_name}-ddos-high-new-flows"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "NewFlowCount"
  namespace           = "AWS/NetworkELB"
  period              = 60
  statistic           = "Sum"
  threshold           = 10000
  alarm_description   = "Potential DDoS - High number of new connections"
  alarm_actions       = [aws_sns_topic.shield_alerts.arn]
  ok_actions          = [aws_sns_topic.shield_alerts.arn]

  dimensions = {
    LoadBalancer = aws_lb.network.arn_suffix
  }

  tags = {
    Name = "${var.project_name}-ddos-alarm"
  }
}

# CloudWatch Alarm for high TCP reset count (potential SYN flood)
resource "aws_cloudwatch_metric_alarm" "tcp_resets" {
  alarm_name          = "${var.project_name}-high-tcp-resets"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "TCP_Client_Reset_Count"
  namespace           = "AWS/NetworkELB"
  period              = 60
  statistic           = "Sum"
  threshold           = 1000
  alarm_description   = "High TCP reset count - potential SYN flood attack"
  alarm_actions       = [aws_sns_topic.shield_alerts.arn]
  ok_actions          = [aws_sns_topic.shield_alerts.arn]

  dimensions = {
    LoadBalancer = aws_lb.network.arn_suffix
  }

  tags = {
    Name = "${var.project_name}-tcp-reset-alarm"
  }
}
