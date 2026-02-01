# 03 - AWS Glue ETL for ML Data Preparation

> **Exam Weight**: Part of Data Preparation domain (28%)
> **Priority**: HIGH - Essential for data transformation and cataloging

## What is AWS Glue?

AWS Glue[^glue] is a fully managed ETL[^etl] (Extract, Transform, Load) service that makes it easy to prepare and transform data for analytics and ML. It includes:
- **Glue Data Catalog**[^data-catalog]: Centralized metadata repository
- **Glue ETL Jobs**: Serverless Spark-based data transformation
- **Glue Crawlers**[^crawler]: Automatic schema discovery
- **Glue DataBrew**: Visual data preparation (no-code)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           AWS GLUE ECOSYSTEM                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  DATA SOURCES          GLUE COMPONENTS           DATA TARGETS          │
│  ────────────          ────────────────          ────────────          │
│  • S3                  • Crawlers                • S3                  │
│  • RDS                 • Data Catalog            • Redshift            │
│  • DynamoDB            • ETL Jobs                • RDS                 │
│  • JDBC                • DataBrew                • Elasticsearch       │
│  • Kinesis             • Workflows               • SageMaker           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Glue Components (EXAM FOCUS)

### 1. Glue Data Catalog

The central metadata repository that stores table definitions, schema, and partition information.

```
┌─────────────────────────────────────────────────┐
│              GLUE DATA CATALOG                  │
├─────────────────────────────────────────────────┤
│  Database: ml_data_lake                         │
│  ├── Table: raw_customers                       │
│  │   ├── Columns: id, name, email, created_at  │
│  │   ├── Location: s3://bucket/raw/customers/  │
│  │   └── Partitions: year, month               │
│  ├── Table: raw_transactions                    │
│  │   └── ...                                    │
│  └── Table: features_customers                  │
│      └── ...                                    │
└─────────────────────────────────────────────────┘
```

**Key Points:**
- Hive-compatible metastore
- Used by Athena, Redshift Spectrum, EMR, SageMaker
- Supports multiple data formats (CSV, JSON, Parquet, ORC, Avro)

### 2. Glue Crawlers

Automatically discover and catalog data schemas.

```
┌──────────┐     ┌──────────┐     ┌──────────────┐
│    S3    │────▶│ Crawler  │────▶│ Data Catalog │
│   Data   │     │          │     │   (Tables)   │
└──────────┘     └──────────┘     └──────────────┘
```

**Crawler Behavior:**
| Scenario | Action |
|----------|--------|
| New data discovered | Creates new table |
| Schema change | Updates table schema |
| New partitions | Adds partitions to table |

### 3. Glue ETL Jobs

Serverless Spark jobs for data transformation.

| Job Type | Use Case | Language |
|----------|----------|----------|
| **Spark** | Large-scale ETL | Python, Scala |
| **Spark Streaming** | Real-time ETL | Python, Scala |
| **Python Shell** | Small jobs, lightweight | Python |
| **Ray** | ML workloads | Python |

### 4. Glue DataBrew

Visual data preparation tool (no-code).

**Key Features:**
- 250+ built-in transformations
- Data quality rules
- Visual data profiling
- Recipe-based transformations

---

## DPU[^dpu] (Data Processing Units) - EXAM FAVORITE

| Worker Type | Memory | vCPUs | Use Case |
|-------------|--------|-------|----------|
| **Standard** | 16 GB | 4 | General ETL |
| **G.1X** | 16 GB | 4 | Memory-intensive |
| **G.2X** | 32 GB | 8 | Very memory-intensive |
| **G.4X** | 64 GB | 16 | Large transformations |
| **G.8X** | 128 GB | 32 | Extreme workloads |
| **Z.2X** | 64 GB | 8 | Streaming jobs |

### Exam Tip: DPU Selection
- **"Cost-effective, standard workload"** → Standard (default)
- **"Memory-intensive joins"** → G.2X or higher
- **"Streaming data"** → Z.2X

---

## Glue Job Bookmarks[^job-bookmarks]

Track processed data to avoid reprocessing.

```
Without Bookmarks:
Run 1: Process files A, B, C
Run 2: Process files A, B, C, D  ← Reprocesses A, B, C!

With Bookmarks:
Run 1: Process files A, B, C     ← Bookmark saves state
Run 2: Process file D only       ← Only new data!
```

| Setting | Behavior |
|---------|----------|
| **Enable** | Track and process only new data |
| **Disable** | Process all data every run |
| **Pause** | Keep bookmark but process all data |

### Exam Tip
- **"Process only new files"** → Enable job bookmarks
- **"Reprocess everything once"** → Pause, then Enable

---

## Glue Workflows

Orchestrate multiple crawlers and jobs.

```
┌─────────────────────────────────────────────────────────────────┐
│                       GLUE WORKFLOW                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐   │
│  │ Trigger │────▶│ Crawler │────▶│ ETL Job │────▶│ Crawler │   │
│  │ (Start) │     │  (Raw)  │     │ (Clean) │     │(Output) │   │
│  └─────────┘     └─────────┘     └─────────┘     └─────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Trigger Types:**
| Type | Description |
|------|-------------|
| **On-demand** | Manual trigger |
| **Scheduled** | Cron expression |
| **Conditional** | Based on job completion |
| **Event** | S3 events, EventBridge |

---

## Glue + SageMaker Integration

### Pattern 1: Data Preparation Pipeline

```
S3 (Raw) → Glue Crawler → Glue ETL → S3 (Processed) → SageMaker Training
```

### Pattern 2: Feature Engineering

```
S3 (Raw) → Glue ETL → SageMaker Feature Store
```

### Pattern 3: Inference Data Prep

```
S3 (New Data) → Glue ETL → SageMaker Batch Transform
```

---

## Glue Data Quality

Built-in data quality rules for ML data validation.

```python
# Example quality rules
rules = """
    Rules = [
        ColumnValues "customer_id" > 0,
        IsComplete "email",
        ColumnLength "phone" = 10,
        ColumnValues "age" between 0 and 120,
        Uniqueness "customer_id" > 0.99,
        ColumnDataType "created_at" = "timestamp"
    ]
"""
```

**Key Metrics:**
- Completeness (no nulls)
- Uniqueness (no duplicates)
- Validity (within range)
- Consistency (format checks)

---

## Common Transformations for ML

### 1. Schema Transformation

```python
# ApplyMapping - rename and cast columns
from awsglue.transforms import ApplyMapping

mapped = ApplyMapping.apply(
    frame=datasource,
    mappings=[
        ("old_name", "string", "new_name", "string"),
        ("price", "string", "price", "double"),
        ("date", "string", "date", "timestamp")
    ]
)
```

### 2. Filtering

```python
# Filter rows based on conditions
filtered = Filter.apply(
    frame=datasource,
    f=lambda x: x["age"] >= 18 and x["country"] == "US"
)
```

### 3. Join Operations

```python
# Join two datasets
joined = Join.apply(
    frame1=customers,
    frame2=transactions,
    keys1=["customer_id"],
    keys2=["customer_id"]
)
```

### 4. Handling Missing Values

```python
# Fill missing values
from awsglue.transforms import FillMissingValues

filled = FillMissingValues.apply(
    frame=datasource,
    missing_vals_column="salary",
    dimension_column="department"  # Fill based on department mean
)
```

### 5. Drop Duplicates

```python
# Remove duplicates
deduped = DropDuplicates.apply(
    frame=datasource,
    keys=["customer_id", "transaction_id"]
)
```

---

## Glue ETL Script Structure

```python
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame  # DynamicFrame[^dynamicframe]

# Initialize Glue context
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Read from Data Catalog
datasource = glueContext.create_dynamic_frame.from_catalog(
    database="ml_database",
    table_name="raw_data"
)

# Transform
transformed = ApplyMapping.apply(
    frame=datasource,
    mappings=[...]
)

# Write to S3 in Parquet format
glueContext.write_dynamic_frame.from_options(
    frame=transformed,
    connection_type="s3",
    connection_options={"path": "s3://bucket/processed/"},
    format="parquet"
)

# Commit job (for bookmarks)
job.commit()
```

---

## Data Formats and Partitioning

### Output Formats

| Format | Compression | Use Case |
|--------|-------------|----------|
| **Parquet**[^parquet] | Snappy (default) | Analytics, Athena queries |
| **ORC** | Zlib | Hive workloads |
| **JSON** | Gzip | Semi-structured data |
| **CSV** | Gzip | Simple exchange |

### Partitioning (EXAM FAVORITE)

```python
# Write with partitioning
glueContext.write_dynamic_frame.from_options(
    frame=transformed,
    connection_type="s3",
    connection_options={
        "path": "s3://bucket/processed/",
        "partitionKeys": ["year", "month", "day"]  # Creates folder structure
    },
    format="parquet"
)

# Result:
# s3://bucket/processed/year=2024/month=01/day=15/data.parquet
```

### Exam Tip
- **"Optimize Athena query costs"** → Partition by frequently filtered columns
- **"Time-series data"** → Partition by date (year/month/day)

---

## Security

### IAM Role for Glue

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::source-bucket/*",
                "arn:aws:s3:::target-bucket/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "glue:*"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:/aws-glue/*"
        }
    ]
}
```

### Encryption

| Type | Description |
|------|-------------|
| **At Rest** | S3 encryption (SSE-S3, SSE-KMS) |
| **In Transit** | SSL/TLS connections |
| **Job Bookmarks** | Encrypted by default |
| **Data Catalog** | Catalog encryption setting |

---

## Cost Optimization

| Strategy | Description |
|----------|-------------|
| **Right-size DPUs** | Start small, scale as needed |
| **Job Bookmarks** | Avoid reprocessing data |
| **Partitioning** | Reduce data scanned |
| **Columnar Formats** | Parquet/ORC compress better |
| **Auto-scaling** | Enable for variable workloads |
| **Schedule Jobs** | Run during off-peak hours |

### Glue Job Pricing
- Billed per DPU-hour
- 10-second minimum billing
- Development endpoints: continuous billing

---

## Exam Question Patterns

### Pattern 1: Schema Discovery
> "Need to automatically detect schema of new data in S3..."

**Answer**: Use Glue Crawler to populate Data Catalog

### Pattern 2: Incremental Processing
> "ETL job should only process new files since last run..."

**Answer**: Enable Glue Job Bookmarks

### Pattern 3: Data Quality
> "Validate data quality before ML training..."

**Answer**: Use Glue Data Quality rules

### Pattern 4: Large Joins
> "ETL job fails with OOM during large join..."

**Answer**: Increase to G.2X or G.4X worker type

### Pattern 5: Query Optimization
> "Athena queries are slow and expensive..."

**Answer**: Partition data and use Parquet format

### Pattern 6: Visual Prep
> "Business users need to prepare data without coding..."

**Answer**: Use Glue DataBrew

---

## Glue vs Other Services

| Service | Use Case | Exam Scenario |
|---------|----------|---------------|
| **Glue ETL** | Batch transformation | "Transform data for ML" |
| **Glue DataBrew** | Visual, no-code prep | "Non-technical users" |
| **EMR** | Complex/custom Spark | "Custom ML algorithms" |
| **SageMaker Processing** | ML-specific processing | "Scikit-learn preprocessing" |
| **Kinesis** | Real-time streaming | "Real-time feature engineering" |
| **Lambda** | Small, event-driven | "Lightweight transformation" |

---

## Checklist

- [ ] Understand Glue components (Catalog, Crawlers, Jobs, DataBrew)
- [ ] Know DPU types and when to use each
- [ ] Understand job bookmarks for incremental processing
- [ ] Know how to partition data for performance
- [ ] Understand Glue + SageMaker integration patterns
- [ ] Know data quality rules
- [ ] Understand workflow orchestration

---

## Glossary

[^etl]: **ETL** - Extract, Transform, Load. A data integration process that extracts data from sources, transforms it into a usable format, and loads it into a target system.

[^glue]: **AWS Glue** - A fully managed, serverless ETL service that makes it easy to discover, prepare, and combine data for analytics, machine learning, and application development.

[^crawler]: **Crawler** - An AWS Glue component that automatically scans data sources, identifies data formats, and infers schemas to populate the Data Catalog with table definitions.

[^data-catalog]: **Data Catalog** - A centralized metadata repository in AWS Glue that stores table definitions, schema information, and partition data. It is Hive-compatible and used by services like Athena and Redshift Spectrum.

[^dynamicframe]: **DynamicFrame** - A distributed collection of data in AWS Glue, similar to a Spark DataFrame but with additional features for ETL operations like schema flexibility and built-in transformations.

[^job-bookmarks]: **Job Bookmarks** - A feature in AWS Glue that tracks data that has already been processed, enabling incremental ETL jobs that only process new data since the last run.

[^dpu]: **DPU** - Data Processing Unit. A measure of processing power in AWS Glue consisting of 4 vCPUs and 16 GB of memory. Different worker types (Standard, G.1X, G.2X, etc.) provide different memory configurations.

[^parquet]: **Parquet** - A columnar storage file format optimized for analytics workloads. It provides efficient compression and encoding schemes, making it ideal for queries that access specific columns.

---

## Next Steps

After completing this module, proceed to:
- [04 - SageMaker Feature Store](../04-feature-store/) - Centralized feature management
