# =============================================================================
# AWS Shield Configuration
# =============================================================================
#
# AWS Shield Standard:
# - Automatically included at no extra cost
# - Protects against most common Layer 3/4 DDoS attacks
# - Automatically applied to ELB, CloudFront, Route 53, Global Accelerator
#
# AWS Shield Advanced:
# - Requires subscription ($3,000/month + data transfer fees)
# - Enhanced DDoS protection with 24/7 DRT support
# - Cost protection for scaling during attacks
# - Advanced metrics and reporting
# =============================================================================

# Shield Advanced Protection for NLB (only if Shield Advanced is enabled)
resource "aws_shield_protection" "nlb" {
  count        = var.enable_shield_advanced ? 1 : 0
  name         = "${var.project_name}-nlb-protection"
  resource_arn = aws_lb.network.arn

  tags = {
    Name = "${var.project_name}-nlb-shield"
  }
}

# Shield Advanced Protection for Elastic IP (NAT Gateway)
resource "aws_shield_protection" "eip" {
  count        = var.enable_shield_advanced ? 1 : 0
  name         = "${var.project_name}-eip-protection"
  resource_arn = "arn:aws:ec2:${var.aws_region}:${data.aws_caller_identity.current.account_id}:eip-allocation/${aws_eip.nat.id}"

  tags = {
    Name = "${var.project_name}-eip-shield"
  }
}

# Shield Advanced Protection Group (groups multiple protected resources)
resource "aws_shield_protection_group" "main" {
  count                = var.enable_shield_advanced ? 1 : 0
  protection_group_id  = "${var.project_name}-protection-group"
  aggregation          = "SUM"
  pattern              = "BY_RESOURCE_TYPE"
  resource_type        = "ELASTIC_IP_ALLOCATION"

  tags = {
    Name = "${var.project_name}-protection-group"
  }

  depends_on = [
    aws_shield_protection.nlb,
    aws_shield_protection.eip
  ]
}

# Alternative: Protection group for all resources
resource "aws_shield_protection_group" "all_resources" {
  count                = var.enable_shield_advanced ? 1 : 0
  protection_group_id  = "${var.project_name}-all-resources"
  aggregation          = "MAX"
  pattern              = "ALL"

  tags = {
    Name = "${var.project_name}-all-protection-group"
  }

  depends_on = [
    aws_shield_protection.nlb,
    aws_shield_protection.eip
  ]
}
