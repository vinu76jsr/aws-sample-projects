"""
AWS Glue ETL Job for ML Data Preparation

This script demonstrates a complete Glue ETL job that prepares data for ML training.
It covers common transformations, data quality checks, and best practices.

EXAM TIPS:
- Know the DynamicFrame vs DataFrame difference
- Understand job bookmarks for incremental processing
- Know common transformations (ApplyMapping, Filter, Join)
- Understand partitioning for query performance
"""

import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.functions import col, when, lit, year, month, dayofmonth
from pyspark.sql.functions import mean, stddev, count, isnan, isnull
from pyspark.sql.types import DoubleType, IntegerType, StringType


# ============================================================================
# INITIALIZATION
# ============================================================================

# Get job arguments
# EXAM TIP: getResolvedOptions parses command-line arguments
args = getResolvedOptions(sys.argv, [
    'JOB_NAME',
    'source_database',
    'source_table',
    'target_path',
    'target_database',
    'target_table'
])

# Initialize Spark and Glue contexts
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)

# Initialize job with bookmarks support
# EXAM TIP: job.init() enables job bookmarks
job.init(args['JOB_NAME'], args)


# ============================================================================
# EXTRACT - Read from Data Catalog
# ============================================================================

def extract_data():
    """
    Read data from Glue Data Catalog.

    EXAM TIP: create_dynamic_frame.from_catalog reads from Data Catalog
    Alternative: from_options for direct S3 read
    """

    # Read from Data Catalog (recommended)
    datasource = glueContext.create_dynamic_frame.from_catalog(
        database=args['source_database'],
        table_name=args['source_table'],
        transformation_ctx="datasource"  # Required for bookmarks
    )

    print(f"Records read: {datasource.count()}")
    print(f"Schema: {datasource.schema()}")

    return datasource


def extract_from_s3():
    """
    Alternative: Read directly from S3.

    EXAM TIP: Use this when data isn't in Data Catalog
    """

    datasource = glueContext.create_dynamic_frame.from_options(
        connection_type="s3",
        connection_options={
            "paths": ["s3://bucket/raw/data/"],
            "recurse": True,
            # Enable bookmarks for incremental processing
            "transformation_ctx": "s3_source"
        },
        format="csv",
        format_options={
            "withHeader": True,
            "separator": ","
        },
        transformation_ctx="s3_source"
    )

    return datasource


# ============================================================================
# TRANSFORM - Data Cleaning and Feature Engineering
# ============================================================================

def clean_and_transform(dynamic_frame):
    """
    Apply transformations for ML data preparation.

    EXAM TIP: Know these common transformations:
    - ApplyMapping: Rename/cast columns
    - Filter: Remove rows
    - DropNullFields: Remove null columns
    - ResolveChoice: Handle ambiguous types
    """

    # 1. Apply schema mapping (rename and cast columns)
    # EXAM TIP: ApplyMapping is the go-to for schema transformation
    mapped = ApplyMapping.apply(
        frame=dynamic_frame,
        mappings=[
            ("customer_id", "string", "customer_id", "long"),
            ("customer_name", "string", "name", "string"),
            ("purchase_amount", "string", "amount", "double"),
            ("purchase_date", "string", "date", "timestamp"),
            ("product_category", "string", "category", "string"),
            ("customer_age", "string", "age", "int"),
            ("customer_region", "string", "region", "string")
        ],
        transformation_ctx="mapped"
    )

    # 2. Resolve any type ambiguities
    # EXAM TIP: Use when columns have multiple possible types
    resolved = ResolveChoice.apply(
        frame=mapped,
        choice="cast:double",  # Cast ambiguous types to double
        transformation_ctx="resolved"
    )

    # 3. Drop records with null keys
    # EXAM TIP: DropNullFields removes columns that are entirely null
    cleaned = DropNullFields.apply(
        frame=resolved,
        transformation_ctx="cleaned"
    )

    return cleaned


def advanced_transformations(dynamic_frame):
    """
    Advanced transformations using Spark DataFrame.

    EXAM TIP: Convert to DataFrame for complex transformations,
    then back to DynamicFrame for Glue operations.
    """

    # Convert DynamicFrame to Spark DataFrame
    df = dynamic_frame.toDF()

    # Handle missing values
    # Fill numeric nulls with median
    numeric_cols = ['amount', 'age']
    for col_name in numeric_cols:
        median_val = df.approxQuantile(col_name, [0.5], 0.01)[0]
        df = df.fillna({col_name: median_val})

    # Fill categorical nulls with mode
    df = df.fillna({'category': 'Unknown', 'region': 'Unknown'})

    # Remove outliers (values beyond 3 standard deviations)
    for col_name in numeric_cols:
        mean_val = df.select(mean(col(col_name))).collect()[0][0]
        std_val = df.select(stddev(col(col_name))).collect()[0][0]
        lower_bound = mean_val - 3 * std_val
        upper_bound = mean_val + 3 * std_val
        df = df.filter((col(col_name) >= lower_bound) & (col(col_name) <= upper_bound))

    # Feature engineering: Add date components
    df = df.withColumn("year", year(col("date")))
    df = df.withColumn("month", month(col("date")))
    df = df.withColumn("day", dayofmonth(col("date")))

    # Feature engineering: Create derived features
    df = df.withColumn("amount_category",
        when(col("amount") < 100, "low")
        .when(col("amount") < 500, "medium")
        .otherwise("high")
    )

    # Feature engineering: Age groups
    df = df.withColumn("age_group",
        when(col("age") < 25, "young")
        .when(col("age") < 45, "middle")
        .when(col("age") < 65, "senior")
        .otherwise("elderly")
    )

    # Convert back to DynamicFrame
    transformed = DynamicFrame.fromDF(df, glueContext, "transformed")

    return transformed


def data_quality_checks(dynamic_frame):
    """
    Perform data quality checks.

    EXAM TIP: Glue Data Quality provides built-in rules,
    but you can also implement custom checks.
    """

    df = dynamic_frame.toDF()

    # Check for nulls in critical columns
    critical_cols = ['customer_id', 'amount', 'date']
    null_counts = {}
    total_records = df.count()

    for col_name in critical_cols:
        null_count = df.filter(col(col_name).isNull()).count()
        null_counts[col_name] = null_count
        null_percentage = (null_count / total_records) * 100

        if null_percentage > 5:  # Fail if more than 5% nulls
            raise Exception(f"Data quality check failed: {col_name} has {null_percentage:.2f}% nulls")

    # Check for duplicates
    distinct_count = df.select('customer_id', 'date').distinct().count()
    duplicate_rate = 1 - (distinct_count / total_records)

    if duplicate_rate > 0.01:  # Fail if more than 1% duplicates
        print(f"Warning: {duplicate_rate:.2%} duplicate records detected")

    # Log quality metrics
    print(f"Data Quality Report:")
    print(f"  Total records: {total_records}")
    print(f"  Null counts: {null_counts}")
    print(f"  Duplicate rate: {duplicate_rate:.2%}")

    return dynamic_frame


# ============================================================================
# FILTER - Remove Unwanted Records
# ============================================================================

def filter_data(dynamic_frame):
    """
    Filter records based on business rules.

    EXAM TIP: Filter.apply uses a lambda function for conditions
    """

    # Filter: Keep only valid records
    filtered = Filter.apply(
        frame=dynamic_frame,
        f=lambda x: (
            x["amount"] is not None and
            x["amount"] > 0 and
            x["customer_id"] is not None
        ),
        transformation_ctx="filtered"
    )

    print(f"Records after filtering: {filtered.count()}")
    return filtered


# ============================================================================
# JOIN - Combine Multiple Data Sources
# ============================================================================

def join_datasets(frame1, frame2):
    """
    Join two DynamicFrames.

    EXAM TIP: For large joins, consider:
    - Increasing DPU worker type (G.2X, G.4X)
    - Partitioning data
    - Using broadcast joins for small tables
    """

    joined = Join.apply(
        frame1=frame1,
        frame2=frame2,
        keys1=["customer_id"],
        keys2=["customer_id"],
        transformation_ctx="joined"
    )

    return joined


# ============================================================================
# LOAD - Write to Target
# ============================================================================

def load_to_s3(dynamic_frame):
    """
    Write transformed data to S3.

    EXAM TIP: Know the output formats:
    - Parquet: Best for analytics (columnar, compressed)
    - JSON: Semi-structured data
    - CSV: Simple, universal
    """

    # Convert to DataFrame for partitioning
    df = dynamic_frame.toDF()

    # Repartition for optimal file sizes
    # EXAM TIP: Too many small files = poor query performance
    # Target: 128MB - 1GB per file
    df = df.repartition(10)

    # Convert back to DynamicFrame
    output_frame = DynamicFrame.fromDF(df, glueContext, "output")

    # Write with partitioning
    # EXAM TIP: Partition by frequently filtered columns
    glueContext.write_dynamic_frame.from_options(
        frame=output_frame,
        connection_type="s3",
        connection_options={
            "path": args['target_path'],
            "partitionKeys": ["year", "month"]  # Partition by date
        },
        format="parquet",
        format_options={
            "compression": "snappy"  # Default, good balance
        },
        transformation_ctx="output"
    )

    print(f"Data written to: {args['target_path']}")


def load_to_catalog(dynamic_frame):
    """
    Write to S3 and update Data Catalog.

    EXAM TIP: Use catalog tables for seamless Athena integration
    """

    glueContext.write_dynamic_frame.from_catalog(
        frame=dynamic_frame,
        database=args['target_database'],
        table_name=args['target_table'],
        transformation_ctx="catalog_output"
    )


def load_with_options(dynamic_frame):
    """
    Write with different format options.
    """

    # Option 1: Parquet with Snappy compression (recommended for analytics)
    glueContext.write_dynamic_frame.from_options(
        frame=dynamic_frame,
        connection_type="s3",
        connection_options={"path": "s3://bucket/output/parquet/"},
        format="parquet",
        format_options={"compression": "snappy"}
    )

    # Option 2: JSON with Gzip compression
    glueContext.write_dynamic_frame.from_options(
        frame=dynamic_frame,
        connection_type="s3",
        connection_options={"path": "s3://bucket/output/json/"},
        format="json",
        format_options={"compression": "gzip"}
    )

    # Option 3: CSV (no compression, for compatibility)
    glueContext.write_dynamic_frame.from_options(
        frame=dynamic_frame,
        connection_type="s3",
        connection_options={"path": "s3://bucket/output/csv/"},
        format="csv",
        format_options={
            "writeHeader": True,
            "separator": ","
        }
    )


# ============================================================================
# MAIN ETL FLOW
# ============================================================================

def main():
    """
    Main ETL pipeline.
    """

    print("Starting ETL job...")

    # Extract
    print("Extracting data...")
    raw_data = extract_data()

    # Transform
    print("Cleaning and transforming data...")
    cleaned_data = clean_and_transform(raw_data)

    # Data quality checks
    print("Running data quality checks...")
    validated_data = data_quality_checks(cleaned_data)

    # Advanced transformations
    print("Applying advanced transformations...")
    transformed_data = advanced_transformations(validated_data)

    # Filter
    print("Filtering data...")
    filtered_data = filter_data(transformed_data)

    # Load
    print("Loading data to S3...")
    load_to_s3(filtered_data)

    print("ETL job completed successfully!")


if __name__ == "__main__":
    main()

    # CRITICAL: Commit job for bookmarks
    # EXAM TIP: job.commit() must be called for bookmarks to work
    job.commit()
