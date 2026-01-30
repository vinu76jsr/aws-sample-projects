# 15 - Amazon Athena for ML Data Analysis

> **Exam Weight**: Part of Data Preparation domain (28%)
> **Priority**: MEDIUM - SQL queries on S3 data

## What is Amazon Athena?

Amazon Athena is a serverless query service that lets you analyze data in S3 using standard SQL. For ML, it's used to explore, analyze, and prepare training data.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         ATHENA FOR ML                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐              │
│  │    Glue     │     │   Athena    │     │    S3       │              │
│  │   Catalog   │◄────│   Query     │────▶│   (Data)    │              │
│  │  (Schema)   │     │   Engine    │     │             │              │
│  └─────────────┘     └─────────────┘     └─────────────┘              │
│                             │                                          │
│                             ▼                                          │
│  Use Cases:                                                            │
│  • Data exploration & profiling                                        │
│  • Feature analysis & selection                                        │
│  • Training data preparation                                           │
│  • Model evaluation results analysis                                   │
│  • Query Feature Store offline data                                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Key Features (KNOW FOR EXAM)

| Feature | Description | ML Use Case |
|---------|-------------|-------------|
| **Serverless** | No infrastructure | Ad-hoc analysis |
| **Standard SQL** | Presto/Trino engine | Easy queries |
| **Glue Catalog** | Schema management | Data discovery |
| **Partitioning** | Query optimization | Reduce costs |
| **CTAS** | Create Table As Select | Data transformation |
| **Federated Query** | Query multiple sources | Cross-data analysis |

---

## Basic Queries

### Data Exploration

```sql
-- Explore dataset
SELECT * FROM ml_data.training_data LIMIT 10;

-- Data profiling
SELECT
    COUNT(*) as total_rows,
    COUNT(DISTINCT customer_id) as unique_customers,
    AVG(amount) as avg_amount,
    MIN(amount) as min_amount,
    MAX(amount) as max_amount,
    STDDEV(amount) as std_amount
FROM ml_data.training_data;

-- Check for nulls
SELECT
    COUNT(*) as total,
    SUM(CASE WHEN feature1 IS NULL THEN 1 ELSE 0 END) as null_feature1,
    SUM(CASE WHEN feature2 IS NULL THEN 1 ELSE 0 END) as null_feature2
FROM ml_data.training_data;
```

### Feature Analysis

```sql
-- Feature distribution
SELECT
    feature_category,
    COUNT(*) as count,
    AVG(target) as avg_target
FROM ml_data.training_data
GROUP BY feature_category
ORDER BY count DESC;

-- Correlation proxy (using grouping)
SELECT
    NTILE(10) OVER (ORDER BY feature1) as decile,
    AVG(target) as avg_target,
    COUNT(*) as count
FROM ml_data.training_data
GROUP BY NTILE(10) OVER (ORDER BY feature1)
ORDER BY decile;
```

---

## Query Feature Store

```sql
-- Query Feature Store offline data
SELECT
    customer_id,
    total_purchases,
    avg_order_value,
    customer_segment,
    event_time
FROM "sagemaker_featurestore"."customer_features"
WHERE event_time >= CAST('2024-01-01' AS TIMESTAMP)
LIMIT 1000;

-- Point-in-time feature retrieval
SELECT
    t.customer_id,
    t.label_date,
    t.label,
    f.total_purchases,
    f.avg_order_value
FROM labels t
LEFT JOIN "sagemaker_featurestore"."customer_features" f
    ON t.customer_id = f.customer_id
    AND f.event_time <= t.label_date
WHERE f.event_time = (
    SELECT MAX(event_time)
    FROM "sagemaker_featurestore"."customer_features"
    WHERE customer_id = t.customer_id
    AND event_time <= t.label_date
);
```

---

## Create Table As Select (CTAS)

Transform and save query results.

```sql
-- Create processed training data
CREATE TABLE ml_data.processed_training
WITH (
    format = 'PARQUET',
    external_location = 's3://bucket/processed/',
    partitioned_by = ARRAY['year', 'month']
)
AS
SELECT
    customer_id,
    feature1,
    feature2,
    COALESCE(feature3, 0) as feature3,  -- Handle nulls
    target,
    year(date) as year,
    month(date) as month
FROM ml_data.raw_data
WHERE date >= DATE('2023-01-01');
```

---

## Partitioning for Cost Optimization

### Why Partition? (EXAM FAVORITE)

```
Without Partitioning:
Query: WHERE date = '2024-01-15'
Result: Scans ALL data (expensive!)

With Partitioning:
Query: WHERE year=2024 AND month=1 AND day=15
Result: Scans only that partition (cheap!)
```

### Partition Projection

```sql
-- Create table with partition projection (no crawling needed)
CREATE EXTERNAL TABLE ml_data.events (
    event_id string,
    user_id string,
    event_type string,
    amount double
)
PARTITIONED BY (
    year string,
    month string,
    day string
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe'
STORED AS PARQUET
LOCATION 's3://bucket/events/'
TBLPROPERTIES (
    'projection.enabled' = 'true',
    'projection.year.type' = 'integer',
    'projection.year.range' = '2020,2030',
    'projection.month.type' = 'integer',
    'projection.month.range' = '1,12',
    'projection.day.type' = 'integer',
    'projection.day.range' = '1,31',
    'storage.location.template' = 's3://bucket/events/year=${year}/month=${month}/day=${day}/'
);
```

---

## Cost Optimization

### Pricing: $5 per TB scanned

| Strategy | Savings | How |
|----------|---------|-----|
| **Partitioning** | Up to 99% | Scan only needed partitions |
| **Columnar Format** | 50-90% | Parquet/ORC read only needed columns |
| **Compression** | 50-80% | Less data to scan |
| **LIMIT clause** | Variable | Stop early |

### Exam Tip: Reduce Costs
1. Use Parquet/ORC format
2. Partition by frequently filtered columns
3. Use `LIMIT` for exploration
4. Select only needed columns (avoid `SELECT *`)

---

## Athena + ML Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                     ML DATA PIPELINE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Explore with Athena                                         │
│     SELECT * FROM raw_data LIMIT 100                           │
│                           │                                     │
│                           ▼                                     │
│  2. Profile & Analyze                                           │
│     - Check distributions                                       │
│     - Find missing values                                       │
│     - Identify correlations                                     │
│                           │                                     │
│                           ▼                                     │
│  3. Create Training Data (CTAS)                                │
│     CREATE TABLE processed AS SELECT ...                        │
│                           │                                     │
│                           ▼                                     │
│  4. Train with SageMaker                                        │
│     s3://bucket/processed/ → SageMaker                          │
│                           │                                     │
│                           ▼                                     │
│  5. Analyze Results with Athena                                 │
│     Query predictions, evaluation metrics                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Federated Query

Query multiple data sources.

```sql
-- Query across S3 and RDS
SELECT
    s3_data.customer_id,
    s3_data.ml_score,
    rds_data.customer_name,
    rds_data.account_status
FROM ml_data.predictions s3_data
JOIN "rds-catalog"."customers"."customer_table" rds_data
    ON s3_data.customer_id = rds_data.customer_id
WHERE s3_data.ml_score > 0.8;
```

---

## Exam Question Patterns

### Pattern 1: Ad-hoc Analysis
> "Quickly explore training data in S3..."

**Answer**: Athena (serverless, SQL)

### Pattern 2: Cost Optimization
> "Athena queries are expensive..."

**Answer**: Partition data, use Parquet, avoid SELECT *

### Pattern 3: Data Transformation
> "Create processed dataset from raw data..."

**Answer**: CTAS (Create Table As Select)

### Pattern 4: Feature Store Query
> "Query features from SageMaker Feature Store..."

**Answer**: Athena queries offline Feature Store

### Pattern 5: Cross-Source
> "Join S3 data with RDS database..."

**Answer**: Athena Federated Query

---

## Athena vs Alternatives

| Service | Use Case | Exam Scenario |
|---------|----------|---------------|
| **Athena** | Ad-hoc SQL queries | "Explore data quickly" |
| **Glue** | ETL transformation | "Transform data pipeline" |
| **EMR** | Complex processing | "Custom Spark jobs" |
| **Redshift** | Data warehouse | "BI and reporting" |

---

## Checklist

- [ ] Know Athena pricing model (per TB scanned)
- [ ] Understand partitioning for cost optimization
- [ ] Know CTAS for data transformation
- [ ] Understand Athena + Feature Store integration
- [ ] Know federated query capabilities

---

## Next Steps

After completing this module, proceed to:
- [16 - CloudWatch Alerts](../16-cloudwatch-alerts/) - ML monitoring and alerting
