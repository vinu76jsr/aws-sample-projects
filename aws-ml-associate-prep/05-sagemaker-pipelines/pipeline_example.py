"""
SageMaker Pipelines Complete Example

This script demonstrates creating an end-to-end ML pipeline with:
- Data processing
- Model training
- Evaluation
- Conditional deployment
- Model registration

EXAM TIPS:
- Know all step types and their purposes
- Understand how to reference outputs between steps
- Know condition steps for quality gates
- Understand Model Registry and approval workflow
"""

import sagemaker
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.steps import ProcessingStep, TrainingStep, CacheConfig
from sagemaker.workflow.step_collections import RegisterModel
from sagemaker.workflow.conditions import ConditionGreaterThanOrEqualTo
from sagemaker.workflow.condition_step import ConditionStep
from sagemaker.workflow.functions import JsonGet
from sagemaker.workflow.properties import PropertyFile
from sagemaker.workflow.parameters import (
    ParameterInteger,
    ParameterString,
    ParameterFloat
)
from sagemaker.workflow.fail_step import FailStep
from sagemaker.processing import ScriptProcessor, ProcessingInput, ProcessingOutput
from sagemaker.estimator import Estimator
from sagemaker.inputs import TrainingInput
import boto3


# Initialize SageMaker session
session = sagemaker.Session()
role = sagemaker.get_execution_role()
bucket = session.default_bucket()
region = session.boto_region_name


# ============================================================================
# PIPELINE PARAMETERS
# ============================================================================

def define_parameters():
    """
    Define pipeline parameters for flexibility.

    EXAM TIP: Use parameters for values that change between runs
    """

    processing_instance_type = ParameterString(
        name="ProcessingInstanceType",
        default_value="ml.m5.xlarge"
    )

    processing_instance_count = ParameterInteger(
        name="ProcessingInstanceCount",
        default_value=1
    )

    training_instance_type = ParameterString(
        name="TrainingInstanceType",
        default_value="ml.m5.xlarge"
    )

    training_instance_count = ParameterInteger(
        name="TrainingInstanceCount",
        default_value=1
    )

    model_approval_status = ParameterString(
        name="ModelApprovalStatus",
        default_value="PendingManualApproval"
    )

    accuracy_threshold = ParameterFloat(
        name="AccuracyThreshold",
        default_value=0.8
    )

    input_data_uri = ParameterString(
        name="InputDataUri",
        default_value=f"s3://{bucket}/data/raw/"
    )

    return {
        "processing_instance_type": processing_instance_type,
        "processing_instance_count": processing_instance_count,
        "training_instance_type": training_instance_type,
        "training_instance_count": training_instance_count,
        "model_approval_status": model_approval_status,
        "accuracy_threshold": accuracy_threshold,
        "input_data_uri": input_data_uri
    }


# ============================================================================
# PROCESSING STEP
# ============================================================================

def create_processing_step(params, sklearn_image):
    """
    Create data processing step.

    EXAM TIP: ProcessingStep for data preprocessing, feature engineering
    """

    processor = ScriptProcessor(
        role=role,
        image_uri=sklearn_image,
        instance_type=params["processing_instance_type"],
        instance_count=params["processing_instance_count"],
        command=["python3"]
    )

    processing_step = ProcessingStep(
        name="DataProcessing",
        processor=processor,
        inputs=[
            ProcessingInput(
                source=params["input_data_uri"],
                destination="/opt/ml/processing/input"
            )
        ],
        outputs=[
            ProcessingOutput(
                output_name="train",
                source="/opt/ml/processing/output/train",
                destination=f"s3://{bucket}/pipeline/processed/train/"
            ),
            ProcessingOutput(
                output_name="validation",
                source="/opt/ml/processing/output/validation",
                destination=f"s3://{bucket}/pipeline/processed/validation/"
            ),
            ProcessingOutput(
                output_name="test",
                source="/opt/ml/processing/output/test",
                destination=f"s3://{bucket}/pipeline/processed/test/"
            )
        ],
        code="scripts/preprocessing.py",
        cache_config=CacheConfig(
            enable_caching=True,
            expire_after="P7D"  # Cache for 7 days
        )
    )

    return processing_step


# ============================================================================
# TRAINING STEP
# ============================================================================

def create_training_step(params, processing_step, xgboost_image):
    """
    Create model training step.

    EXAM TIP: TrainingStep references ProcessingStep outputs via .properties
    """

    estimator = Estimator(
        image_uri=xgboost_image,
        role=role,
        instance_count=params["training_instance_count"],
        instance_type=params["training_instance_type"],
        output_path=f"s3://{bucket}/pipeline/models/",
        hyperparameters={
            "objective": "binary:logistic",
            "num_round": 100,
            "max_depth": 5,
            "eta": 0.2,
            "eval_metric": "auc"
        },
        enable_sagemaker_metrics=True
    )

    training_step = TrainingStep(
        name="ModelTraining",
        estimator=estimator,
        inputs={
            # EXAM TIP: Reference output from processing step
            "train": TrainingInput(
                s3_data=processing_step.properties.ProcessingOutputConfig
                    .Outputs["train"].S3Output.S3Uri,
                content_type="text/csv"
            ),
            "validation": TrainingInput(
                s3_data=processing_step.properties.ProcessingOutputConfig
                    .Outputs["validation"].S3Output.S3Uri,
                content_type="text/csv"
            )
        },
        cache_config=CacheConfig(
            enable_caching=True,
            expire_after="P7D"
        )
    )

    return training_step


# ============================================================================
# EVALUATION STEP
# ============================================================================

def create_evaluation_step(params, processing_step, training_step, sklearn_image):
    """
    Create model evaluation step.

    EXAM TIP: PropertyFile allows reading metrics for ConditionStep
    """

    # Property file to store evaluation metrics
    evaluation_report = PropertyFile(
        name="EvaluationReport",
        output_name="evaluation",
        path="evaluation.json"
    )

    processor = ScriptProcessor(
        role=role,
        image_uri=sklearn_image,
        instance_type="ml.m5.large",
        instance_count=1,
        command=["python3"]
    )

    evaluation_step = ProcessingStep(
        name="ModelEvaluation",
        processor=processor,
        inputs=[
            # Model artifacts from training
            ProcessingInput(
                source=training_step.properties.ModelArtifacts.S3ModelArtifacts,
                destination="/opt/ml/processing/model"
            ),
            # Test data from processing
            ProcessingInput(
                source=processing_step.properties.ProcessingOutputConfig
                    .Outputs["test"].S3Output.S3Uri,
                destination="/opt/ml/processing/test"
            )
        ],
        outputs=[
            ProcessingOutput(
                output_name="evaluation",
                source="/opt/ml/processing/evaluation",
                destination=f"s3://{bucket}/pipeline/evaluation/"
            )
        ],
        code="scripts/evaluate.py",
        property_files=[evaluation_report]  # EXAM TIP: Enable metric extraction
    )

    return evaluation_step, evaluation_report


# ============================================================================
# CONDITION STEP
# ============================================================================

def create_condition_step(params, evaluation_step, evaluation_report,
                          register_step, fail_step):
    """
    Create conditional branching based on model quality.

    EXAM TIP: ConditionStep implements quality gates
    - JsonGet extracts values from PropertyFile
    - Supports GreaterThan, LessThan, Equals, etc.
    """

    # Define condition: accuracy >= threshold
    accuracy_condition = ConditionGreaterThanOrEqualTo(
        # EXAM TIP: JsonGet reads from PropertyFile
        left=JsonGet(
            step_name=evaluation_step.name,
            property_file=evaluation_report,
            json_path="metrics.accuracy"
        ),
        right=params["accuracy_threshold"]
    )

    condition_step = ConditionStep(
        name="CheckModelQuality",
        conditions=[accuracy_condition],
        if_steps=[register_step],  # If accuracy >= threshold
        else_steps=[fail_step]      # If accuracy < threshold
    )

    return condition_step


# ============================================================================
# MODEL REGISTRATION
# ============================================================================

def create_register_step(params, training_step, xgboost_image):
    """
    Create model registration step.

    EXAM TIP: Model Registry tracks model versions and approval status
    """

    register_step = RegisterModel(
        name="RegisterModel",
        estimator=None,  # Not using estimator
        model_data=training_step.properties.ModelArtifacts.S3ModelArtifacts,
        content_types=["text/csv", "application/json"],
        response_types=["application/json"],
        inference_instances=["ml.m5.large", "ml.m5.xlarge", "ml.c5.xlarge"],
        transform_instances=["ml.m5.xlarge"],
        model_package_group_name="MLPipelineModelGroup",
        approval_status=params["model_approval_status"],  # EXAM TIP: Controls deployment gate
        image_uri=xgboost_image,
        description="Model trained by ML Pipeline"
    )

    return register_step


# ============================================================================
# FAIL STEP
# ============================================================================

def create_fail_step():
    """
    Create failure step for when conditions aren't met.

    EXAM TIP: FailStep stops pipeline and marks as failed
    """

    fail_step = FailStep(
        name="ModelQualityFailed",
        error_message="Model did not meet quality threshold. Pipeline failed."
    )

    return fail_step


# ============================================================================
# BUILD PIPELINE
# ============================================================================

def build_pipeline():
    """
    Assemble the complete pipeline.
    """

    # Get container images
    sklearn_image = sagemaker.image_uris.retrieve(
        framework="sklearn",
        region=region,
        version="1.0-1",
        py_version="py3"
    )

    xgboost_image = sagemaker.image_uris.retrieve(
        framework="xgboost",
        region=region,
        version="1.5-1"
    )

    # Define parameters
    params = define_parameters()

    # Create steps
    processing_step = create_processing_step(params, sklearn_image)
    training_step = create_training_step(params, processing_step, xgboost_image)
    evaluation_step, evaluation_report = create_evaluation_step(
        params, processing_step, training_step, sklearn_image
    )
    fail_step = create_fail_step()
    register_step = create_register_step(params, training_step, xgboost_image)
    condition_step = create_condition_step(
        params, evaluation_step, evaluation_report, register_step, fail_step
    )

    # Build pipeline
    pipeline = Pipeline(
        name="MLTrainingPipeline",
        parameters=[
            params["processing_instance_type"],
            params["processing_instance_count"],
            params["training_instance_type"],
            params["training_instance_count"],
            params["model_approval_status"],
            params["accuracy_threshold"],
            params["input_data_uri"]
        ],
        steps=[
            processing_step,
            training_step,
            evaluation_step,
            condition_step  # Contains register_step or fail_step
        ],
        sagemaker_session=session
    )

    return pipeline


# ============================================================================
# PIPELINE OPERATIONS
# ============================================================================

def create_or_update_pipeline(pipeline):
    """
    Create or update pipeline definition.

    EXAM TIP: upsert() creates if doesn't exist, updates if exists
    """

    pipeline.upsert(role_arn=role)
    print(f"Pipeline '{pipeline.name}' created/updated successfully")

    return pipeline


def start_pipeline(pipeline, parameters=None):
    """
    Start pipeline execution.
    """

    execution = pipeline.start(parameters=parameters or {})

    print(f"Pipeline execution started: {execution.arn}")
    print(f"Execution status: {execution.describe()['PipelineExecutionStatus']}")

    return execution


def monitor_execution(execution):
    """
    Monitor pipeline execution.
    """

    # Wait for completion
    execution.wait()

    # Get final status
    status = execution.describe()
    print(f"Final status: {status['PipelineExecutionStatus']}")

    # List steps
    steps = execution.list_steps()
    for step in steps['PipelineExecutionSteps']:
        print(f"  Step: {step['StepName']}, Status: {step['StepStatus']}")

    return status


def list_executions(pipeline_name):
    """
    List all executions of a pipeline.
    """

    sm_client = boto3.client('sagemaker')

    response = sm_client.list_pipeline_executions(
        PipelineName=pipeline_name,
        SortBy='CreationTime',
        SortOrder='Descending',
        MaxResults=10
    )

    for exec in response['PipelineExecutionSummaries']:
        print(f"Execution: {exec['PipelineExecutionArn']}")
        print(f"  Status: {exec['PipelineExecutionStatus']}")
        print(f"  Created: {exec['CreationTime']}")
        print()

    return response


# ============================================================================
# MODEL REGISTRY OPERATIONS
# ============================================================================

def list_model_packages(model_package_group_name):
    """
    List models in Model Registry.
    """

    sm_client = boto3.client('sagemaker')

    response = sm_client.list_model_packages(
        ModelPackageGroupName=model_package_group_name,
        SortBy='CreationTime',
        SortOrder='Descending'
    )

    for pkg in response['ModelPackageSummaryList']:
        print(f"Model: {pkg['ModelPackageArn']}")
        print(f"  Status: {pkg['ModelApprovalStatus']}")
        print(f"  Created: {pkg['CreationTime']}")
        print()

    return response


def approve_model(model_package_arn):
    """
    Approve a model for deployment.

    EXAM TIP: Change status from PendingManualApproval to Approved
    """

    sm_client = boto3.client('sagemaker')

    sm_client.update_model_package(
        ModelPackageArn=model_package_arn,
        ModelApprovalStatus='Approved'
    )

    print(f"Model approved: {model_package_arn}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("SageMaker Pipelines Example")
    print("=" * 50)
    print("\nKey concepts demonstrated:")
    print("1. Pipeline parameters for flexibility")
    print("2. Processing step for data preparation")
    print("3. Training step with step references")
    print("4. Evaluation step with PropertyFile")
    print("5. Condition step for quality gates")
    print("6. Model registration with approval workflow")
    print("7. Caching for cost optimization")

    # Example usage:
    # pipeline = build_pipeline()
    # create_or_update_pipeline(pipeline)
    # execution = start_pipeline(pipeline, {"AccuracyThreshold": 0.85})
    # monitor_execution(execution)
