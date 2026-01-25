# =============================================================================
# Outputs
# =============================================================================

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "nlb_dns_name" {
  description = "Network Load Balancer DNS name (Layer 4 endpoint)"
  value       = aws_lb.network.dns_name
}

output "nlb_arn" {
  description = "Network Load Balancer ARN"
  value       = aws_lb.network.arn
}

output "nlb_zone_id" {
  description = "Network Load Balancer Zone ID (for Route 53)"
  value       = aws_lb.network.zone_id
}

output "shield_standard_status" {
  description = "AWS Shield Standard protection status"
  value       = "ACTIVE - Automatically enabled for ELB, CloudFront, Route 53"
}

output "shield_advanced_status" {
  description = "AWS Shield Advanced protection status"
  value       = var.enable_shield_advanced ? "ENABLED" : "DISABLED (set enable_shield_advanced=true to enable)"
}

output "dashboard_url" {
  description = "CloudWatch Dashboard URL"
  value       = "https://${var.aws_region}.console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:name=${var.project_name}-shield-dashboard"
}

output "test_endpoint" {
  description = "Test the deployment"
  value       = "curl http://${aws_lb.network.dns_name}"
}

output "protected_resources" {
  description = "Resources protected by AWS Shield"
  value = {
    nlb     = aws_lb.network.dns_name
    eip     = aws_eip.nat.public_ip
    subnets = aws_subnet.public[*].id
  }
}

output "sns_topic_arn" {
  description = "SNS Topic ARN for Shield alerts"
  value       = aws_sns_topic.shield_alerts.arn
}
