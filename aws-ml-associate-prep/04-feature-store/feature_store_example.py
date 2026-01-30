"""
SageMaker Feature Store Complete Example

This script demonstrates creating, populating, and querying a Feature Store
for ML workflows.

EXAM TIPS:
- Know Online vs Offline Store use cases
- Understand record identifier and event time requirements
- Know ingestion patterns (streaming vs batch)
- Understand point-in-time queries for training
"""

import sagemaker
from sagemaker.feature_store.feature_group import FeatureGroup
from sagemaker.feature_store.feature_definition import (
    FeatureDefinition,
    FeatureTypeEnum
)
from sagemaker.feature_store.inputs import (
    FeatureValue,
    OnlineStoreConfig,
    OfflineStoreConfig,
    S3StorageConfig,
    TtlDuration,
    OnlineStoreConfigUpdate
)
import pandas as pd
import numpy as np
import time
import boto3


# Initialize SageMaker session
session = sagemaker.Session()
role = sagemaker.get_execution_role()
bucket = session.default_bucket()
region = session.boto_region_name


# ============================================================================
# PART 1: Create Feature Group
# ============================================================================

def create_customer_feature_group():
    """
    Create a feature group for customer features.

    EXAM TIP: Every feature group needs:
    - Record identifier (primary key)
    - Event time (timestamp for versioning)
    """

    feature_group_name = "customer-ml-features"

    # Define feature schema
    # EXAM TIP: Only 3 types: STRING, INTEGRAL, FRACTIONAL
    feature_definitions = [
        # Required fields
        FeatureDefinition(
            feature_name="customer_id",
            feature_type=FeatureTypeEnum.STRING
        ),
        FeatureDefinition(
            feature_name="event_time",
            feature_type=FeatureTypeEnum.FRACTIONAL  # Unix timestamp
        ),

        # Customer demographic features
        FeatureDefinition(
            feature_name="age",
            feature_type=FeatureTypeEnum.INTEGRAL
        ),
        FeatureDefinition(
            feature_name="tenure_months",
            feature_type=FeatureTypeEnum.INTEGRAL
        ),
        FeatureDefinition(
            feature_name="account_type",
            feature_type=FeatureTypeEnum.STRING
        ),

        # Behavioral features
        FeatureDefinition(
            feature_name="total_transactions",
            feature_type=FeatureTypeEnum.INTEGRAL
        ),
        FeatureDefinition(
            feature_name="avg_transaction_amount",
            feature_type=FeatureTypeEnum.FRACTIONAL
        ),
        FeatureDefinition(
            feature_name="total_spend",
            feature_type=FeatureTypeEnum.FRACTIONAL
        ),
        FeatureDefinition(
            feature_name="days_since_last_transaction",
            feature_type=FeatureTypeEnum.INTEGRAL
        ),

        # Engagement features
        FeatureDefinition(
            feature_name="login_frequency",
            feature_type=FeatureTypeEnum.FRACTIONAL
        ),
        FeatureDefinition(
            feature_name="support_tickets",
            feature_type=FeatureTypeEnum.INTEGRAL
        ),

        # Derived features
        FeatureDefinition(
            feature_name="customer_segment",
            feature_type=FeatureTypeEnum.STRING
        ),
        FeatureDefinition(
            feature_name="churn_risk_score",
            feature_type=FeatureTypeEnum.FRACTIONAL
        ),
    ]

    # Create feature group
    feature_group = FeatureGroup(
        name=feature_group_name,
        sagemaker_session=session,
        feature_definitions=feature_definitions
    )

    # Create with both Online and Offline stores
    # EXAM TIP: Enable both for training + real-time inference
    feature_group.create(
        s3_uri=f"s3://{bucket}/feature-store/{feature_group_name}/",
        record_identifier_name="customer_id",
        event_time_feature_name="event_time",
        role_arn=role,
        enable_online_store=True,  # For real-time inference
        # Online store config with TTL
        online_store_config=OnlineStoreConfig(
            enable_online_store=True,
            ttl_duration=TtlDuration(
                unit="Days",
                value=90  # Records expire after 90 days
            )
        ),
        # Offline store for training
        offline_store_config=OfflineStoreConfig(
            s3_storage_config=S3StorageConfig(
                s3_uri=f"s3://{bucket}/feature-store/{feature_group_name}/"
            )
        ),
        description="Customer features for churn prediction model",
        tags=[
            {"Key": "Project", "Value": "ChurnPrediction"},
            {"Key": "Team", "Value": "DataScience"}
        ]
    )

    # Wait for feature group to be created
    print("Creating feature group...")
    while True:
        status = feature_group.describe().get("FeatureGroupStatus")
        if status == "Created":
            print(f"Feature group '{feature_group_name}' created successfully!")
            break
        elif status == "CreateFailed":
            raise Exception(f"Feature group creation failed")
        time.sleep(5)

    return feature_group


# ============================================================================
# PART 2: Ingest Features
# ============================================================================

def generate_sample_data(n_customers=1000):
    """
    Generate sample customer feature data.
    """

    np.random.seed(42)

    data = {
        "customer_id": [f"CUST_{i:06d}" for i in range(n_customers)],
        "event_time": [time.time()] * n_customers,
        "age": np.random.randint(18, 80, n_customers),
        "tenure_months": np.random.randint(1, 120, n_customers),
        "account_type": np.random.choice(["basic", "premium", "enterprise"], n_customers),
        "total_transactions": np.random.randint(0, 500, n_customers),
        "avg_transaction_amount": np.random.uniform(10, 500, n_customers).round(2),
        "total_spend": np.random.uniform(100, 50000, n_customers).round(2),
        "days_since_last_transaction": np.random.randint(0, 365, n_customers),
        "login_frequency": np.random.uniform(0, 10, n_customers).round(2),
        "support_tickets": np.random.randint(0, 20, n_customers),
        "customer_segment": np.random.choice(["low_value", "medium_value", "high_value"], n_customers),
        "churn_risk_score": np.random.uniform(0, 1, n_customers).round(4),
    }

    return pd.DataFrame(data)


def batch_ingest_features(feature_group, df):
    """
    Batch ingest features from DataFrame.

    EXAM TIP: Use ingest() for bulk data, put_record() for streaming
    """

    print(f"Ingesting {len(df)} records...")

    # Batch ingest
    # EXAM TIP: max_workers controls parallelism
    feature_group.ingest(
        data_frame=df,
        max_workers=3,
        wait=True  # Wait for completion
    )

    print("Batch ingestion complete!")


def streaming_ingest_features(feature_group, records):
    """
    Stream ingest individual records.

    EXAM TIP: Use for real-time feature updates
    """

    for record in records:
        # Convert record to Feature Store format
        feature_values = [
            FeatureValue(feature_name=k, value_as_string=str(v))
            for k, v in record.items()
        ]

        feature_group.put_record(record=feature_values)

    print(f"Streamed {len(records)} records")


# ============================================================================
# PART 3: Query Features
# ============================================================================

def query_online_store(feature_group, customer_ids):
    """
    Query Online Store for real-time inference.

    EXAM TIP: Online Store returns only latest values
    Latency: <10ms
    """

    results = []

    for customer_id in customer_ids:
        # Get single record
        record = feature_group.get_record(
            record_identifier_value_as_string=customer_id
        )
        results.append(record)

    return results


def batch_get_online_store(feature_group_name, customer_ids):
    """
    Batch get from Online Store.

    EXAM TIP: More efficient for multiple records
    """

    from sagemaker.feature_store.feature_store import FeatureStore
    from sagemaker.feature_store.inputs import Identifier

    feature_store = FeatureStore(sagemaker_session=session)

    # Create identifiers
    identifiers = [
        Identifier(
            feature_group_name=feature_group_name,
            record_identifiers_value_as_string=[cid]
        )
        for cid in customer_ids
    ]

    # Batch get
    response = feature_store.batch_get_record(identifiers=identifiers)

    return response


def query_offline_store(feature_group, query_string):
    """
    Query Offline Store using Athena.

    EXAM TIP: Offline Store contains full history
    Use for training data extraction
    """

    # Create query object
    query = feature_group.athena_query()

    # Run query
    query.run(
        query_string=query_string,
        output_location=f"s3://{bucket}/athena-results/"
    )

    # Wait for completion
    query.wait()

    # Get results as DataFrame
    df = query.as_dataframe()

    return df


def point_in_time_query(feature_group_name, label_timestamps):
    """
    Point-in-time query to avoid data leakage.

    EXAM TIP: Critical for ML training
    Retrieves features as they were at label time
    """

    # SQL for point-in-time correct features
    # This gets the latest feature values before each label timestamp
    query = f"""
    WITH labeled_data AS (
        SELECT
            customer_id,
            label_timestamp,
            label
        FROM labels_table
    ),
    feature_history AS (
        SELECT
            customer_id,
            event_time,
            total_transactions,
            avg_transaction_amount,
            total_spend,
            customer_segment,
            churn_risk_score,
            ROW_NUMBER() OVER (
                PARTITION BY customer_id
                ORDER BY event_time DESC
            ) as rn
        FROM "sagemaker_featurestore"."{feature_group_name}"
    )
    SELECT
        l.customer_id,
        l.label_timestamp,
        l.label,
        f.total_transactions,
        f.avg_transaction_amount,
        f.total_spend,
        f.customer_segment,
        f.churn_risk_score
    FROM labeled_data l
    JOIN feature_history f
        ON l.customer_id = f.customer_id
        AND f.event_time <= l.label_timestamp
    WHERE f.rn = 1
    """

    return query


# ============================================================================
# PART 4: Feature Store for Training
# ============================================================================

def create_training_dataset(feature_group_name, start_date, end_date):
    """
    Create training dataset from Feature Store.

    EXAM TIP: Use Offline Store for training data extraction
    """

    query_string = f"""
    SELECT
        customer_id,
        age,
        tenure_months,
        account_type,
        total_transactions,
        avg_transaction_amount,
        total_spend,
        days_since_last_transaction,
        login_frequency,
        support_tickets,
        customer_segment,
        churn_risk_score
    FROM "sagemaker_featurestore"."{feature_group_name}"
    WHERE event_time >= {start_date}
      AND event_time <= {end_date}
    """

    # This would be used with the athena_query() method
    return query_string


def create_sagemaker_training_input(feature_group_name):
    """
    Create SageMaker training input from Feature Store.

    EXAM TIP: Feature Store integrates directly with SageMaker training
    """

    from sagemaker.inputs import TrainingInput

    # Query and save to S3
    feature_group = FeatureGroup(name=feature_group_name, sagemaker_session=session)
    query = feature_group.athena_query()

    query.run(
        query_string=f'SELECT * FROM "sagemaker_featurestore"."{feature_group_name}"',
        output_location=f"s3://{bucket}/training-data/"
    )
    query.wait()

    # Create training input
    train_input = TrainingInput(
        s3_data=f"s3://{bucket}/training-data/",
        content_type="text/csv"
    )

    return train_input


# ============================================================================
# PART 5: Feature Store for Inference
# ============================================================================

def real_time_inference_pattern(feature_group, customer_id, endpoint_name):
    """
    Pattern: Real-time inference with Feature Store.

    1. Receive inference request with customer_id
    2. Fetch features from Online Store
    3. Send to SageMaker endpoint
    """

    # Step 1: Get features from Online Store
    record = feature_group.get_record(
        record_identifier_value_as_string=customer_id
    )

    # Step 2: Extract feature values
    features = {r['FeatureName']: r['ValueAsString'] for r in record['Record']}

    # Step 3: Prepare for inference (example format)
    inference_payload = [
        float(features.get('age', 0)),
        float(features.get('tenure_months', 0)),
        float(features.get('total_transactions', 0)),
        float(features.get('avg_transaction_amount', 0)),
        float(features.get('total_spend', 0)),
        float(features.get('days_since_last_transaction', 0)),
        float(features.get('login_frequency', 0)),
        float(features.get('support_tickets', 0)),
    ]

    # Step 4: Invoke endpoint
    runtime = boto3.client('sagemaker-runtime')
    response = runtime.invoke_endpoint(
        EndpointName=endpoint_name,
        ContentType='text/csv',
        Body=','.join(map(str, inference_payload))
    )

    prediction = response['Body'].read().decode()
    return prediction


# ============================================================================
# PART 6: Feature Group Management
# ============================================================================

def list_feature_groups():
    """
    List all feature groups.
    """

    sm_client = boto3.client('sagemaker')

    response = sm_client.list_feature_groups()

    for fg in response['FeatureGroupSummaries']:
        print(f"Name: {fg['FeatureGroupName']}, Status: {fg['FeatureGroupStatus']}")

    return response['FeatureGroupSummaries']


def describe_feature_group(feature_group_name):
    """
    Get details of a feature group.
    """

    feature_group = FeatureGroup(name=feature_group_name, sagemaker_session=session)
    description = feature_group.describe()

    print(f"Name: {description['FeatureGroupName']}")
    print(f"Status: {description['FeatureGroupStatus']}")
    print(f"Online Store: {description.get('OnlineStoreConfig', {}).get('EnableOnlineStore')}")
    print(f"Offline Store: {description.get('OfflineStoreConfig')}")
    print(f"Features: {[f['FeatureName'] for f in description['FeatureDefinitions']]}")

    return description


def delete_feature_group(feature_group_name):
    """
    Delete a feature group.

    EXAM TIP: Deleting feature group doesn't delete S3 data
    """

    feature_group = FeatureGroup(name=feature_group_name, sagemaker_session=session)
    feature_group.delete()

    print(f"Feature group '{feature_group_name}' deleted")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("SageMaker Feature Store Example")
    print("=" * 50)
    print("\nKey concepts demonstrated:")
    print("1. Creating feature groups with Online + Offline stores")
    print("2. Batch and streaming ingestion")
    print("3. Online Store queries (real-time)")
    print("4. Offline Store queries (Athena)")
    print("5. Point-in-time queries for training")
    print("6. Integration with SageMaker training and inference")

    # Example usage (uncomment to run):
    # feature_group = create_customer_feature_group()
    # df = generate_sample_data(100)
    # batch_ingest_features(feature_group, df)
