"""
Amazon SageMaker End-to-End Example

This script demonstrates the complete SageMaker workflow:
1. Data preparation and upload to S3
2. Training with built-in XGBoost
3. Hyperparameter tuning
4. Model deployment
5. Inference
6. Cleanup

EXAM TIPS:
- Know the difference between Estimator (training) and Predictor (inference)
- Understand S3 paths for input/output
- Know when to use Spot instances (cost savings, with checkpointing)
- Understand instance types for different workloads
"""

import sagemaker
from sagemaker import get_execution_role
from sagemaker.xgboost import XGBoost
from sagemaker.tuner import (
    HyperparameterTuner,
    IntegerParameter,
    ContinuousParameter
)
from sagemaker.model import Model
from sagemaker.serializers import CSVSerializer
from sagemaker.deserializers import JSONDeserializer
import boto3


# Initialize SageMaker session and role
session = sagemaker.Session()
role = get_execution_role()
bucket = session.default_bucket()
prefix = 'sagemaker-xgboost-demo'


# ============================================================================
# PART 1: Basic Training Job
# ============================================================================

def run_basic_training():
    """
    Run a basic training job with XGBoost built-in algorithm.

    EXAM TIPS:
    - instance_type determines compute (ml.m5 for CPU, ml.p3 for GPU)
    - instance_count > 1 enables distributed training
    - hyperparameters are passed to the training script
    """

    # Define the estimator
    xgb_estimator = XGBoost(
        entry_point='train_xgboost.py',  # Your training script
        role=role,
        instance_count=1,
        instance_type='ml.m5.xlarge',     # General purpose instance
        framework_version='1.5-1',
        py_version='py3',
        hyperparameters={
            'objective': 'binary:logistic',
            'num_round': 100,
            'max_depth': 5,
            'eta': 0.2,
            'subsample': 0.8,
            'colsample_bytree': 0.8
        },
        output_path=f's3://{bucket}/{prefix}/output',

        # Cost optimization with Spot instances (EXAM FAVORITE)
        use_spot_instances=True,
        max_wait=3600,  # Maximum time to wait for Spot capacity
        max_run=1800,   # Maximum training time

        # Checkpointing - REQUIRED for Spot instances
        checkpoint_s3_uri=f's3://{bucket}/{prefix}/checkpoints',

        # Enable network isolation for security (EXAM TIP)
        enable_network_isolation=False,  # Set True for compliance

        # Tags for cost tracking
        tags=[
            {'Key': 'Project', 'Value': 'ML-Demo'},
            {'Key': 'Environment', 'Value': 'Development'}
        ]
    )

    # Define input channels
    # EXAM TIP: Channel names become directories under /opt/ml/input/data/
    train_input = sagemaker.inputs.TrainingInput(
        s3_data=f's3://{bucket}/{prefix}/train/',
        content_type='text/csv',
        input_mode='File'  # or 'Pipe' for large datasets
    )

    validation_input = sagemaker.inputs.TrainingInput(
        s3_data=f's3://{bucket}/{prefix}/validation/',
        content_type='text/csv'
    )

    # Start training
    xgb_estimator.fit({
        'train': train_input,
        'validation': validation_input
    })

    return xgb_estimator


# ============================================================================
# PART 2: Hyperparameter Tuning
# ============================================================================

def run_hyperparameter_tuning():
    """
    Run hyperparameter tuning job.

    EXAM TIPS:
    - Bayesian strategy is default and most efficient
    - Use Random for large search spaces
    - max_jobs limits total training jobs
    - max_parallel_jobs controls concurrency
    """

    # Base estimator
    xgb_estimator = XGBoost(
        entry_point='train_xgboost.py',
        role=role,
        instance_count=1,
        instance_type='ml.m5.xlarge',
        framework_version='1.5-1',
        py_version='py3',
        hyperparameters={
            'objective': 'binary:logistic',
            'num_round': 100
        }
    )

    # Define hyperparameter ranges
    hyperparameter_ranges = {
        'eta': ContinuousParameter(0.01, 0.3),          # Learning rate
        'max_depth': IntegerParameter(3, 10),            # Tree depth
        'subsample': ContinuousParameter(0.5, 1.0),      # Row sampling
        'colsample_bytree': ContinuousParameter(0.5, 1.0),  # Column sampling
        'min_child_weight': IntegerParameter(1, 10)      # Min samples per leaf
    }

    # Create tuner
    tuner = HyperparameterTuner(
        estimator=xgb_estimator,
        objective_metric_name='validation:auc',
        objective_type='Maximize',
        hyperparameter_ranges=hyperparameter_ranges,
        max_jobs=20,              # Total tuning jobs
        max_parallel_jobs=4,       # Concurrent jobs
        strategy='Bayesian',       # Bayesian, Random, Grid, or Hyperband

        # Early stopping (EXAM TIP: Hyperband does this automatically)
        early_stopping_type='Auto'
    )

    # Start tuning
    tuner.fit({
        'train': f's3://{bucket}/{prefix}/train/',
        'validation': f's3://{bucket}/{prefix}/validation/'
    })

    # Get best training job
    best_job = tuner.best_training_job()
    print(f"Best training job: {best_job}")

    return tuner


# ============================================================================
# PART 3: Model Deployment
# ============================================================================

def deploy_real_time_endpoint(estimator):
    """
    Deploy model to real-time endpoint.

    EXAM TIPS:
    - Real-time for low-latency, consistent traffic
    - Serverless for intermittent traffic (cost savings)
    - Async for large payloads (up to 1GB)
    """

    # Deploy to real-time endpoint
    predictor = estimator.deploy(
        initial_instance_count=1,
        instance_type='ml.m5.large',  # Smaller instance for inference
        endpoint_name='xgboost-realtime-endpoint',
        serializer=CSVSerializer(),
        deserializer=JSONDeserializer()
    )

    return predictor


def deploy_serverless_endpoint(estimator):
    """
    Deploy to serverless endpoint.

    EXAM TIP: Serverless is ideal for:
    - Intermittent or unpredictable traffic
    - Cost optimization (pay per inference)
    - Trade-off: Cold start latency
    """

    from sagemaker.serverless import ServerlessInferenceConfig

    serverless_config = ServerlessInferenceConfig(
        memory_size_in_mb=2048,  # 1024, 2048, 3072, 4096, 5120, or 6144
        max_concurrency=10       # Max concurrent invocations
    )

    predictor = estimator.deploy(
        serverless_inference_config=serverless_config,
        endpoint_name='xgboost-serverless-endpoint',
        serializer=CSVSerializer(),
        deserializer=JSONDeserializer()
    )

    return predictor


def deploy_async_endpoint(estimator):
    """
    Deploy to async endpoint for large payloads.

    EXAM TIP: Async endpoints support:
    - Payloads up to 1GB (vs 6MB for real-time)
    - Longer processing times
    - S3 input/output
    - Auto-scaling to zero
    """

    from sagemaker.async_inference import AsyncInferenceConfig

    async_config = AsyncInferenceConfig(
        output_path=f's3://{bucket}/{prefix}/async-output/',
        max_concurrent_invocations_per_instance=4,

        # Optional: SNS notifications
        # notification_config={
        #     'SuccessTopic': 'arn:aws:sns:...',
        #     'ErrorTopic': 'arn:aws:sns:...'
        # }
    )

    predictor = estimator.deploy(
        async_inference_config=async_config,
        instance_type='ml.m5.large',
        initial_instance_count=1,
        endpoint_name='xgboost-async-endpoint'
    )

    return predictor


# ============================================================================
# PART 4: Batch Transform
# ============================================================================

def run_batch_transform(estimator):
    """
    Run batch transform for offline predictions.

    EXAM TIP: Use batch transform when:
    - Processing large datasets offline
    - Don't need real-time predictions
    - Want to precompute predictions
    """

    # Create transformer
    transformer = estimator.transformer(
        instance_count=1,
        instance_type='ml.m5.xlarge',
        output_path=f's3://{bucket}/{prefix}/batch-output/',

        # How to handle input/output
        strategy='MultiRecord',     # or 'SingleRecord'
        assemble_with='Line',       # or 'None'

        # Max payload size per request
        max_payload=6  # MB
    )

    # Run batch transform
    transformer.transform(
        data=f's3://{bucket}/{prefix}/test/',
        content_type='text/csv',
        split_type='Line',        # Split input by line
        join_source='Input'       # Join predictions with input
    )

    # Wait for completion
    transformer.wait()


# ============================================================================
# PART 5: Multi-Variant Endpoint (A/B Testing)
# ============================================================================

def deploy_multi_variant_endpoint():
    """
    Deploy endpoint with multiple model variants for A/B testing.

    EXAM TIP: Multi-variant endpoints allow:
    - A/B testing different models
    - Canary deployments
    - Shadow testing
    """

    from sagemaker.model import Model
    from sagemaker.predictor import Predictor

    # Create models from artifacts
    model_a = Model(
        image_uri=sagemaker.image_uris.retrieve('xgboost', session.boto_region_name, '1.5-1'),
        model_data=f's3://{bucket}/{prefix}/model-a/model.tar.gz',
        role=role,
        name='model-variant-a'
    )

    model_b = Model(
        image_uri=sagemaker.image_uris.retrieve('xgboost', session.boto_region_name, '1.5-1'),
        model_data=f's3://{bucket}/{prefix}/model-b/model.tar.gz',
        role=role,
        name='model-variant-b'
    )

    # Create endpoint config with variants
    sm_client = boto3.client('sagemaker')

    endpoint_config_name = 'xgboost-ab-test-config'

    sm_client.create_endpoint_config(
        EndpointConfigName=endpoint_config_name,
        ProductionVariants=[
            {
                'VariantName': 'VariantA',
                'ModelName': model_a.name,
                'InstanceType': 'ml.m5.large',
                'InitialInstanceCount': 1,
                'InitialVariantWeight': 0.7  # 70% traffic
            },
            {
                'VariantName': 'VariantB',
                'ModelName': model_b.name,
                'InstanceType': 'ml.m5.large',
                'InitialInstanceCount': 1,
                'InitialVariantWeight': 0.3  # 30% traffic
            }
        ]
    )

    # Create endpoint
    sm_client.create_endpoint(
        EndpointName='xgboost-ab-test-endpoint',
        EndpointConfigName=endpoint_config_name
    )


# ============================================================================
# PART 6: Inference
# ============================================================================

def run_inference(predictor, test_data):
    """
    Run inference on deployed endpoint.
    """

    # Real-time inference
    predictions = predictor.predict(test_data)
    print(f"Predictions: {predictions}")

    return predictions


def run_async_inference(endpoint_name, s3_input_path):
    """
    Run async inference.

    EXAM TIP: Async inference uses S3 for input/output.
    """

    runtime_client = boto3.client('sagemaker-runtime')

    response = runtime_client.invoke_endpoint_async(
        EndpointName=endpoint_name,
        InputLocation=s3_input_path,
        ContentType='text/csv'
    )

    output_location = response['OutputLocation']
    print(f"Output will be at: {output_location}")

    return output_location


# ============================================================================
# PART 7: Cleanup
# ============================================================================

def cleanup(predictor=None, endpoint_name=None):
    """
    Clean up resources to avoid charges.

    EXAM TIP: Always clean up:
    - Endpoints (charged per hour)
    - Endpoint configs
    - Models
    """

    sm_client = boto3.client('sagemaker')

    if predictor:
        predictor.delete_endpoint()
        predictor.delete_model()

    if endpoint_name:
        # Delete endpoint
        sm_client.delete_endpoint(EndpointName=endpoint_name)

        # Get and delete endpoint config
        endpoint = sm_client.describe_endpoint(EndpointName=endpoint_name)
        config_name = endpoint['EndpointConfigName']
        sm_client.delete_endpoint_config(EndpointConfigName=config_name)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    # Note: This requires proper AWS credentials and data in S3
    print("This script demonstrates SageMaker concepts.")
    print("Review the code to understand the patterns.")
    print("\nKey exam concepts covered:")
    print("1. Estimator configuration")
    print("2. Spot instances with checkpointing")
    print("3. Hyperparameter tuning")
    print("4. Deployment options (real-time, serverless, async, batch)")
    print("5. Multi-variant endpoints")
    print("6. Inference patterns")
