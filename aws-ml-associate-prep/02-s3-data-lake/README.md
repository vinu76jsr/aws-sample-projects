# 02 - Amazon S3 Data Lake for ML

> **Exam Weight**: Foundation for all data-related questions (~15%)
> **Priority**: HIGH - S3 is used in almost every ML workflow

## What is Amazon S3?

Amazon Simple Storage Service (S3) is object storage that provides unlimited scalability. For ML, S3 serves as the primary data lake for training data, model artifacts, and inference results.

## Key Concepts for ML

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         S3 FOR MACHINE LEARNING                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐              │
│   │   RAW DATA  │────▶│  PROCESSED  │────▶│   FEATURES  │              │
│   │   (Bronze)  │     │   (Silver)  │     │   (Gold)    │              │
│   └─────────────┘     └─────────────┘     └─────────────┘              │
│         │                   │                   │                       │
│         ▼                   ▼                   ▼                       │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐              │
│   │   Glue ETL  │     │  SageMaker  │     │  Training   │              │
│   │   Crawlers  │     │  Processing │     │    Jobs     │              │
│   └─────────────┘     └─────────────┘     └─────────────┘              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## S3 Storage Classes (KNOW FOR EXAM)

| Storage Class | Use Case | Retrieval | Min Storage | Exam Scenario |
|---------------|----------|-----------|-------------|---------------|
| **S3 Standard** | Frequently accessed data | Instant | None | Active training data |
| **S3 Intelligent-Tiering** | Unknown access patterns | Instant | 30 days | Variable ML workloads |
| **S3 Standard-IA** | Infrequent access | Instant | 30 days | Historical training data |
| **S3 One Zone-IA** | Infrequent, non-critical | Instant | 30 days | Reproducible data |
| **S3 Glacier Instant** | Archive, instant access | Instant | 90 days | Model artifacts archive |
| **S3 Glacier Flexible** | Archive, minutes-hours | 1-12 hours | 90 days | Compliance archives |
| **S3 Glacier Deep Archive** | Long-term archive | 12-48 hours | 180 days | Regulatory retention |

### Exam Tip: Storage Class Selection
- **"Frequently accessed training data"** → S3 Standard
- **"Unpredictable access patterns"** → Intelligent-Tiering
- **"Archive models for compliance"** → Glacier Instant or Flexible
- **"Cost-effective, can be regenerated"** → One Zone-IA

---

## S3 Data Organization for ML

### Recommended Structure

```
s3://ml-data-lake/
├── raw/                          # Raw ingested data (Bronze)
│   ├── source1/
│   │   └── year=2024/month=01/
│   └── source2/
│       └── year=2024/month=01/
│
├── processed/                    # Cleaned data (Silver)
│   └── dataset-v1/
│       ├── train/
│       ├── validation/
│       └── test/
│
├── features/                     # Feature store exports (Gold)
│   └── feature-group-1/
│
├── models/                       # Model artifacts
│   └── model-name/
│       └── version-1/
│           └── model.tar.gz
│
├── predictions/                  # Inference outputs
│   └── batch-job-id/
│
└── experiments/                  # Experiment tracking
    └── experiment-id/
```

### Partitioning Strategy (EXAM FAVORITE)

```
# Good partitioning for time-series data
s3://bucket/data/year=2024/month=01/day=15/

# Good partitioning for categorical data
s3://bucket/data/region=us-east/category=electronics/

# Enables efficient queries with Athena/Glue
# Reduces data scanned = lower cost
```

---

## S3 Data Formats for ML

| Format | Compression | Use Case | SageMaker Support |
|--------|-------------|----------|-------------------|
| **CSV** | Optional | Simple tabular data | All algorithms |
| **JSON/JSONL** | Optional | Semi-structured data | Most algorithms |
| **Parquet** | Built-in | Columnar, analytics | XGBoost, Spark |
| **RecordIO** | Built-in | SageMaker optimized | Built-in algorithms |
| **TFRecord** | Built-in | TensorFlow | TensorFlow |
| **LibSVM** | No | Sparse data | XGBoost |

### Exam Tip: Format Selection
- **"Best performance with SageMaker built-in"** → RecordIO
- **"Columnar analytics, Athena queries"** → Parquet
- **"TensorFlow training"** → TFRecord
- **"Simple, universal"** → CSV

---

## S3 Security for ML

### Access Control Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                        ACCESS CONTROL                           │
├─────────────────────────────────────────────────────────────────┤
│  1. IAM Policies        → Who can access (users, roles)         │
│  2. Bucket Policies     → What can be accessed (bucket level)   │
│  3. S3 Access Points    → Simplified access for applications    │
│  4. ACLs (Legacy)       → Object-level permissions              │
│  5. Block Public Access → Prevent accidental exposure           │
└─────────────────────────────────────────────────────────────────┘
```

### SageMaker IAM Role for S3

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::ml-data-bucket",
                "arn:aws:s3:::ml-data-bucket/*"
            ]
        }
    ]
}
```

### Encryption Options (EXAM FOCUS)

| Type | Key Management | Use Case |
|------|----------------|----------|
| **SSE-S3** | AWS managed | Default, simple |
| **SSE-KMS** | Customer managed (CMK) | Audit trail, key rotation |
| **SSE-C** | Customer provided | Complete control |
| **Client-side** | Before upload | Maximum security |

### Exam Tip
- **"Audit who accessed encryption keys"** → SSE-KMS
- **"Simple encryption, no management"** → SSE-S3
- **"Compliance requires customer keys"** → SSE-KMS with CMK

---

## S3 Features for ML Workflows

### Versioning

```
┌─────────────────────────────────────────────────────┐
│  s3://bucket/model.tar.gz                           │
│  ├── Version ID: abc123 (Latest)                    │
│  ├── Version ID: def456                             │
│  └── Version ID: ghi789                             │
└─────────────────────────────────────────────────────┘

Use cases:
- Model artifact versioning
- Training data lineage
- Rollback capabilities
```

### Lifecycle Policies

```json
{
    "Rules": [
        {
            "ID": "Archive old models",
            "Status": "Enabled",
            "Filter": {"Prefix": "models/"},
            "Transitions": [
                {
                    "Days": 30,
                    "StorageClass": "STANDARD_IA"
                },
                {
                    "Days": 90,
                    "StorageClass": "GLACIER"
                }
            ]
        },
        {
            "ID": "Delete temp data",
            "Status": "Enabled",
            "Filter": {"Prefix": "temp/"},
            "Expiration": {"Days": 7}
        }
    ]
}
```

### S3 Event Notifications (EXAM FAVORITE)

```
┌──────────┐     ┌──────────┐     ┌─────────────────────┐
│   S3     │────▶│  Event   │────▶│  Lambda / SNS / SQS │
│  Upload  │     │ Trigger  │     │  EventBridge        │
└──────────┘     └──────────┘     └─────────────────────┘
                                           │
                                           ▼
                                  ┌─────────────────────┐
                                  │  Start SageMaker    │
                                  │  Training Pipeline  │
                                  └─────────────────────┘
```

### Exam Tip: Event-Driven ML
- **"Automatically start training when new data arrives"** → S3 Event → Lambda → SageMaker
- **"Process uploaded images"** → S3 Event → Lambda → Rekognition

---

## S3 Performance Optimization

### Multipart Upload

```python
# Automatic with boto3 for files > 5MB
import boto3

s3 = boto3.client('s3')

# Configure multipart threshold
from boto3.s3.transfer import TransferConfig

config = TransferConfig(
    multipart_threshold=8 * 1024 * 1024,  # 8MB
    max_concurrency=10,
    multipart_chunksize=8 * 1024 * 1024,
    use_threads=True
)

s3.upload_file('large_file.csv', 'bucket', 'key', Config=config)
```

### S3 Transfer Acceleration

- Uses CloudFront edge locations
- Faster uploads from distant locations
- Enable for geographically distributed teams

### Request Rate Performance

```
S3 Prefix Design for High Throughput:

Bad:  s3://bucket/2024/01/15/file1.csv  (all same prefix)
Good: s3://bucket/a1b2/2024/01/15/file1.csv  (randomized prefix)

S3 now auto-scales, but distributing prefixes still helps
for extremely high request rates (>3,500 PUT/POST/DELETE or
>5,500 GET per second per prefix)
```

---

## S3 Access Points

Simplify access management for shared data lakes:

```
┌──────────────────────────────────────────────────────────────┐
│                     S3 BUCKET (Data Lake)                    │
└──────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│ Access Point  │     │ Access Point  │     │ Access Point  │
│ (Data Science)│     │ (ML Training) │     │ (Analytics)   │
│ /processed/*  │     │ /features/*   │     │ /reports/*    │
└───────────────┘     └───────────────┘     └───────────────┘
```

---

## S3 + SageMaker Integration

### Training Input Configuration

```python
from sagemaker.inputs import TrainingInput

# File mode (default) - downloads to instance
train_input = TrainingInput(
    s3_data='s3://bucket/train/',
    content_type='text/csv',
    input_mode='File'
)

# Pipe mode - streams data (for large datasets)
train_input_pipe = TrainingInput(
    s3_data='s3://bucket/train/',
    content_type='text/csv',
    input_mode='Pipe'  # Faster startup, handles large data
)

# FastFile mode - POSIX streaming
train_input_fast = TrainingInput(
    s3_data='s3://bucket/train/',
    content_type='text/csv',
    input_mode='FastFile'  # Random access + streaming
)
```

### Model Artifacts

```python
# SageMaker saves models to S3 automatically
estimator = XGBoost(
    ...
    output_path='s3://bucket/models/'  # Model artifacts saved here
)

# After training, model is at:
# s3://bucket/models/<training-job-name>/output/model.tar.gz
```

---

## Sample Implementation

### Data Lake Setup with Boto3

```python
import boto3
import json

s3 = boto3.client('s3')
bucket_name = 'ml-data-lake-demo'

# Create bucket
s3.create_bucket(
    Bucket=bucket_name,
    CreateBucketConfiguration={'LocationConstraint': 'us-west-2'}
)

# Enable versioning
s3.put_bucket_versioning(
    Bucket=bucket_name,
    VersioningConfiguration={'Status': 'Enabled'}
)

# Block public access
s3.put_public_access_block(
    Bucket=bucket_name,
    PublicAccessBlockConfiguration={
        'BlockPublicAcls': True,
        'IgnorePublicAcls': True,
        'BlockPublicPolicy': True,
        'RestrictPublicBuckets': True
    }
)

# Enable default encryption (SSE-S3)
s3.put_bucket_encryption(
    Bucket=bucket_name,
    ServerSideEncryptionConfiguration={
        'Rules': [{
            'ApplyServerSideEncryptionByDefault': {
                'SSEAlgorithm': 'AES256'
            }
        }]
    }
)

# Add lifecycle policy
lifecycle_policy = {
    'Rules': [
        {
            'ID': 'ArchiveOldModels',
            'Status': 'Enabled',
            'Filter': {'Prefix': 'models/'},
            'Transitions': [
                {'Days': 30, 'StorageClass': 'STANDARD_IA'},
                {'Days': 90, 'StorageClass': 'GLACIER'}
            ]
        },
        {
            'ID': 'DeleteTempFiles',
            'Status': 'Enabled',
            'Filter': {'Prefix': 'temp/'},
            'Expiration': {'Days': 7}
        }
    ]
}

s3.put_bucket_lifecycle_configuration(
    Bucket=bucket_name,
    LifecycleConfiguration=lifecycle_policy
)

print(f"Bucket {bucket_name} configured for ML data lake")
```

---

## Exam Question Patterns

### Pattern 1: Storage Class
> "Training data is accessed frequently during development but rarely after model deployment..."

**Answer**: Use lifecycle policy to transition to Standard-IA after 30 days

### Pattern 2: Security
> "Compliance requires encryption with audit trail of key access..."

**Answer**: SSE-KMS with customer managed key (CMK)

### Pattern 3: Performance
> "Large training dataset (500GB) causes slow training job startup..."

**Answer**: Use Pipe mode instead of File mode

### Pattern 4: Event-Driven
> "Automatically trigger retraining when new data is uploaded..."

**Answer**: S3 Event Notification → EventBridge → Step Functions/Lambda

### Pattern 5: Cost
> "Reduce storage costs for old model artifacts while keeping them accessible..."

**Answer**: Lifecycle policy to Glacier Instant Retrieval

---

## Checklist

- [ ] Understand all S3 storage classes and when to use each
- [ ] Know encryption options (SSE-S3, SSE-KMS, SSE-C)
- [ ] Understand lifecycle policies for cost optimization
- [ ] Know File vs Pipe vs FastFile mode for SageMaker
- [ ] Understand S3 event notifications for ML pipelines
- [ ] Know data format options (CSV, Parquet, RecordIO)
- [ ] Understand partitioning strategies for performance

---

## Next Steps

After completing this module, proceed to:
- [03 - AWS Glue ETL](../03-glue-etl/) - Data transformation and cataloging
