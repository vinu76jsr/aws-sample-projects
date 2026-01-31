# Lab 07: SageMaker Model Monitor

## Overview
Set up Model Monitor to detect data drift in a deployed model endpoint.

**Duration**: 60-90 minutes
**Cost**: ~$5-10
**Prerequisites**: Deployed SageMaker endpoint

---

## Architecture Overview

```mermaid
flowchart TB
    subgraph Inference["fa:fa-broadcast-tower Real-time Inference"]
        Client[fa:fa-user Client App]
        Endpoint[fa:fa-server SageMaker Endpoint]
        Capture[fa:fa-camera Data Capture]
    end

    subgraph Storage["fa:fa-database Data Storage"]
        S3Cap[(fa:fa-database S3: Captured Data)]
        S3Base[(fa:fa-ruler S3: Baseline)]
        S3Report[(fa:fa-file-alt S3: Reports)]
    end

    subgraph Monitor["fa:fa-eye Model Monitor"]
        Schedule[fa:fa-calendar Monitoring Schedule<br/>Hourly/Daily]
        Job[fa:fa-cogs Processing Job<br/>Compare to Baseline]
        Analyze[fa:fa-search Analyze Violations]
    end

    subgraph Alerts["fa:fa-bell Alerting"]
        CW[fa:fa-chart-line CloudWatch Metrics]
        Alarm[fa:fa-exclamation-triangle CloudWatch Alarm]
        SNS[fa:fa-envelope SNS Notification]
    end

    Client --> Endpoint
    Endpoint --> Capture
    Capture --> S3Cap

    S3Cap --> Job
    S3Base --> Job
    Schedule --> Job
    Job --> S3Report
    Job --> Analyze
    Analyze --> CW
    CW --> Alarm
    Alarm --> SNS

    style Inference fill:#e3f2fd
    style Storage fill:#fff3e0
    style Monitor fill:#e8f5e9
    style Alerts fill:#fce4ec
```

### Monitor Types

```mermaid
flowchart LR
    subgraph DataQuality["fa:fa-table Data Quality Monitor"]
        DQ1[fa:fa-chart-bar Feature Statistics]
        DQ2[fa:fa-question-circle Missing Values]
        DQ3[fa:fa-exchange-alt Data Type Changes]
    end

    subgraph ModelQuality["fa:fa-bullseye Model Quality Monitor"]
        MQ1[fa:fa-percentage Accuracy Metrics]
        MQ2[fa:fa-balance-scale Precision/Recall]
        MQ3[fa:fa-check-double Ground Truth Required]
    end

    subgraph BiasDrift["fa:fa-balance-scale-right Bias Drift Monitor"]
        BD1[fa:fa-users Demographic Parity]
        BD2[fa:fa-equals Equalized Odds]
        BD3[fa:fa-gavel Fairness Metrics]
    end

    subgraph FeatureAttribution["fa:fa-lightbulb Feature Attribution"]
        FA1[fa:fa-project-diagram SHAP Values]
        FA2[fa:fa-sort-amount-down Feature Importance]
        FA3[fa:fa-random Explainability Drift]
    end

    style DataQuality fill:#e3f2fd
    style ModelQuality fill:#e8f5e9
    style BiasDrift fill:#fff3e0
    style FeatureAttribution fill:#fce4ec
```

### Drift Detection Flow

```mermaid
sequenceDiagram
    participant Train as fa:fa-database Training Data
    participant Base as fa:fa-ruler Baseline Job
    participant Prod as fa:fa-broadcast-tower Production Traffic
    participant Mon as fa:fa-eye Monitor Job
    participant CW as CloudWatch

    Train->>Base: Create baseline statistics
    Base->>Base: Calculate mean, std, min, max
    Note over Base: Store baseline in S3

    loop Every hour
        Prod->>Mon: Captured inference data
        Mon->>Mon: Calculate current statistics
        Mon->>Mon: Compare to baseline
        alt Drift detected
            Mon->>CW: Publish violation metrics
            CW->>CW: Trigger alarm
        else No drift
            Mon->>CW: Publish normal metrics
        end
    end
```

---

## Lab Objectives

- [ ] Enable data capture on an endpoint
- [ ] Create a baseline from training data
- [ ] Set up a monitoring schedule
- [ ] Analyze monitoring results

---

## Part 1: Deploy Model with Data Capture

```python
# Cell 1: Setup
import sagemaker
from sagemaker.model_monitor import DataCaptureConfig, DefaultModelMonitor
from sagemaker.model_monitor.dataset_format import DatasetFormat
import pandas as pd
import numpy as np

session = sagemaker.Session()
role = sagemaker.get_execution_role()
bucket = session.default_bucket()

# Assuming you have a trained model from Lab 01
# If not, train a quick XGBoost model first
```

```python
# Cell 2: Configure data capture
data_capture_config = DataCaptureConfig(
    enable_capture=True,
    sampling_percentage=100,  # Capture all requests
    destination_s3_uri=f"s3://{bucket}/model-monitor/data-capture",
    capture_options=["Input", "Output"],
    csv_content_types=["text/csv"],
    json_content_types=["application/json"]
)

# Deploy model with data capture
predictor = model.deploy(
    initial_instance_count=1,
    instance_type="ml.t2.medium",
    data_capture_config=data_capture_config,
    endpoint_name="monitor-lab-endpoint"
)

print(f"Endpoint deployed: {predictor.endpoint_name}")
```

---

## Part 2: Generate Baseline

```python
# Cell 3: Create baseline from training data
monitor = DefaultModelMonitor(
    role=role,
    instance_count=1,
    instance_type="ml.m5.xlarge",
    volume_size_in_gb=20,
    max_runtime_in_seconds=3600
)

# Suggest baseline from training data
monitor.suggest_baseline(
    baseline_dataset=f"s3://{bucket}/train/train.csv",
    dataset_format=DatasetFormat.csv(header=True),
    output_s3_uri=f"s3://{bucket}/model-monitor/baseline",
    wait=True
)

print("Baseline created!")

# View baseline statistics
!aws s3 cp s3://{bucket}/model-monitor/baseline/statistics.json ./
!cat statistics.json | python -m json.tool | head -50
```

---

## Part 3: Create Monitoring Schedule

```python
# Cell 4: Create monitoring schedule
from sagemaker.model_monitor import CronExpressionGenerator

monitor.create_monitoring_schedule(
    monitor_schedule_name="monitor-lab-schedule",
    endpoint_input=predictor.endpoint_name,
    output_s3_uri=f"s3://{bucket}/model-monitor/reports",
    statistics=f"s3://{bucket}/model-monitor/baseline/statistics.json",
    constraints=f"s3://{bucket}/model-monitor/baseline/constraints.json",
    schedule_cron_expression=CronExpressionGenerator.hourly(),
    enable_cloudwatch_metrics=True
)

print("Monitoring schedule created!")
```

---

## Part 4: Generate Traffic and Observe

```python
# Cell 5: Generate predictions to create captured data
import time

# Normal predictions
for i in range(50):
    sample = np.random.randn(1, 20)
    predictor.predict(sample)

print("Normal predictions sent")

# Drifted predictions (different distribution)
for i in range(50):
    sample = np.random.randn(1, 20) * 5 + 10  # Shifted distribution
    predictor.predict(sample)

print("Drifted predictions sent")
print("Wait for monitoring job to run (hourly schedule)")
```

---

## Part 5: Check Monitoring Results

```python
# Cell 6: List monitoring executions
executions = monitor.list_executions()

if executions:
    latest = executions[-1]
    print(f"Latest execution: {latest}")

    # Check for violations
    if latest.exit_message:
        print(f"Exit message: {latest.exit_message}")

    # Download violation report
    !aws s3 ls s3://{bucket}/model-monitor/reports/ --recursive
```

---

## Part 6: Clean Up

```python
# Delete monitoring schedule
monitor.delete_monitoring_schedule()

# Delete endpoint
predictor.delete_endpoint()

# Clean up S3
!aws s3 rm s3://{bucket}/model-monitor/ --recursive

print("Cleanup complete!")
```

---

## Lab Summary

| Concept | What You Did |
|---------|--------------|
| **Data Capture** | Enabled capture on endpoint |
| **Baseline** | Created from training data |
| **Schedule** | Set up hourly monitoring |
| **Drift Detection** | Generated drifted data |

---

## Exam Relevance

- ✅ Four types of monitoring (Data Quality, Model Quality, Bias, Feature Attribution)
- ✅ Data capture configuration
- ✅ Baseline creation
- ✅ CloudWatch integration

---

## Next Lab

Continue to [Lab 08: Custom Container ECR](../08-custom-container-ecr/LAB.md) →
