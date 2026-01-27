# AWS Landing Zone

A solution for setting up a secure, multi-account AWS environment based on best practices.

## The Problem It Solves

When organizations scale on AWS, they need:
- Multiple accounts (dev, staging, prod, security, logging, etc.)
- Consistent security baselines across all accounts
- Centralized logging and auditing
- Guardrails to prevent misconfigurations

Setting this up manually is complex and error-prone.

## What Landing Zone Provides

| Component | Purpose |
|-----------|---------|
| **Account Vending** | Automated creation of new accounts with baseline configs |
| **Multi-account structure** | Organizes accounts using AWS Organizations |
| **Centralized logging** | All CloudTrail/Config logs go to a dedicated account |
| **Security baseline** | IAM roles, SCPs, GuardDuty enabled by default |
| **Network architecture** | Shared VPCs, transit gateway patterns |

## Landing Zone vs Control Tower

| | Landing Zone (Legacy) | Control Tower (Current) |
|---|----------------------|------------------------|
| **Type** | Self-managed solution | Managed AWS service |
| **Setup** | Deploy via CloudFormation/CDK | Console wizard |
| **Maintenance** | You manage updates | AWS manages |
| **Status** | Deprecated | Recommended |

**Use AWS Control Tower today** - it's the managed successor that does the same thing with less operational overhead.

## Typical Multi-Account Structure

```
Organization Root
├── Security OU
│   ├── Log Archive Account     (centralized logs)
│   └── Security Account        (GuardDuty, Security Hub)
├── Infrastructure OU
│   └── Shared Services Account (DNS, AD, CI/CD)
└── Workloads OU
    ├── Dev Account
    ├── Staging Account
    └── Production Account
```

## Core Components

### 1. AWS Organizations
- Groups accounts into Organizational Units (OUs)
- Applies Service Control Policies (SCPs) for guardrails
- Consolidated billing

### 2. Account Baseline
Each new account automatically gets:
- CloudTrail enabled (logs to central account)
- AWS Config enabled (logs to central account)
- IAM roles for cross-account access
- VPC with standard CIDR ranges
- GuardDuty enabled

### 3. Centralized Logging
```
All Accounts → CloudTrail/Config → Log Archive Account → S3 (encrypted)
```

### 4. Security Controls
- **SCPs**: Prevent disabling CloudTrail, leaving organization, etc.
- **GuardDuty**: Threat detection across all accounts
- **Security Hub**: Aggregated security findings
- **IAM Access Analyzer**: Detect external access

## When You Need This

| Scenario | Single Account | Landing Zone/Control Tower |
|----------|---------------|---------------------------|
| Learning/Personal | ✓ | |
| Small startup | ✓ | |
| Multiple teams | | ✓ |
| Compliance (SOC2, HIPAA, PCI) | | ✓ |
| Enterprise | | ✓ |
| Workload isolation required | | ✓ |

## Getting Started with Control Tower

1. **Prerequisites**
   - AWS Organizations not yet set up (or clean state)
   - Admin access to management account

2. **Setup Steps**
   ```
   AWS Console → Control Tower → Set up landing zone
   ```
   - Choose home region
   - Configure OUs (Security, Sandbox)
   - Control Tower creates Log Archive and Audit accounts

3. **Account Factory**
   - Use Account Factory to provision new accounts
   - Each account gets the baseline automatically

## Key Terminology

| Term | Meaning |
|------|---------|
| **Management Account** | The root account that owns the organization |
| **OU (Organizational Unit)** | Logical grouping of accounts |
| **SCP (Service Control Policy)** | Permission guardrails applied to OUs/accounts |
| **Guardrails** | Preventive or detective controls (Control Tower term) |
| **Account Factory** | Automated account provisioning in Control Tower |
| **AFT (Account Factory for Terraform)** | Terraform-based account provisioning |

## Best Practices

1. **Never use management account for workloads** - only for organization management
2. **Separate security and logging accounts** - limits blast radius
3. **Use OUs to group accounts** - apply SCPs at OU level
4. **Enable all regions in CloudTrail** - attackers use unused regions
5. **Use SSO for human access** - no IAM users in member accounts
6. **Automate account provisioning** - use Account Factory or AFT

## Further Reading

- [AWS Control Tower Documentation](https://docs.aws.amazon.com/controltower/)
- [AWS Organizations Documentation](https://docs.aws.amazon.com/organizations/)
- [AWS Multi-Account Strategy Whitepaper](https://docs.aws.amazon.com/whitepapers/latest/organizing-your-aws-environment/)
