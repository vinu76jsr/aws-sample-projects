variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name prefix for all resources"
  type        = string
  default     = "shield-demo"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "enable_shield_advanced" {
  description = "Enable AWS Shield Advanced (requires subscription, additional cost)"
  type        = bool
  default     = false
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "demo"
}
