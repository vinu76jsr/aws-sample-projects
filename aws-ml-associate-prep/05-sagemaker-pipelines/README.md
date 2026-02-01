# 05 - SageMaker Pipelines[^pipeline]

> **Exam Weight**: Part of Deployment & Orchestration domain (22%)
> **Priority**: HIGH - Core MLOps component

## What is SageMaker Pipelines?

SageMaker Pipelines is a purpose-built CI/CD service for ML that enables you to create, automate, and manage end-to-end ML workflows. It's the native orchestration solution for SageMaker.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      SAGEMAKER PIPELINE WORKFLOW                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐  │
│  │  Data   │──▶│Processing│──▶│Training │──▶│  Eval   │──▶│ Register│  │
│  │  Prep   │   │   Step  │   │  Step   │   │  Step   │   │  Model  │  │
│  └─────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘  │
│                                                   │                     │
│                                                   ▼                     │
│                                            ┌───────────┐               │
│                                            │ Condition │               │
│                                            │   Step    │               │
│                                            └───────────┘               │
│                                            │           │               │
│                                     Pass ──┘           └── Fail        │
│                                            │                │          │
│                                            ▼                ▼          │
│                                     ┌───────────┐   ┌───────────┐     │
│                                     │  Deploy   │   │   Fail    │     │
│                                     │   Step    │   │   Step    │     │
│                                     └───────────┘   └───────────┘     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Pipeline Steps[^pipeline-step] (KNOW FOR EXAM)

| Step Type | Purpose | Use Case |
|-----------|---------|----------|
| **ProcessingStep**[^processing-step] | Data preprocessing, evaluation | ETL, feature engineering, model evaluation |
| **TrainingStep**[^training-step] | Model training | Run SageMaker training job |
| **TuningStep** | Hyperparameter tuning | Run HPO job |
| **CreateModelStep** | Create SageMaker model | Package model for deployment |
| **RegisterModelStep** | Register in Model Registry[^model-registry] | Version and track models |
| **TransformStep** | Batch inference | Run batch transform |
| **ConditionStep**[^condition-step] | Conditional branching | If-else logic based on metrics |
| **FailStep** | Fail pipeline | Stop on error conditions |
| **CallbackStep** | External integration | Wait for external systems |
| **LambdaStep** | Run Lambda function | Custom logic |
| **QualityCheckStep** | Data/Model quality | Bias, drift detection |
| **ClarifyCheckStep** | Explainability | Model explanations |
| **EMRStep** | EMR processing | Big data processing |

---

## Pipeline Parameters

Define parameters at pipeline level for flexibility.

```python
from sagemaker.workflow.parameters import (
    ParameterInteger,
    ParameterString,
    ParameterFloat
)

# Define parameters
processing_instance_count = ParameterInteger(
    name="ProcessingInstanceCount",
    default_value=1
)

training_instance_type = ParameterString(
    name="TrainingInstanceType",
    default_value="ml.m5.xlarge"
)

model_approval_status = ParameterString(
    name="ModelApprovalStatus",
    default_value="PendingManualApproval"
)
```

### Exam Tip: Parameters
- Use parameters for values that change between runs
- Instance types, counts, S3 paths, thresholds
- Enables pipeline reuse across environments

---

## Processing Step

```python
from sagemaker.processing import ScriptProcessor
from sagemaker.workflow.steps import ProcessingStep

# Define processor
processor = ScriptProcessor(
    role=role,
    image_uri=image_uri,
    instance_type="ml.m5.xlarge",
    instance_count=1
)

# Create processing step
processing_step = ProcessingStep(
    name="DataProcessing",
    processor=processor,
    inputs=[
        ProcessingInput(
            source="s3://bucket/raw/",
            destination="/opt/ml/processing/input"
        )
    ],
    outputs=[
        ProcessingOutput(
            output_name="train",
            source="/opt/ml/processing/output/train",
            destination="s3://bucket/processed/train/"
        ),
        ProcessingOutput(
            output_name="test",
            source="/opt/ml/processing/output/test",
            destination="s3://bucket/processed/test/"
        )
    ],
    code="preprocessing.py"
)
```

---

## Training Step

```python
from sagemaker.estimator import Estimator
from sagemaker.workflow.steps import TrainingStep

# Define estimator
estimator = Estimator(
    image_uri=training_image,
    role=role,
    instance_count=1,
    instance_type=training_instance_type,  # Pipeline parameter
    output_path=f"s3://{bucket}/models/",
    hyperparameters={
        "epochs": 10,
        "learning_rate": 0.01
    }
)

# Create training step
training_step = TrainingStep(
    name="ModelTraining",
    estimator=estimator,
    inputs={
        # Reference output from processing step
        "train": TrainingInput(
            s3_data=processing_step.properties.ProcessingOutputConfig
                .Outputs["train"].S3Output.S3Uri
        )
    }
)
```

### Exam Tip: Step References
- Use `.properties` to reference outputs from previous steps
- Creates automatic dependencies between steps

---

## Evaluation Step

```python
from sagemaker.workflow.steps import ProcessingStep
from sagemaker.workflow.properties import PropertyFile

# Define property file for metrics
evaluation_report = PropertyFile(  # PropertyFile[^property-file]
    name="EvaluationReport",
    output_name="evaluation",
    path="evaluation.json"
)

# Evaluation step
evaluation_step = ProcessingStep(
    name="ModelEvaluation",
    processor=processor,
    inputs=[
        ProcessingInput(
            source=training_step.properties.ModelArtifacts.S3ModelArtifacts,
            destination="/opt/ml/processing/model"
        ),
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
            destination="s3://bucket/evaluation/"
        )
    ],
    code="evaluate.py",
    property_files=[evaluation_report]
)
```

---

## Condition Step (EXAM FAVORITE)

```python
from sagemaker.workflow.conditions import ConditionGreaterThanOrEqualTo
from sagemaker.workflow.condition_step import ConditionStep
from sagemaker.workflow.functions import JsonGet

# Define condition
condition = ConditionGreaterThanOrEqualTo(
    left=JsonGet(
        step_name=evaluation_step.name,
        property_file=evaluation_report,
        json_path="metrics.accuracy"  # Read from evaluation.json
    ),
    right=0.8  # Threshold
)

# Condition step
condition_step = ConditionStep(
    name="CheckModelQuality",
    conditions=[condition],
    if_steps=[register_step, deploy_step],  # If condition passes
    else_steps=[fail_step]                   # If condition fails
)
```

### Exam Tip: Condition Step
- Use JsonGet to extract values from PropertyFiles
- Multiple conditions can be combined (AND logic)
- Common use: Quality gates for model deployment

---

## Model Registry

```python
from sagemaker.workflow.steps import RegisterModelStep
from sagemaker.workflow.model_step import ModelStep

# Register model in Model Registry
register_step = RegisterModelStep(
    name="RegisterModel",
    estimator=estimator,
    model_data=training_step.properties.ModelArtifacts.S3ModelArtifacts,
    content_types=["application/json"],
    response_types=["application/json"],
    inference_instances=["ml.m5.large", "ml.m5.xlarge"],
    transform_instances=["ml.m5.xlarge"],
    model_package_group_name="MyModelPackageGroup",
    approval_status=model_approval_status  # Pipeline parameter
)
```

### Model Registry Concepts

```
┌─────────────────────────────────────────────────────────────┐
│                     MODEL REGISTRY                          │
├─────────────────────────────────────────────────────────────┤
│  Model Package Group: ChurnPredictionModels                 │
│  ├── Model Package v1 (Approved)                           │
│  │   ├── Model Artifacts: s3://bucket/model-v1/            │
│  │   ├── Metrics: accuracy=0.85, f1=0.82                   │
│  │   └── Status: Approved                                   │
│  ├── Model Package v2 (PendingApproval)                    │
│  │   ├── Model Artifacts: s3://bucket/model-v2/            │
│  │   ├── Metrics: accuracy=0.87, f1=0.84                   │
│  │   └── Status: PendingManualApproval                     │
│  └── Model Package v3 (Rejected)                           │
│      └── Status: Rejected                                   │
└─────────────────────────────────────────────────────────────┘
```

| Approval Status | Description |
|-----------------|-------------|
| **Approved** | Ready for deployment |
| **Rejected** | Not suitable for deployment |
| **PendingManualApproval** | Awaiting human review |

---

## Complete Pipeline Example

```python
from sagemaker.workflow.pipeline import Pipeline

# Create pipeline
pipeline = Pipeline(
    name="MLPipeline",
    parameters=[
        processing_instance_count,
        training_instance_type,
        model_approval_status
    ],
    steps=[
        processing_step,
        training_step,
        evaluation_step,
        condition_step  # Contains register_step or fail_step
    ],
    sagemaker_session=session
)

# Create/update pipeline definition
pipeline.upsert(role_arn=role)

# Start pipeline execution
execution = pipeline.start(
    parameters={
        "ProcessingInstanceCount": 2,
        "TrainingInstanceType": "ml.m5.2xlarge"
    }
)

# Monitor execution
execution.describe()
execution.list_steps()
```

---

## Pipeline Triggers

### 1. Manual Trigger

```python
execution = pipeline.start()
```

### 2. Scheduled Trigger (EventBridge)

```python
# EventBridge rule to trigger pipeline
{
    "source": ["aws.events"],
    "detail-type": ["Scheduled Event"],
    "schedule": "rate(1 day)"
}
```

### 3. Event-Driven (S3 Event)

```python
# S3 event → EventBridge → Pipeline
{
    "source": ["aws.s3"],
    "detail-type": ["Object Created"],
    "detail": {
        "bucket": {"name": ["training-data-bucket"]}
    }
}
```

### Exam Tip: Pipeline Triggers
- **"Daily retraining"** → EventBridge scheduled rule
- **"Trigger on new data"** → S3 event → EventBridge → Pipeline
- **"Manual approval workflow"** → Start with PendingManualApproval

---

## Caching[^cache-config]

Enable caching to skip unchanged steps.

```python
from sagemaker.workflow.steps import CacheConfig

cache_config = CacheConfig(
    enable_caching=True,
    expire_after="P30D"  # Cache for 30 days (ISO 8601 duration)
)

training_step = TrainingStep(
    name="ModelTraining",
    estimator=estimator,
    inputs={...},
    cache_config=cache_config  # Enable caching
)
```

### Exam Tip: Caching
- Skips steps if inputs haven't changed
- Reduces cost and execution time
- Expire cache with `expire_after`

---

## Pipeline vs Step Functions

| Feature | SageMaker Pipelines | Step Functions |
|---------|---------------------|----------------|
| **Purpose** | ML-specific orchestration | General workflow orchestration |
| **ML Integration** | Native SageMaker support | Requires custom integration |
| **Step Types** | ML-specific steps | State machine states |
| **Visualization** | SageMaker Studio | Step Functions console |
| **Model Registry** | Built-in integration | Manual integration |
| **Use Case** | Pure ML pipelines | Multi-service workflows |

### Exam Tip: When to Use What
- **"ML training pipeline"** → SageMaker Pipelines
- **"Complex workflow with multiple AWS services"** → Step Functions
- **"Combine ML with non-ML steps"** → Consider both, Step Functions for orchestration

---

## Exam Question Patterns

### Pattern 1: Automation
> "Automate model retraining when new data arrives..."

**Answer**: S3 Event → EventBridge → SageMaker Pipeline

### Pattern 2: Quality Gate
> "Only deploy model if accuracy > 90%..."

**Answer**: ConditionStep with accuracy threshold check

### Pattern 3: Model Versioning
> "Track and version all trained models..."

**Answer**: RegisterModelStep with Model Registry

### Pattern 4: Approval Workflow
> "Require human approval before production deployment..."

**Answer**: Set ModelApprovalStatus to "PendingManualApproval"

### Pattern 5: Cost Optimization
> "Reduce pipeline execution costs..."

**Answer**: Enable caching for unchanged steps

### Pattern 6: Step Dependencies
> "Run evaluation only after training completes..."

**Answer**: Use step.properties to create dependency

---

## Best Practices

1. **Parameterize Everything**: Use parameters for flexibility
2. **Enable Caching**: Skip unchanged steps
3. **Use Condition Steps**: Implement quality gates
4. **Register Models**: Always use Model Registry
5. **Log Everything**: Include evaluation metrics
6. **Version Control**: Store pipeline definition in Git

---

## Checklist

- [ ] Understand different step types and their purposes
- [ ] Know how to use pipeline parameters
- [ ] Understand condition steps for quality gates
- [ ] Know Model Registry concepts and approval workflow
- [ ] Understand caching for cost optimization
- [ ] Know how to trigger pipelines (manual, scheduled, event-driven)
- [ ] Understand when to use Pipelines vs Step Functions

---

## Glossary

[^pipeline]: **Pipeline** - A SageMaker Pipelines workflow that defines a series of interconnected steps for ML workflows. Pipelines enable automation, reproducibility, and CI/CD practices for machine learning.

[^pipeline-step]: **Pipeline Step** - An individual unit of work within a SageMaker Pipeline. Steps can include data processing, model training, evaluation, and deployment, with dependencies automatically managed.

[^condition-step]: **ConditionStep** - A pipeline step that enables conditional branching based on the output of previous steps. Used to implement quality gates that determine whether to proceed with deployment.

[^property-file]: **PropertyFile** - A mechanism in SageMaker Pipelines for extracting specific values (like metrics) from step outputs. PropertyFiles are used with ConditionSteps to make decisions based on model performance.

[^model-registry]: **Model Registry** - A SageMaker component for cataloging and versioning trained models. It tracks model packages, approval status, and metadata, enabling model governance and deployment workflows.

[^cache-config]: **CacheConfig** - A configuration that enables step caching in SageMaker Pipelines. When enabled, steps with unchanged inputs are skipped, reducing execution time and cost.

[^processing-step]: **ProcessingStep** - A pipeline step that runs data processing jobs using SageMaker Processing. Used for ETL, feature engineering, data validation, and model evaluation tasks.

[^training-step]: **TrainingStep** - A pipeline step that runs SageMaker training jobs. It takes processed data as input and produces model artifacts, which can be referenced by subsequent steps.

---

## Next Steps

After completing this module, proceed to:
- [06 - Step Functions ML](../06-step-functions-ml/) - General workflow orchestration
