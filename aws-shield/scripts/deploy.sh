#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$SCRIPT_DIR/../terraform"

echo "=== AWS Shield Layer 4 Protection Deployment ==="
echo ""

cd "$TERRAFORM_DIR"

# Check if terraform is installed
if ! command -v terraform &> /dev/null; then
    echo "Error: Terraform is not installed"
    exit 1
fi

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "Error: AWS credentials not configured"
    echo "Run: aws configure"
    exit 1
fi

echo "Current AWS Identity:"
aws sts get-caller-identity --query 'Arn' --output text
echo ""

# Initialize Terraform
echo "Initializing Terraform..."
terraform init

# Create tfvars if not exists
if [ ! -f terraform.tfvars ]; then
    echo "Creating terraform.tfvars from example..."
    cp terraform.tfvars.example terraform.tfvars
fi

# Plan
echo ""
echo "Planning deployment..."
terraform plan -out=tfplan

# Confirm deployment
echo ""
read -p "Do you want to apply this plan? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Deploying..."
    terraform apply tfplan

    echo ""
    echo "=== Deployment Complete ==="
    echo ""
    echo "NLB DNS: $(terraform output -raw nlb_dns_name)"
    echo ""
    echo "Test with: curl http://$(terraform output -raw nlb_dns_name)"
    echo ""
    echo "Dashboard: $(terraform output -raw dashboard_url)"
else
    echo "Deployment cancelled"
fi
