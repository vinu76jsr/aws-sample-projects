# AWS Config - Complete Guide

Track, audit, and evaluate your AWS resource configurations.

> **Note**: This is primarily an AWS Console service. No code required for basic usage.

## What is AWS Config?

AWS Config continuously monitors and records your AWS resource configurations, letting you:

```
┌─────────────────────────────────────────────────────────────┐
│                       AWS Config                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   1. RECORD         What resources exist and how they're    │
│                     configured (EC2, S3, IAM, etc.)         │
│                                                             │
│   2. EVALUATE       Are resources compliant with your       │
│                     rules? (e.g., "S3 must be encrypted")   │
│                                                             │
│   3. TRACK          What changed? When? Who changed it?     │
│                                                             │
│   4. REMEDIATE      Auto-fix non-compliant resources        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Why Use AWS Config?

| Question | AWS Config Answers |
|----------|-------------------|
| "What resources do I have?" | Resource inventory |
| "How is this resource configured?" | Configuration details |
| "Did someone change this?" | Change history |
| "Are we compliant?" | Rule evaluations |
| "What was the config last week?" | Point-in-time snapshots |

## Key Concepts

### 1. Configuration Items (CI)

A point-in-time snapshot of a resource's configuration:

```json
{
  "resourceType": "AWS::S3::Bucket",
  "resourceId": "my-bucket",
  "configuration": {
    "name": "my-bucket",
    "encryption": "AES256",
    "versioning": "Enabled",
    "publicAccess": "Blocked"
  },
  "captureTime": "2024-01-15T10:30:00Z"
}
```

### 2. Configuration Recorder

The component that records configuration items. You must enable this first.

### 3. Delivery Channel

Where Config sends configuration snapshots (S3 bucket).

### 4. Config Rules

Evaluate if resources are compliant:

```
Rule: s3-bucket-encryption-enabled
  │
  ├── my-bucket-1 → ✅ COMPLIANT (encrypted)
  ├── my-bucket-2 → ✅ COMPLIANT (encrypted)
  └── my-bucket-3 → ❌ NON_COMPLIANT (not encrypted)
```

### 5. Conformance Packs

Pre-packaged collections of rules for compliance frameworks (CIS, PCI-DSS, etc.).

## Getting Started (Console)

### Step 1: Enable AWS Config

1. Go to **AWS Console** → **Config**
2. Click **Get started** or **Settings**
3. Configure:
   - **Resource types**: Select "Record all resources" (recommended)
   - **S3 bucket**: Create new or select existing
   - **SNS topic**: Optional, for notifications
   - **IAM role**: Let AWS create one
4. Click **Confirm**

### Step 2: Wait for Discovery

- Initial recording takes 10-30 minutes
- Config discovers all existing resources
- Check **Resources** to see inventory

### Step 3: Add Your First Rule

1. Go to **Rules** → **Add rule**
2. Select **Add AWS managed rule**
3. Search for `s3-bucket-public-read-prohibited`
4. Click **Next** → **Add rule**
5. Wait for evaluation (few minutes)

## Exercise 1: Explore Resource Inventory

1. Go to **Resources** in left sidebar
2. Use filters:
   - Resource type: `AWS::EC2::Instance`
   - Resource type: `AWS::S3::Bucket`
3. Click any resource to see:
   - Current configuration (JSON)
   - Configuration timeline
   - Relationships

## Exercise 2: View Configuration Timeline

1. Go to **Resources**
2. Select any resource
3. Click **Resource Timeline**
4. See:
   - Configuration changes over time
   - Before/after comparisons
   - CloudTrail events (who made changes)

## Exercise 3: Add Essential Rules

Add these high-value managed rules:

| Rule Name | What It Checks |
|-----------|----------------|
| `s3-bucket-public-read-prohibited` | S3 buckets aren't publicly readable |
| `s3-bucket-ssl-requests-only` | S3 requires HTTPS |
| `encrypted-volumes` | EBS volumes are encrypted |
| `rds-instance-public-access-check` | RDS not publicly accessible |
| `root-account-mfa-enabled` | Root has MFA |
| `iam-password-policy` | Strong password policy |
| `vpc-flow-logs-enabled` | VPC flow logs on |
| `cloudtrail-enabled` | CloudTrail is on |

**To add:**
1. Rules → Add rule → Add AWS managed rule
2. Search for rule name
3. Configure scope (all resources or specific tags)
4. Save

## Exercise 4: Check Compliance Dashboard

1. Go to **Dashboard**
2. View:
   - Overall compliance percentage
   - Non-compliant resources count
   - Rules by compliance status
3. Click on non-compliant rules to see affected resources

## Exercise 5: Set Up Notifications

Get notified when resources become non-compliant:

1. Go to **Settings**
2. Under **Amazon SNS topic**, select or create a topic
3. Subscribe your email to the topic
4. You'll receive emails on configuration changes

## Exercise 6: Use Conformance Packs

Deploy a pre-built set of rules:

1. Go to **Conformance packs** → **Deploy**
2. Choose a template:
   - **Operational Best Practices for AWS Well-Architected Framework**
   - **Operational Best Practices for Amazon S3**
   - **Operational Best Practices for CIS AWS Foundations**
3. Deploy and monitor compliance

## Exercise 7: Query with Advanced Queries

Use SQL-like queries to search resources:

1. Go to **Advanced queries**
2. Try these queries:

**Find all public S3 buckets:**
```sql
SELECT
  resourceId,
  resourceType,
  configuration.publicAccessBlockConfiguration
WHERE
  resourceType = 'AWS::S3::Bucket'
```

**Find unencrypted EBS volumes:**
```sql
SELECT
  resourceId,
  configuration.encrypted
WHERE
  resourceType = 'AWS::EC2::Volume'
  AND configuration.encrypted = false
```

**Count resources by type:**
```sql
SELECT
  resourceType,
  COUNT(*)
WHERE
  resourceType LIKE 'AWS::EC2::%'
GROUP BY
  resourceType
```

## Exercise 8: Set Up Auto-Remediation

Automatically fix non-compliant resources:

1. Go to **Rules**
2. Select a rule (e.g., `s3-bucket-public-read-prohibited`)
3. Click **Actions** → **Manage remediation**
4. Choose remediation action:
   - **Automatic**: Fix immediately when detected
   - **Manual**: Require approval
5. Select an SSM Automation document (e.g., `AWS-DisableS3BucketPublicReadWrite`)
6. Save

## AWS CLI Commands

### Check Config Status
```bash
aws configservice describe-configuration-recorder-status
```

### List All Rules
```bash
aws configservice describe-config-rules \
  --query 'ConfigRules[*].[ConfigRuleName,ConfigRuleState]' \
  --output table
```

### Get Compliance Summary
```bash
aws configservice get-compliance-summary-by-config-rule
```

### Get Non-Compliant Resources for a Rule
```bash
aws configservice get-compliance-details-by-config-rule \
  --config-rule-name s3-bucket-public-read-prohibited \
  --compliance-types NON_COMPLIANT \
  --query 'EvaluationResults[*].EvaluationResultIdentifier.EvaluationResultQualifier'
```

### Run Advanced Query
```bash
aws configservice select-resource-config \
  --expression "SELECT resourceId, resourceType WHERE resourceType = 'AWS::S3::Bucket'"
```

## Custom Rules (Advanced)

Create your own compliance logic with Lambda:

### Example: Check EC2 Instances Have Tags

```python
import json
import boto3

def lambda_handler(event, context):
    config = boto3.client('config')

    # Get the resource configuration
    configuration_item = json.loads(event['invokingEvent'])['configurationItem']

    # Your custom logic
    tags = configuration_item.get('tags', {})
    required_tags = ['Environment', 'Owner', 'Project']

    missing_tags = [t for t in required_tags if t not in tags]

    if missing_tags:
        compliance = 'NON_COMPLIANT'
        annotation = f"Missing required tags: {missing_tags}"
    else:
        compliance = 'COMPLIANT'
        annotation = 'All required tags present'

    # Report back to Config
    config.put_evaluations(
        Evaluations=[{
            'ComplianceResourceType': configuration_item['resourceType'],
            'ComplianceResourceId': configuration_item['resourceId'],
            'ComplianceType': compliance,
            'Annotation': annotation,
            'OrderingTimestamp': configuration_item['configurationItemCaptureTime']
        }],
        ResultToken=event['resultToken']
    )
```

## Pricing

| Item | Cost |
|------|------|
| Configuration items recorded | $0.003 per item |
| Config rule evaluations | $0.001 per evaluation |
| Conformance pack evaluations | $0.001 per evaluation per rule |
| Advanced queries | $0.003 per query |

**Example**: 100 resources × 10 rules × 30 days = ~$30/month

## Best Practices

1. **Start with managed rules** - AWS maintains 300+ pre-built rules
2. **Enable on all regions** - Resources can be created anywhere
3. **Use conformance packs** - Easier than individual rules
4. **Set up remediation** - Auto-fix common issues
5. **Export to S3** - Long-term analysis and compliance audits
6. **Use aggregators** - Multi-account visibility
7. **Integrate with Security Hub** - Centralized security view

## Config vs CloudTrail

| | AWS Config | CloudTrail |
|---|-----------|------------|
| **Records** | Resource configurations | API calls |
| **Answers** | "What is the current state?" | "Who did what?" |
| **Use for** | Compliance, inventory | Auditing, forensics |
| **Example** | "Is encryption enabled?" | "Who disabled encryption?" |

Use both together for complete visibility.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Resources not appearing | Wait 30 min, check recorder is running |
| Rules stuck in "Evaluating" | Check Lambda permissions for custom rules |
| No compliance data | Verify delivery channel has S3 permissions |
| High costs | Reduce rule evaluation frequency |

## Related Services

| Service | Relationship |
|---------|--------------|
| **Security Hub** | Receives Config compliance findings |
| **CloudTrail** | Shows who made configuration changes |
| **Systems Manager** | Remediation automation |
| **Organizations** | Multi-account Config aggregation |
