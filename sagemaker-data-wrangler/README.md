# SageMaker Data Wrangler - Getting Started

A hands-on guide to learn Amazon SageMaker Data Wrangler using a simple customer dataset.

## What is Data Wrangler?

Data Wrangler is a visual data preparation tool in SageMaker Studio that helps you:
- Import data from various sources (S3, Athena, Redshift, etc.)
- Analyze data quality issues
- Transform and clean data without writing code
- Export prepared data for ML training

## Prerequisites

- AWS Account
- SageMaker Studio domain set up
- S3 bucket for storing data

## Step 1: Upload Sample Data to S3

```bash
# Upload the sample dataset to your S3 bucket
aws s3 cp sample_customers.csv s3://YOUR-BUCKET-NAME/data-wrangler-demo/
```

## Step 2: Open SageMaker Studio

1. Go to **AWS Console** > **SageMaker** > **Studio**
2. Click **Open Studio** for your user profile

## Step 3: Create a New Data Wrangler Flow

1. In Studio, click **File** > **New** > **Data Wrangler Flow**
2. Wait for the flow to initialize (creates a `.flow` file)

## Step 4: Import Your Data

1. Click **Import data**
2. Select **Amazon S3** as the data source
3. Navigate to your bucket and select `sample_customers.csv`
4. Click **Import**

## Step 5: Explore Data Quality (Key Feature!)

After import, click on your dataset node, then:

1. Click **Add analysis**
2. Choose **Data Quality and Insights Report**
3. Set target column to `is_premium` (our prediction target)
4. Click **Create**

### What the Report Shows:
- **Missing values**: Rows 4, 6, 14 have missing data
- **Outliers**: Age values like -5 and 200 are invalid
- **Data types**: Automatic type detection
- **Statistics**: Mean, median, distributions

## Step 6: Add Transformations

Click the **+** on your data node and select **Add transform**. Try these:

### Transform 1: Handle Missing Values
1. Click **Add step** > **Handle missing**
2. Select `email` column
3. Choose **Drop missing** or **Fill with custom value**

### Transform 2: Fix Invalid Ages
1. Click **Add step** > **Filter rows**
2. Condition: `age > 0 AND age < 120`
3. This removes rows with invalid ages

### Transform 3: Parse Date
1. Click **Add step** > **Parse column as type**
2. Select `signup_date`
3. Target type: **Date**

### Transform 4: Create New Feature
1. Click **Add step** > **Custom formula**
2. Formula: `total_spent / purchase_count`
3. New column name: `avg_order_value`

### Transform 5: Encode Categorical
1. Click **Add step** > **Encode categorical**
2. Select `region` column
3. Choose **One-hot encode**

## Step 7: Preview Results

- Click **Preview** at any step to see transformed data
- Check row counts to verify filters worked

## Step 8: Export Options

Click **Export** to choose output:

| Option | Use Case |
|--------|----------|
| **S3** | Save CSV/Parquet to S3 |
| **Pipeline** | Create SageMaker Pipeline |
| **Python Code** | Generate transformation script |
| **Feature Store** | Store features for reuse |

For learning, try **Export to S3** first:
1. Select S3 destination
2. Choose Parquet format (efficient for ML)
3. Run the export job

## Sample Dataset Details

The `sample_customers.csv` contains intentional issues for practice:

| Issue | Rows | Column |
|-------|------|--------|
| Missing email | 6, 14 | email |
| Missing income | 4 | income |
| Invalid age (negative) | 8 | age |
| Invalid age (too high) | 15 | age |
| Invalid date format | 11 | signup_date |

## Common Transformations Reference

| Task | Transform Type |
|------|---------------|
| Remove duplicates | Manage rows > Drop duplicates |
| Rename columns | Manage columns > Rename |
| Change data type | Parse column as type |
| Filter rows | Filter rows |
| Split column | Split column |
| Join datasets | Join (requires 2nd dataset) |
| Group & aggregate | Group by |

## Clean Up

To avoid charges:
1. Delete the Data Wrangler `.flow` file
2. Stop your Studio instance
3. Delete S3 data if not needed

## Next Steps

After mastering basics:
1. Try importing from **Athena** or **Redshift**
2. Create a **SageMaker Pipeline** from your flow
3. Use **Feature Store** to save reusable features
4. Explore **Custom transforms** with Pandas/PySpark
