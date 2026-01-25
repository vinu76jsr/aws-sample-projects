# AWS Config - Resource Configuration Tracking

AWS Config continuously monitors and records AWS resource configurations and evaluates them against desired configurations.

## Using AWS Console

1. Go to [AWS Config Console](https://console.aws.amazon.com/config)
2. Click **Get started** (first time) or **Settings**
3. Select resource types to record (or all resources)
4. Choose an S3 bucket for configuration snapshots
5. Click **Confirm**

## Key Concepts

| Concept | Description |
|---------|-------------|
| Configuration Item | Point-in-time record of a resource's configuration |
| Configuration Recorder | Records configurations of supported resources |
| Delivery Channel | S3 bucket where Config sends configuration data |
| Config Rules | Evaluates if resources comply with desired configurations |

## Exercise 1: Enable AWS Config

1. Go to **Settings** → **Edit**
2. Enable recording for **All resources**
3. Create or select an S3 bucket
4. Optionally enable SNS notifications
5. Save

## Exercise 2: View Resource Inventory

1. Go to **Resources** in the left sidebar
2. Filter by resource type (e.g., EC2 instances, S3 buckets)
3. Click a resource to see:
   - Current configuration
   - Configuration timeline
   - Relationships to other resources

## Exercise 3: Add a Managed Rule

AWS provides pre-built rules for common compliance checks.

1. Go to **Rules** → **Add rule**
2. Select **Add AWS managed rule**
3. Try these starter rules:

| Rule | What it checks |
|------|----------------|
| `s3-bucket-public-read-prohibited` | S3 buckets aren't publicly readable |
| `ec2-instance-no-public-ip` | EC2 instances don't have public IPs |
| `rds-instance-public-access-check` | RDS instances aren't publicly accessible |
| `root-account-mfa-enabled` | Root account has MFA enabled |

4. Configure scope (all resources or specific tags)
5. Click **Save**

## Exercise 4: Check Compliance

1. Go to **Rules**
2. View compliance status for each rule:
   - ✅ **Compliant** - Resources meet the rule
   - ❌ **Noncompliant** - Resources violate the rule
3. Click a rule to see which specific resources are noncompliant
4. Click a resource to see why it failed

## Exercise 5: View Configuration History

1. Go to **Resources**
2. Select any resource
3. Click **Configuration timeline**
4. See changes over time:
   - What changed
   - When it changed
   - Before/after comparison

## Exercise 6: Create a Custom Rule (Advanced)

Using Lambda for custom compliance logic:

1. Go to **Rules** → **Add rule**
2. Select **Create custom Lambda rule**
3. Create a Lambda function that returns:
   ```json
   {
     "compliance_type": "COMPLIANT" | "NON_COMPLIANT",
     "annotation": "Reason for the status"
   }
   ```
4. Link the Lambda function to the rule
5. Set trigger type (configuration changes or periodic)

## Conformance Packs

Pre-packaged collections of rules for common frameworks:

1. Go to **Conformance packs** → **Deploy**
2. Choose a template:
   - Operational Best Practices for AWS Identity and Access Management
   - Operational Best Practices for Amazon S3
   - Operational Best Practices for CIS AWS Foundations Benchmark
3. Deploy and monitor compliance

## Pricing

- **Configuration items recorded**: $0.003 per item
- **Config rule evaluations**: $0.001 per evaluation
- **Conformance pack evaluations**: $0.001 per evaluation
- Free tier: None

## Tips

- Start with a few critical rules, not everything at once
- Use resource tags to scope rules to specific environments
- Set up SNS notifications for compliance changes
- Export configuration data to S3 for long-term analysis
