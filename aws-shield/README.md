# AWS Shield Layer 4 Protection Sample Project

This project demonstrates AWS Shield DDoS protection at Layer 4 (Network/Transport layer) using a Network Load Balancer (NLB) setup.

## Architecture

```
                                    ┌─────────────────────────────────────┐
                                    │         AWS Shield Standard         │
                                    │    (Automatic L3/L4 Protection)     │
                                    └─────────────────────────────────────┘
                                                     │
                    Internet                         ▼
                        │              ┌─────────────────────────┐
                        │              │   Network Load Balancer │
                        └─────────────►│       (Layer 4)         │
                                       │   TCP/UDP Traffic       │
                                       └───────────┬─────────────┘
                                                   │
                         ┌─────────────────────────┼─────────────────────────┐
                         │                         │                         │
                         ▼                         ▼                         ▼
              ┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
              │   EC2 Instance   │     │   EC2 Instance   │     │   EC2 Instance   │
              │   (Web Server)   │     │   (Web Server)   │     │   (Auto Scaled)  │
              └──────────────────┘     └──────────────────┘     └──────────────────┘
                         │                         │                         │
                         └─────────────────────────┴─────────────────────────┘
                                                   │
                                          Private Subnets
```

## AWS Shield Overview

### Shield Standard (Included - No Extra Cost)
- Automatically enabled for all AWS customers
- Protects against most common Layer 3/4 DDoS attacks:
  - SYN/UDP floods
  - Reflection attacks
  - Other common infrastructure attacks
- Applied to: ELB, CloudFront, Route 53, Global Accelerator

### Shield Advanced (Optional - $3,000/month)
- Enhanced DDoS protection
- 24/7 DDoS Response Team (DRT) support
- Cost protection for scaling during attacks
- Advanced metrics and attack visibility
- Application layer (Layer 7) protection when combined with AWS WAF

## Layer 4 Protection Details

Layer 4 operates at the Transport layer (TCP/UDP) and protects against:

| Attack Type | Description | Shield Standard | Shield Advanced |
|------------|-------------|-----------------|-----------------|
| SYN Flood | Exhausts connection state tables | ✓ | ✓ Enhanced |
| UDP Flood | Volumetric UDP packet flood | ✓ | ✓ Enhanced |
| TCP Reset | Malicious connection resets | ✓ | ✓ Enhanced |
| Reflection | Amplification attacks (DNS, NTP) | ✓ | ✓ Enhanced |

## Prerequisites

- AWS CLI configured with appropriate credentials
- Terraform >= 1.0
- An AWS account with permissions to create VPC, EC2, ELB resources

## Quick Start

```bash
# Navigate to terraform directory
cd terraform

# Copy and customize variables
cp terraform.tfvars.example terraform.tfvars

# Initialize Terraform
terraform init

# Preview changes
terraform plan

# Deploy infrastructure
terraform apply

# Test the deployment
curl http://$(terraform output -raw nlb_dns_name)
```

## Configuration

Edit `terraform.tfvars` to customize:

```hcl
aws_region             = "us-east-1"
project_name           = "my-shield-demo"
vpc_cidr               = "10.0.0.0/16"
enable_shield_advanced = false  # Set to true for enhanced protection
```

## Resources Created

| Resource | Purpose |
|----------|---------|
| VPC | Isolated network environment |
| Network Load Balancer | Layer 4 load balancing with Shield protection |
| Auto Scaling Group | Automatic scaling during traffic spikes |
| CloudWatch Dashboard | Monitoring and visibility |
| CloudWatch Alarms | DDoS detection alerts |
| SNS Topic | Alert notifications |

## Monitoring

After deployment, access the CloudWatch dashboard:

```bash
# Get dashboard URL
terraform output dashboard_url
```

Key metrics monitored:
- **NewFlowCount**: New TCP connections per minute
- **ActiveFlowCount**: Current active connections
- **TCP_Client_Reset_Count**: Abnormal connection terminations
- **ProcessedBytes**: Total data processed

## Alerts

The project creates CloudWatch alarms for:

1. **High New Flow Count** (>10,000/min) - Potential connection flood
2. **High TCP Resets** (>1,000/min) - Potential SYN flood attack

Subscribe to the SNS topic for notifications:

```bash
aws sns subscribe \
  --topic-arn $(terraform output -raw sns_topic_arn) \
  --protocol email \
  --notification-endpoint your@email.com
```

## Testing Layer 4 Protection

**Note**: Only test against your own infrastructure with proper authorization.

```bash
# Get the NLB endpoint
NLB_DNS=$(terraform output -raw nlb_dns_name)

# Normal traffic test
curl http://$NLB_DNS

# Check health endpoint
curl -I http://$NLB_DNS

# Monitor in real-time (separate terminal)
watch -n 5 "aws cloudwatch get-metric-statistics \
  --namespace AWS/NetworkELB \
  --metric-name NewFlowCount \
  --dimensions Name=LoadBalancer,Value=$(terraform output -raw nlb_arn | cut -d: -f6 | cut -d/ -f2-) \
  --start-time \$(date -u -d '5 minutes ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time \$(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 60 \
  --statistics Sum"
```

## Cleanup

```bash
terraform destroy
```

## Cost Estimation

| Component | Estimated Cost |
|-----------|---------------|
| Shield Standard | Free |
| Shield Advanced | $3,000/month |
| NLB | ~$20/month + data |
| EC2 (2x t3.micro) | ~$15/month |
| NAT Gateway | ~$32/month + data |
| **Total (Standard)** | **~$67/month** |
| **Total (Advanced)** | **~$3,067/month** |

## Best Practices

1. **Use Elastic IPs** - Provides stable addresses for whitelisting
2. **Enable VPC Flow Logs** - For forensic analysis
3. **Set up CloudWatch Alarms** - Early detection of anomalies
4. **Use Auto Scaling** - Absorb traffic spikes
5. **Consider Shield Advanced** - For production workloads with strict SLAs

## Additional Resources

- [AWS Shield Documentation](https://docs.aws.amazon.com/waf/latest/developerguide/shield-chapter.html)
- [DDoS Best Practices Whitepaper](https://docs.aws.amazon.com/whitepapers/latest/aws-best-practices-ddos-resiliency/welcome.html)
- [AWS Shield Pricing](https://aws.amazon.com/shield/pricing/)
