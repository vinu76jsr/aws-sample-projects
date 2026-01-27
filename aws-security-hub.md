# AWS Security Hub

A central dashboard to view and manage security alerts across your AWS accounts.

> **Note**: This is primarily an AWS Console service. No code required.

## What is Security Hub?

Security Hub aggregates security findings from multiple AWS services and third-party tools into one place:

```
┌─────────────────────────────────────────────────────────────┐
│                     AWS Security Hub                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   GuardDuty ──────┐                                         │
│   Inspector ──────┼──→ Centralized Dashboard ──→ You        │
│   Macie ──────────┤         │                               │
│   Firewall Mgr ───┤         ↓                               │
│   IAM Analyzer ───┤    Compliance Scores                    │
│   Config ─────────┤    Security Standards                   │
│   3rd Party ──────┘    Automated Checks                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Why Use Security Hub?

| Without Security Hub | With Security Hub |
|---------------------|-------------------|
| Check 6+ consoles separately | One dashboard |
| Manual compliance tracking | Automated scoring |
| No prioritization | Severity-based sorting |
| Siloed findings | Correlated insights |

## Getting Started (Console)

### Step 1: Enable Security Hub

1. Go to **AWS Console** → **Security Hub**
2. Click **Go to Security Hub**
3. Select security standards to enable:
   - ✅ AWS Foundational Security Best Practices (recommended)
   - ✅ CIS AWS Foundations Benchmark (if needed)
   - ✅ PCI DSS (if processing payments)
4. Click **Enable Security Hub**

### Step 2: Wait for Initial Scan

- First scan takes ~30 minutes to 2 hours
- Security Hub will automatically check your resources
- Findings will start appearing in the dashboard

### Step 3: Explore the Dashboard

Navigate the left sidebar:

| Section | What it shows |
|---------|---------------|
| **Summary** | Overview, severity breakdown, trends |
| **Findings** | All security issues found |
| **Insights** | Pre-built queries (e.g., "S3 buckets with public access") |
| **Security standards** | Compliance scores per framework |
| **Integrations** | Connected AWS services |

## Understanding Findings

Each finding has:

```
┌────────────────────────────────────────────────────────┐
│ Title: S3 bucket has public read access                │
├────────────────────────────────────────────────────────┤
│ Severity: HIGH (score: 70)                             │
│ Resource: arn:aws:s3:::my-bucket                       │
│ Account: 123456789012                                  │
│ Region: us-east-1                                      │
│ Source: AWS Config                                     │
│ Status: ACTIVE                                         │
│ Remediation: Remove public access policy               │
└────────────────────────────────────────────────────────┘
```

### Severity Levels

| Severity | Score | Action |
|----------|-------|--------|
| CRITICAL | 90-100 | Fix immediately |
| HIGH | 70-89 | Fix within 24 hours |
| MEDIUM | 40-69 | Fix within 1 week |
| LOW | 1-39 | Fix when possible |
| INFORMATIONAL | 0 | Review only |

## Exercise 1: Review Security Score

1. Go to **Security standards**
2. Click **AWS Foundational Security Best Practices**
3. Review your score (aim for 80%+)
4. Click **View results** to see failed checks

## Exercise 2: Investigate a Finding

1. Go to **Findings**
2. Filter by `Severity = CRITICAL or HIGH`
3. Click any finding
4. Review:
   - What's wrong
   - Which resource
   - Remediation steps
5. Click **Workflow status** → Set to "INVESTIGATING"

## Exercise 3: Use Insights

1. Go to **Insights**
2. Try these built-in insights:
   - "AWS resources with the most findings"
   - "S3 buckets with public access"
   - "EC2 instances with public IP addresses"
3. Click an insight to see matching findings

## Exercise 4: Suppress a Finding

If a finding is a false positive or accepted risk:

1. Select the finding
2. Click **Workflow status**
3. Choose **SUPPRESSED**
4. Add a note explaining why

## Exercise 5: Set Up Notifications

Get alerted on new critical findings:

1. Go to **Settings** → **Custom actions**
2. Create a custom action
3. Set up EventBridge rule:
   ```
   Security Hub → EventBridge → SNS → Email
   ```

Or use CloudWatch Events:
```json
{
  "source": ["aws.securityhub"],
  "detail-type": ["Security Hub Findings - Imported"],
  "detail": {
    "findings": {
      "Severity": {
        "Label": ["CRITICAL", "HIGH"]
      }
    }
  }
}
```

## Security Standards Comparison

| Standard | Focus | Best For |
|----------|-------|----------|
| **AWS Foundational Security Best Practices** | AWS-specific best practices | Everyone (start here) |
| **CIS AWS Foundations Benchmark** | Industry security baseline | Compliance-focused orgs |
| **PCI DSS** | Payment card security | E-commerce, payments |
| **NIST 800-53** | US government standard | Government contractors |

## Integrations

### AWS Services (Automatic)

These send findings automatically when enabled:

| Service | What it detects |
|---------|-----------------|
| **GuardDuty** | Threats, compromised credentials |
| **Inspector** | Vulnerabilities in EC2/containers |
| **Macie** | Sensitive data in S3 |
| **IAM Access Analyzer** | External access to resources |
| **Firewall Manager** | WAF/Shield compliance |
| **AWS Config** | Resource configuration issues |

### Third-Party Tools

Security Hub integrates with 50+ partners:
- Splunk, Sumo Logic (SIEM)
- Palo Alto, CrowdStrike (security)
- Jira, ServiceNow (ticketing)

## Multi-Account Setup

For organizations:

1. **Designate admin account** in AWS Organizations
2. **Enable Security Hub** in admin account
3. **Add member accounts**:
   - Settings → Accounts → Add accounts
   - Or use AWS Organizations integration
4. **View aggregated findings** across all accounts

## Automation with AWS CLI

### List High Severity Findings
```bash
aws securityhub get-findings \
  --filters '{"SeverityLabel": [{"Value": "HIGH", "Comparison": "EQUALS"}]}' \
  --query 'Findings[*].[Title,Resources[0].Id]' \
  --output table
```

### Get Security Score
```bash
aws securityhub get-enabled-standards \
  --query 'StandardsSubscriptions[*].[StandardsArn]' \
  --output table
```

### Batch Update Findings
```bash
aws securityhub batch-update-findings \
  --finding-identifiers '[{"Id": "finding-id", "ProductArn": "arn"}]' \
  --workflow '{"Status": "RESOLVED"}'
```

## Pricing

| Item | Cost |
|------|------|
| Security checks | $0.0010 per check/account/region |
| Finding ingestion events | $0.00003 per event |
| First 10,000 checks/month | Free |

Typical cost: $5-50/month per account depending on resources.

## Best Practices

1. **Enable AWS Foundational standard first** - Best coverage for AWS
2. **Start with one region** - Expand after initial cleanup
3. **Fix CRITICAL findings immediately** - They're exploitable
4. **Set up notifications** - Don't rely on checking the console
5. **Review weekly** - Security is ongoing
6. **Use multi-account** - Aggregate findings centrally
7. **Automate remediation** - Use Lambda for common fixes

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No findings appearing | Wait 2 hours, check service integrations |
| Score not updating | Findings refresh every 12-24 hours |
| Missing resources | Check if Config is enabled |
| Integration not working | Verify IAM permissions |

## Related Services

| Service | Relationship |
|---------|--------------|
| **AWS Config** | Feeds findings to Security Hub |
| **GuardDuty** | Threat detection → Security Hub |
| **Detective** | Investigate findings from Security Hub |
| **Systems Manager** | Remediate findings |
