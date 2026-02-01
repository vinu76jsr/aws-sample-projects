# 04 - SageMaker Feature Store[^feature-store]

> **Exam Weight**: High frequency in Data Preparation domain (28%)
> **Priority**: HIGH - Hot topic in the exam

## What is SageMaker Feature Store?

A centralized repository to store, share, and manage ML features for training and real-time inference. It provides consistency between training and serving, and enables feature reuse across teams.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     SAGEMAKER FEATURE STORE                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐                              ┌─────────────┐          │
│  │   ONLINE    │◄─── Low Latency (<10ms) ────│  Real-time  │          │
│  │    STORE    │     GetRecord API            │  Inference  │          │
│  │  (DynamoDB) │                              └─────────────┘          │
│  └─────────────┘                                                        │
│         │                                                               │
│         │  Auto-sync                                                    │
│         ▼                                                               │
│  ┌─────────────┐                              ┌─────────────┐          │
│  │   OFFLINE   │◄─── Batch Queries ──────────│  Training   │          │
│  │    STORE    │     Athena / Spark           │    Jobs     │          │
│  │    (S3)     │                              └─────────────┘          │
│  └─────────────┘                                                        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Key Concepts (MEMORIZE FOR EXAM)

### Feature Group[^feature-group]

A logical grouping of features (like a table).

```
Feature Group: customer_features
├── record_identifier: customer_id (Primary Key)
├── event_time: timestamp (Required)
├── feature_1: total_purchases
├── feature_2: avg_order_value
├── feature_3: days_since_last_purchase
└── feature_4: customer_segment
```

### Online Store[^online-store] vs Offline Store[^offline-store]

| Aspect | Online Store | Offline Store |
|--------|--------------|---------------|
| **Storage** | DynamoDB | S3 (Parquet) |
| **Latency** | <10ms | Seconds-minutes |
| **Use Case** | Real-time inference | Training, batch inference |
| **Query** | GetRecord API | Athena[^athena], Spark, Feature Store queries |
| **Data** | Latest values only | Full history |
| **Cost** | Higher (DynamoDB) | Lower (S3) |

### Exam Tip: Store Selection
- **"Real-time fraud detection"** → Online Store
- **"Model training"** → Offline Store
- **"Both training and inference"** → Enable both stores

---

## Record Identifier[^record-identifier] and Event Time[^event-time]

Every feature group requires:

1. **Record Identifier**: Primary key (e.g., customer_id, transaction_id)
2. **Event Time**: Timestamp for versioning and point-in-time queries

```python
feature_group = FeatureGroup(
    name="customer_features",
    record_identifier_feature_name="customer_id",  # Primary key
    event_time_feature_name="event_time",          # Required timestamp
    feature_definitions=[...],
    sagemaker_session=session
)
```

---

## Feature Definitions and Types

### Supported Data Types

| Type | Description | Example |
|------|-------------|---------|
| **Integral** | Integer values | customer_id, age |
| **Fractional** | Floating point | amount, score |
| **String** | Text values | name, category |

```python
from sagemaker.feature_store.feature_definition import (
    FeatureDefinition,
    FeatureTypeEnum
)

feature_definitions = [
    FeatureDefinition(feature_name="customer_id", feature_type=FeatureTypeEnum.INTEGRAL),
    FeatureDefinition(feature_name="event_time", feature_type=FeatureTypeEnum.FRACTIONAL),
    FeatureDefinition(feature_name="total_purchases", feature_type=FeatureTypeEnum.INTEGRAL),
    FeatureDefinition(feature_name="avg_order_value", feature_type=FeatureTypeEnum.FRACTIONAL),
    FeatureDefinition(feature_name="customer_segment", feature_type=FeatureTypeEnum.STRING),
]
```

---

## Ingestion Patterns

### 1. Streaming Ingestion (Real-time)

```python
# Ingest single record
feature_group.put_record(
    record=[
        {"FeatureName": "customer_id", "ValueAsString": "12345"},
        {"FeatureName": "event_time", "ValueAsString": "1609459200.0"},
        {"FeatureName": "total_purchases", "ValueAsString": "50"},
        {"FeatureName": "avg_order_value", "ValueAsString": "75.50"},
    ]
)
```

### 2. Batch Ingestion (Bulk)

```python
# Ingest from DataFrame
feature_group.ingest(
    data_frame=df,
    max_workers=3,
    wait=True
)
```

### 3. Streaming Ingestion from Kinesis

```
Kinesis Data Streams → Lambda → Feature Store
```

### Exam Tip: Ingestion Selection
- **"Real-time updates"** → put_record API
- **"Bulk historical data"** → ingest() from DataFrame
- **"Streaming pipeline"** → Kinesis → Lambda → Feature Store

---

## Querying Features

### Online Store Query (Real-time)

```python
# Get latest feature values for a record
record = feature_group.get_record(
    record_identifier_value_as_string="12345"
)

# Batch get (multiple records)
from sagemaker.feature_store.feature_store import FeatureStore

feature_store = FeatureStore(sagemaker_session=session)
batch_records = feature_store.batch_get_record(
    identifiers=[
        Identifier(
            feature_group_name="customer_features",
            record_identifiers_value_as_string=["12345", "67890"]
        )
    ]
)
```

### Offline Store Query (Training)

```python
# Query with Athena
query = feature_group.athena_query()

query.run(
    query_string="""
        SELECT *
        FROM "sagemaker_featurestore"."customer_features"
        WHERE customer_segment = 'premium'
    """,
    output_location="s3://bucket/query-results/"
)

# Get results as DataFrame
df = query.as_dataframe()
```

---

## Point-in-Time Queries[^point-in-time] (EXAM FAVORITE)

Retrieve features as they were at a specific point in time - crucial for avoiding data leakage in ML.

```python
# Point-in-time correct feature retrieval
query_string = """
SELECT cf.customer_id,
       cf.total_purchases,
       cf.avg_order_value,
       cf.event_time
FROM "sagemaker_featurestore"."customer_features" cf
WHERE cf.event_time <= 1609459200.0  -- Features as of this timestamp
  AND cf.customer_id IN ('12345', '67890')
"""
```

### Why Point-in-Time Matters

```
Training Example (Label at time T):
─────────────────────────────────────────────────
Timeline:  T-30 days    T-7 days    T (Label)    T+7 days
              │            │           │            │
Features:   [A, B]      [C, D]      [E, F]       [G, H]

WRONG: Use features [E, F] or [G, H] for training (data leakage!)
RIGHT: Use features [C, D] (last known before label time)
```

### Exam Tip
- **"Avoid data leakage in training"** → Point-in-time queries
- **"Feature values at prediction time"** → Match training time window

---

## Feature Store Integration Patterns

### Pattern 1: Training Pipeline

```
┌──────────┐     ┌──────────────┐     ┌──────────────┐     ┌───────────┐
│  Glue    │────▶│   Feature    │────▶│   Offline    │────▶│ SageMaker │
│  ETL     │     │    Store     │     │    Store     │     │ Training  │
└──────────┘     └──────────────┘     └──────────────┘     └───────────┘
```

### Pattern 2: Real-time Inference

```
┌──────────┐     ┌──────────────┐     ┌──────────────┐
│ Request  │────▶│   Online     │────▶│  SageMaker   │
│          │     │    Store     │     │   Endpoint   │
└──────────┘     └──────────────┘     └──────────────┘
```

### Pattern 3: Batch Inference

```
┌──────────┐     ┌──────────────┐     ┌──────────────┐
│ Offline  │────▶│    Athena    │────▶│    Batch     │
│  Store   │     │    Query     │     │  Transform   │
└──────────┘     └──────────────┘     └──────────────┘
```

---

## Feature Store Security

### IAM Permissions

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "sagemaker:CreateFeatureGroup",
                "sagemaker:DescribeFeatureGroup",
                "sagemaker:GetRecord",
                "sagemaker:PutRecord",
                "sagemaker:DeleteRecord"
            ],
            "Resource": "arn:aws:sagemaker:*:*:feature-group/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject"
            ],
            "Resource": "arn:aws:s3:::sagemaker-*-featurestore/*"
        }
    ]
}
```

### Encryption

| Component | Encryption |
|-----------|------------|
| Online Store | AWS managed KMS or CMK |
| Offline Store | S3 encryption (SSE-S3 or SSE-KMS) |
| In Transit | TLS 1.2 |

---

## TTL (Time-To-Live)

Configure automatic expiration of records in online store.

```python
# Enable TTL when creating feature group
online_store_config = OnlineStoreConfig(
    enable_online_store=True,
    ttl_duration={
        'Unit': 'Days',
        'Value': 30  # Records expire after 30 days
    }
)
```

### Exam Tip
- TTL only applies to **Online Store**
- Offline Store retains full history
- Use for features that become stale (e.g., real-time signals)

---

## Cost Considerations

| Component | Pricing Model |
|-----------|---------------|
| **Online Store** | Read/Write units + Storage (DynamoDB pricing) |
| **Offline Store** | S3 storage (Parquet files) |
| **Ingestion** | Per-record charge |
| **Queries** | Athena charges (per TB scanned) |

### Cost Optimization

- Disable Online Store if only used for training
- Use TTL to reduce Online Store storage
- Partition Offline Store data for efficient Athena queries

---

## Sample Implementation

```python
import sagemaker
from sagemaker.feature_store.feature_group import FeatureGroup
from sagemaker.feature_store.feature_definition import (
    FeatureDefinition,
    FeatureTypeEnum
)
import pandas as pd
import time

# Initialize
session = sagemaker.Session()
role = sagemaker.get_execution_role()
region = session.boto_region_name

# Define feature group
feature_group_name = "customer-features"

feature_definitions = [
    FeatureDefinition(feature_name="customer_id", feature_type=FeatureTypeEnum.STRING),
    FeatureDefinition(feature_name="event_time", feature_type=FeatureTypeEnum.FRACTIONAL),
    FeatureDefinition(feature_name="total_purchases", feature_type=FeatureTypeEnum.INTEGRAL),
    FeatureDefinition(feature_name="avg_order_value", feature_type=FeatureTypeEnum.FRACTIONAL),
    FeatureDefinition(feature_name="days_since_last_purchase", feature_type=FeatureTypeEnum.INTEGRAL),
    FeatureDefinition(feature_name="customer_segment", feature_type=FeatureTypeEnum.STRING),
]

feature_group = FeatureGroup(
    name=feature_group_name,
    sagemaker_session=session,
    feature_definitions=feature_definitions
)

# Create feature group
feature_group.create(
    s3_uri=f"s3://{session.default_bucket()}/feature-store/",
    record_identifier_name="customer_id",
    event_time_feature_name="event_time",
    role_arn=role,
    enable_online_store=True,   # Enable for real-time inference
    # enable_online_store=False,  # Disable if only used for training
)

# Wait for creation
while feature_group.describe().get("FeatureGroupStatus") == "Creating":
    print("Creating feature group...")
    time.sleep(5)

print(f"Feature group status: {feature_group.describe().get('FeatureGroupStatus')}")

# Prepare sample data
data = {
    "customer_id": ["C001", "C002", "C003"],
    "event_time": [time.time(), time.time(), time.time()],
    "total_purchases": [50, 120, 30],
    "avg_order_value": [75.50, 150.25, 45.00],
    "days_since_last_purchase": [5, 2, 15],
    "customer_segment": ["premium", "premium", "standard"]
}
df = pd.DataFrame(data)

# Ingest features
feature_group.ingest(data_frame=df, max_workers=3, wait=True)
print("Features ingested successfully!")

# Query online store (real-time)
record = feature_group.get_record(record_identifier_value_as_string="C001")
print(f"Online store record: {record}")

# Query offline store (Athena)
query = feature_group.athena_query()
query.run(
    query_string=f'SELECT * FROM "sagemaker_featurestore"."{feature_group_name}"',
    output_location=f"s3://{session.default_bucket()}/query-results/"
)
query.wait()
df_result = query.as_dataframe()
print(f"Offline store results: {df_result}")
```

---

## Exam Question Patterns

### Pattern 1: Real-time vs Training
> "Features needed for both real-time inference and model training..."

**Answer**: Enable both Online and Offline stores

### Pattern 2: Data Consistency
> "Ensure training features match production features..."

**Answer**: Use Feature Store as single source of truth

### Pattern 3: Historical Features
> "Train model on features as they existed at purchase time..."

**Answer**: Point-in-time query on Offline Store

### Pattern 4: Low Latency
> "Get features for real-time fraud detection (<50ms)..."

**Answer**: Online Store with GetRecord API

### Pattern 5: Feature Reuse
> "Multiple teams need to share customer features..."

**Answer**: Create shared Feature Group with proper IAM permissions

### Pattern 6: Cost Optimization
> "Features only used for batch training, minimize costs..."

**Answer**: Create Feature Group with Online Store disabled

---

## Feature Store vs Alternatives

| Solution | Use Case | Exam Scenario |
|----------|----------|---------------|
| **Feature Store** | Centralized feature management | "Reuse features across teams" |
| **S3 + Glue Catalog** | Simple data lake | "Basic batch training" |
| **DynamoDB** | Custom low-latency store | "Custom application" |
| **ElastiCache** | In-memory caching | "Ultra-low latency" |

---

## Checklist

- [ ] Understand Online vs Offline Store and when to use each
- [ ] Know record identifier and event time requirements
- [ ] Understand ingestion patterns (streaming, batch)
- [ ] Know how to query features (GetRecord, Athena)
- [ ] Understand point-in-time queries for training
- [ ] Know TTL configuration for Online Store
- [ ] Understand security (IAM, encryption)

---

## Glossary

[^feature-store]: **Feature Store** - A centralized repository in SageMaker for storing, sharing, and managing ML features. It ensures consistency between training and inference while enabling feature reuse across teams and projects.

[^feature-group]: **Feature Group** - A logical grouping of features in Feature Store, similar to a database table. Each feature group has a schema, a record identifier, and an event time column.

[^online-store]: **Online Store** - A low-latency store backed by DynamoDB that serves the latest feature values for real-time inference. It provides single-digit millisecond response times via the GetRecord API.

[^offline-store]: **Offline Store** - A store backed by S3 (in Parquet format) that maintains the full history of feature values. It is used for model training, batch inference, and analytical queries.

[^event-time]: **Event Time** - A required timestamp column in every feature group that indicates when a feature value was generated. It enables point-in-time queries and proper versioning of feature records.

[^record-identifier]: **Record Identifier** - The primary key column in a feature group that uniquely identifies each record (e.g., customer_id, transaction_id). Required for all feature groups.

[^point-in-time]: **Point-in-Time Query** - A query technique that retrieves feature values as they existed at a specific timestamp. Critical for avoiding data leakage during model training by ensuring features match the time of the label.

[^athena]: **Athena** - An AWS serverless query service that can be used to run SQL queries on the Offline Store data in S3. It enables ad-hoc analysis and batch feature retrieval for training datasets.

---

## Next Steps

After completing this module, proceed to:
- [05 - SageMaker Pipelines](../05-sagemaker-pipelines/) - ML CI/CD automation
