# 07 - SageMaker Model Monitor

> **Exam Weight**: Part of Monitoring & Security domain (24%)
> **Priority**: HIGH - Critical for production ML

## What is Model Monitor?

SageMaker Model Monitor continuously monitors ML models in production to detect deviations in data quality, model quality, bias, and feature attribution. It's essential for maintaining model performance over time.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      MODEL MONITOR ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐              │
│  │  Real-time  │────▶│  Endpoint   │────▶│  S3 Data    │              │
│  │  Requests   │     │             │     │  Capture    │              │
│  └─────────────┘     └─────────────┘     └─────────────┘              │
│                                                  │                      │
│                                                  ▼                      │
│                                          ┌─────────────┐               │
│                                          │   Monitor   │               │
│                                          │   Schedule  │               │
│                                          └─────────────┘               │
│                                                  │                      │
│                    ┌─────────────────────────────┼─────────────────┐   │
│                    ▼                             ▼                 ▼   │
│            ┌─────────────┐             ┌─────────────┐     ┌─────────┐│
│            │Data Quality │             │Model Quality│     │  Bias   ││
│            │  Monitor    │             │  Monitor    │     │ Monitor ││
│            └─────────────┘             └─────────────┘     └─────────┘│
│                    │                             │                 │   │
│                    └─────────────────────────────┼─────────────────┘   │
│                                                  ▼                      │
│                                          ┌─────────────┐               │
│                                          │ CloudWatch  │               │
│                                          │   Alerts    │               │
│                                          └─────────────┘               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Four Types of Monitoring (MEMORIZE)

| Monitor Type | What It Detects | Baseline Required | Use Case |
|--------------|-----------------|-------------------|----------|
| **Data Quality** | Data drift (input changes) | Yes (from training data) | Schema, missing values, distribution |
| **Model Quality** | Model drift (performance degradation) | Yes (from model metrics) | Accuracy, F1, AUC decline |
| **Bias Drift** | Fairness changes | Yes (from Clarify analysis) | Protected attribute bias |
| **Feature Attribution** | Explainability changes | Yes (from Clarify) | Feature importance drift |

---

## Data Capture

First step: Capture inference requests and responses.

```python
from sagemaker.model_monitor import DataCaptureConfig

data_capture_config = DataCaptureConfig(
    enable_capture=True,
    sampling_percentage=100,  # Capture 100% of requests
    destination_s3_uri=f"s3://{bucket}/data-capture/",
    capture_options=["Input", "Output"],  # Capture both
    csv_content_types=["text/csv"],
    json_content_types=["application/json"]
)

# Apply to endpoint
predictor = model.deploy(
    initial_instance_count=1,
    instance_type="ml.m5.large",
    data_capture_config=data_capture_config
)
```

### Captured Data Structure

```
s3://bucket/data-capture/
└── endpoint-name/
    └── variant-name/
        └── 2024/01/15/10/
            ├── 30-abc123.jsonl
            └── 45-def456.jsonl
```

---

## Data Quality Monitor

Detects changes in input data distribution.

### Create Baseline

```python
from sagemaker.model_monitor import DefaultModelMonitor
from sagemaker.model_monitor.dataset_format import DatasetFormat

# Create monitor
data_quality_monitor = DefaultModelMonitor(
    role=role,
    instance_count=1,
    instance_type="ml.m5.xlarge",
    volume_size_in_gb=20,
    max_runtime_in_seconds=3600
)

# Generate baseline from training data
data_quality_monitor.suggest_baseline(
    baseline_dataset="s3://bucket/training-data/",
    dataset_format=DatasetFormat.csv(header=True),
    output_s3_uri="s3://bucket/baseline/data-quality/",
    wait=True
)
```

### Schedule Monitoring

```python
from sagemaker.model_monitor import CronExpressionGenerator

# Create monitoring schedule
data_quality_monitor.create_monitoring_schedule(
    monitor_schedule_name="data-quality-schedule",
    endpoint_input=endpoint_name,
    output_s3_uri="s3://bucket/monitoring/data-quality/",
    statistics="s3://bucket/baseline/data-quality/statistics.json",
    constraints="s3://bucket/baseline/data-quality/constraints.json",
    schedule_cron_expression=CronExpressionGenerator.hourly(),
    enable_cloudwatch_metrics=True
)
```

### Data Quality Constraints

```json
{
  "version": 0.0,
  "features": [
    {
      "name": "age",
      "inferred_type": "Integral",
      "completeness": 1.0,
      "num_constraints": {
        "is_non_negative": true,
        "min_value": 18,
        "max_value": 100
      }
    },
    {
      "name": "income",
      "inferred_type": "Fractional",
      "completeness": 0.98,
      "num_constraints": {
        "is_non_negative": true
      }
    }
  ]
}
```

---

## Model Quality Monitor

Detects degradation in model performance metrics.

```python
from sagemaker.model_monitor import ModelQualityMonitor

model_quality_monitor = ModelQualityMonitor(
    role=role,
    instance_count=1,
    instance_type="ml.m5.xlarge"
)

# Create baseline from ground truth
model_quality_monitor.suggest_baseline(
    baseline_dataset="s3://bucket/ground-truth/",
    dataset_format=DatasetFormat.csv(header=True),
    output_s3_uri="s3://bucket/baseline/model-quality/",
    problem_type="BinaryClassification",  # or Regression, MulticlassClassification
    inference_attribute="prediction",
    ground_truth_attribute="label",
    probability_attribute="probability"
)

# Schedule monitoring
model_quality_monitor.create_monitoring_schedule(
    monitor_schedule_name="model-quality-schedule",
    endpoint_input=endpoint_name,
    output_s3_uri="s3://bucket/monitoring/model-quality/",
    problem_type="BinaryClassification",
    ground_truth_input="s3://bucket/ground-truth/",
    constraints="s3://bucket/baseline/model-quality/constraints.json",
    schedule_cron_expression=CronExpressionGenerator.daily()
)
```

### Ground Truth Requirements

```
For model quality monitoring, you need GROUND TRUTH LABELS:

Timeline:
──────────────────────────────────────────────────────────
Prediction        Ground Truth        Monitor
   Made    ────▶    Arrives    ────▶  Compares
  (T=0)             (T=+7d)           (T=+7d)

Options for ground truth:
1. Manual labeling pipeline
2. Automated collection (e.g., did customer churn?)
3. Human feedback loops
```

---

## Bias Drift Monitor

Uses SageMaker Clarify to detect fairness changes.

```python
from sagemaker.clarify import (
    BiasConfig,
    DataConfig,
    ModelConfig
)
from sagemaker.model_monitor import ModelBiasMonitor

bias_config = BiasConfig(
    label_values_or_threshold=[1],
    facet_name="gender",
    facet_values_or_threshold=["Male"],
    group_name="age_group"
)

model_bias_monitor = ModelBiasMonitor(
    role=role,
    instance_count=1,
    instance_type="ml.m5.xlarge"
)

model_bias_monitor.suggest_baseline(
    data_config=DataConfig(
        s3_data_input_path="s3://bucket/training-data/",
        s3_output_path="s3://bucket/baseline/bias/",
        label="target",
        features="features"
    ),
    bias_config=bias_config,
    model_config=ModelConfig(
        model_name=model_name,
        instance_type="ml.m5.xlarge"
    )
)
```

---

## Feature Attribution Drift

Monitors changes in feature importance (explainability).

```python
from sagemaker.model_monitor import ModelExplainabilityMonitor
from sagemaker.clarify import SHAPConfig

shap_config = SHAPConfig(
    baseline=[baseline_data],  # Reference data for SHAP
    num_samples=100,
    agg_method="mean_abs"
)

explainability_monitor = ModelExplainabilityMonitor(
    role=role,
    instance_count=1,
    instance_type="ml.m5.xlarge"
)

explainability_monitor.suggest_baseline(
    data_config=data_config,
    model_config=model_config,
    explainability_config=shap_config
)
```

---

## CloudWatch Integration

### Metrics Emitted

| Metric | Description | Monitor Type |
|--------|-------------|--------------|
| **violations** | Number of constraint violations | Data Quality |
| **missing_value_ratio** | Ratio of missing values | Data Quality |
| **baseline_drift** | Drift from baseline | All types |
| **accuracy** | Model accuracy | Model Quality |
| **precision** | Model precision | Model Quality |
| **recall** | Model recall | Model Quality |
| **f1_score** | F1 score | Model Quality |

### CloudWatch Alarm Example

```python
import boto3

cloudwatch = boto3.client('cloudwatch')

cloudwatch.put_metric_alarm(
    AlarmName='ModelQualityDegradation',
    MetricName='accuracy',
    Namespace='aws/sagemaker/Endpoints/data-metrics',
    Statistic='Average',
    Period=3600,
    EvaluationPeriods=1,
    Threshold=0.8,
    ComparisonOperator='LessThanThreshold',
    AlarmActions=['arn:aws:sns:us-east-1:123456789:alerts'],
    Dimensions=[
        {'Name': 'EndpointName', 'Value': 'my-endpoint'},
        {'Name': 'MonitoringSchedule', 'Value': 'model-quality-schedule'}
    ]
)
```

---

## Constraint Violations

### Violation Report Structure

```json
{
  "violations": [
    {
      "feature_name": "age",
      "constraint_check_type": "data_type_check",
      "description": "Data type mismatch: expected Integral, got Fractional"
    },
    {
      "feature_name": "income",
      "constraint_check_type": "baseline_drift_check",
      "description": "Baseline drift detected: 0.25 (threshold: 0.1)"
    }
  ]
}
```

---

## Best Practices

1. **Start with Data Quality**: Most common issues are data-related
2. **Capture 100% Initially**: Reduce later if volume is too high
3. **Set Appropriate Thresholds**: Too sensitive = alert fatigue
4. **Automate Responses**: Trigger retraining on significant drift
5. **Monitor Costs**: Frequent monitoring jobs add up

---

## Exam Question Patterns

### Pattern 1: Data Drift
> "Input data distribution has changed significantly since training..."

**Answer**: Data Quality Monitor to detect and alert on data drift

### Pattern 2: Model Performance
> "Model accuracy has degraded in production..."

**Answer**: Model Quality Monitor with ground truth comparison

### Pattern 3: Fairness
> "Ensure model remains fair across demographic groups..."

**Answer**: Bias Drift Monitor using Clarify

### Pattern 4: Explainability
> "Monitor if feature importance changes over time..."

**Answer**: Feature Attribution Drift Monitor

### Pattern 5: Alerting
> "Get notified when violations exceed threshold..."

**Answer**: Enable CloudWatch metrics + CloudWatch Alarms

### Pattern 6: Continuous Monitoring
> "Monitor model every hour in production..."

**Answer**: Create monitoring schedule with hourly cron

---

## Monitor Comparison

| Scenario | Monitor Type |
|----------|--------------|
| "Input schema changed" | Data Quality |
| "More missing values than training" | Data Quality |
| "Accuracy dropped from 0.9 to 0.7" | Model Quality |
| "Model unfair to certain groups" | Bias Drift |
| "Feature importance shifted" | Feature Attribution |

---

## Checklist

- [ ] Understand all four monitor types and their purposes
- [ ] Know how to set up data capture
- [ ] Understand baseline creation process
- [ ] Know how to create monitoring schedules
- [ ] Understand constraint violations and reports
- [ ] Know CloudWatch integration for alerting

---

## Next Steps

After completing this module, proceed to:
- [08 - Custom Container ECR](../08-custom-container-ecr/) - Build custom training/inference containers
