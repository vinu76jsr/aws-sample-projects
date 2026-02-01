# 16 - CloudWatch for ML Monitoring & Alerts

> **Exam Weight**: Part of Monitoring & Security domain (24%)
> **Priority**: MEDIUM - Operational ML monitoring

## What is CloudWatch for ML?

Amazon CloudWatch[^cloudwatch] provides monitoring and observability for ML workloads. It collects metrics[^metrics], logs, and events from SageMaker and other ML services.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    CLOUDWATCH ML MONITORING                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     DATA SOURCES                                │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────────┐   │   │
│  │  │SageMaker│  │ Lambda  │  │   EMR   │  │ Model Monitor   │   │   │
│  │  │Endpoints│  │Functions│  │ Clusters│  │ (Drift Alerts)  │   │   │
│  │  └────┬────┘  └────┬────┘  └────┬────┘  └────────┬────────┘   │   │
│  └───────┼────────────┼───────────┼────────────────┼─────────────┘   │
│          └────────────┴───────────┴────────────────┘                  │
│                                  │                                     │
│                                  ▼                                     │
│                          ┌─────────────┐                              │
│                          │ CloudWatch  │                              │
│                          │  Metrics    │                              │
│                          └─────────────┘                              │
│                                  │                                     │
│                    ┌─────────────┼─────────────┐                      │
│                    ▼             ▼             ▼                      │
│             ┌───────────┐ ┌───────────┐ ┌───────────┐                │
│             │  Alarms   │ │Dashboards │ │   Logs    │                │
│             │           │ │           │ │ Insights  │                │
│             └───────────┘ └───────────┘ └───────────┘                │
│                    │                                                   │
│                    ▼                                                   │
│             ┌───────────┐                                             │
│             │SNS/Lambda │                                             │
│             │  Actions  │                                             │
│             └───────────┘                                             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## SageMaker Metrics (KNOW FOR EXAM)

### Endpoint Metrics

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| `Invocations` | Number of requests | Low = traffic drop |
| `InvocationsPerInstance` | Requests per instance | High = scaling needed |
| `ModelLatency`[^model-latency] | Inference time (ms) | > SLA = issue |
| `OverheadLatency` | Non-inference overhead | High = infrastructure issue |
| `Invocation4XXErrors` | Client errors | > 0 = bad requests |
| `Invocation5XXErrors`[^invocation-errors] | Server errors | > 0 = model issue |
| `CPUUtilization` | CPU usage % | > 80% = scale up |
| `MemoryUtilization` | Memory usage % | > 80% = scale up |
| `GPUUtilization` | GPU usage % | Varies |
| `DiskUtilization` | Disk usage % | > 80% = increase |

### Training Job Metrics

| Metric | Description | Use |
|--------|-------------|-----|
| `train:loss` | Training loss | Convergence tracking |
| `validation:accuracy` | Validation accuracy | Model quality |
| `CPUUtilization` | CPU usage | Resource optimization |
| `GPUMemoryUtilization` | GPU memory | OOM prevention |

---

## Creating Alarms[^alarms]

### Endpoint Latency Alarm

```python
import boto3

cloudwatch = boto3.client('cloudwatch')

# Create latency alarm
cloudwatch.put_metric_alarm(
    AlarmName='ML-Endpoint-High-Latency',
    ComparisonOperator='GreaterThanThreshold',
    EvaluationPeriods=3,
    MetricName='ModelLatency',
    Namespace='AWS/SageMaker',
    Period=60,  # 1 minute
    Statistic='Average',
    Threshold=1000,  # 1 second
    AlarmDescription='Model latency exceeds 1 second',
    AlarmActions=[
        'arn:aws:sns:us-east-1:123456789:ml-alerts'
    ],
    Dimensions=[
        {'Name': 'EndpointName', 'Value': 'my-endpoint'},
        {'Name': 'VariantName', 'Value': 'AllTraffic'}
    ]
)
```

### Error Rate Alarm

```python
cloudwatch.put_metric_alarm(
    AlarmName='ML-Endpoint-Error-Rate',
    ComparisonOperator='GreaterThanThreshold',
    EvaluationPeriods=2,
    MetricName='Invocation5XXErrors',
    Namespace='AWS/SageMaker',
    Period=300,  # 5 minutes
    Statistic='Sum',
    Threshold=10,  # More than 10 errors
    AlarmDescription='Too many 5XX errors',
    AlarmActions=[
        'arn:aws:sns:us-east-1:123456789:ml-alerts'
    ],
    Dimensions=[
        {'Name': 'EndpointName', 'Value': 'my-endpoint'}
    ]
)
```

### CPU Utilization Alarm (Auto Scaling Trigger)

```python
cloudwatch.put_metric_alarm(
    AlarmName='ML-Endpoint-High-CPU',
    ComparisonOperator='GreaterThanThreshold',
    EvaluationPeriods=3,
    MetricName='CPUUtilization',
    Namespace='/aws/sagemaker/Endpoints',
    Period=60,
    Statistic='Average',
    Threshold=70,
    AlarmDescription='CPU above 70% - consider scaling',
    AlarmActions=[
        'arn:aws:application-autoscaling:action'  # Trigger scaling
    ],
    Dimensions=[
        {'Name': 'EndpointName', 'Value': 'my-endpoint'},
        {'Name': 'VariantName', 'Value': 'AllTraffic'}
    ]
)
```

---

## Model Monitor Integration

Model Monitor publishes metrics to CloudWatch.

```python
# Data quality violation alarm
cloudwatch.put_metric_alarm(
    AlarmName='Model-Data-Drift-Alert',
    ComparisonOperator='GreaterThanThreshold',
    EvaluationPeriods=1,
    MetricName='feature_baseline_drift_amount',
    Namespace='aws/sagemaker/Endpoints/data-metrics',
    Period=3600,  # 1 hour
    Statistic='Maximum',
    Threshold=0.2,  # 20% drift
    AlarmDescription='Feature drift exceeds threshold',
    AlarmActions=[
        'arn:aws:sns:us-east-1:123456789:ml-alerts'
    ],
    Dimensions=[
        {'Name': 'EndpointName', 'Value': 'my-endpoint'},
        {'Name': 'MonitoringScheduleName', 'Value': 'my-schedule'}
    ]
)
```

---

## CloudWatch Logs

### SageMaker Log Groups

| Log Group | Content |
|-----------|---------|
| `/aws/sagemaker/TrainingJobs` | Training job logs |
| `/aws/sagemaker/Endpoints/{endpoint}` | Inference logs |
| `/aws/sagemaker/ProcessingJobs` | Processing logs |
| `/aws/sagemaker/NotebookInstances` | Notebook logs |

### Log Insights Query

```sql
-- Find slow predictions
fields @timestamp, @message
| filter @message like /inference/
| parse @message "latency: * ms" as latency
| filter latency > 1000
| sort @timestamp desc
| limit 100

-- Find errors
fields @timestamp, @message
| filter @message like /ERROR/ or @message like /Exception/
| sort @timestamp desc
| limit 50

-- Count invocations per hour
fields @timestamp
| filter @message like /invocation/
| stats count() by bin(1h)
```

---

## CloudWatch Dashboards[^dashboard]

### Create ML Dashboard

```python
dashboard_body = {
    "widgets": [
        {
            "type": "metric",
            "properties": {
                "title": "Endpoint Latency",
                "metrics": [
                    ["AWS/SageMaker", "ModelLatency", "EndpointName", "my-endpoint"]
                ],
                "period": 60,
                "stat": "Average"
            }
        },
        {
            "type": "metric",
            "properties": {
                "title": "Invocations",
                "metrics": [
                    ["AWS/SageMaker", "Invocations", "EndpointName", "my-endpoint"]
                ],
                "period": 60,
                "stat": "Sum"
            }
        },
        {
            "type": "metric",
            "properties": {
                "title": "Errors",
                "metrics": [
                    ["AWS/SageMaker", "Invocation4XXErrors", "EndpointName", "my-endpoint"],
                    ["AWS/SageMaker", "Invocation5XXErrors", "EndpointName", "my-endpoint"]
                ],
                "period": 60,
                "stat": "Sum"
            }
        },
        {
            "type": "metric",
            "properties": {
                "title": "Resource Utilization",
                "metrics": [
                    ["/aws/sagemaker/Endpoints", "CPUUtilization", "EndpointName", "my-endpoint"],
                    ["/aws/sagemaker/Endpoints", "MemoryUtilization", "EndpointName", "my-endpoint"]
                ],
                "period": 60,
                "stat": "Average"
            }
        }
    ]
}

cloudwatch.put_dashboard(
    DashboardName='ML-Operations-Dashboard',
    DashboardBody=json.dumps(dashboard_body)
)
```

---

## EventBridge[^eventbridge] Integration

Respond to ML events automatically.

```python
import boto3

events = boto3.client('events')

# Rule for training job state changes
events.put_rule(
    Name='training-job-state-change',
    EventPattern=json.dumps({
        "source": ["aws.sagemaker"],
        "detail-type": ["SageMaker Training Job State Change"],
        "detail": {
            "TrainingJobStatus": ["Failed", "Completed"]
        }
    }),
    State='ENABLED'
)

# Add target (SNS[^sns] notification)
events.put_targets(
    Rule='training-job-state-change',
    Targets=[
        {
            'Id': 'sns-notification',
            'Arn': 'arn:aws:sns:us-east-1:123456789:ml-alerts',
            'InputTransformer': {
                'InputPathsMap': {
                    'jobName': '$.detail.TrainingJobName',
                    'status': '$.detail.TrainingJobStatus'
                },
                'InputTemplate': '"Training job <jobName> has <status>"'
            }
        }
    ]
)
```

### Common Event Patterns

| Event | Pattern | Use Case |
|-------|---------|----------|
| Training completed | `TrainingJobStatus: Completed` | Trigger deployment |
| Training failed | `TrainingJobStatus: Failed` | Alert team |
| Endpoint unhealthy | `EndpointStatus: Failed` | Page on-call |
| Model approved | `ModelPackageStatus: Approved` | Trigger deployment |

---

## Auto Scaling with CloudWatch

```python
import boto3

aas = boto3.client('application-autoscaling')

# Register scalable target
aas.register_scalable_target(
    ServiceNamespace='sagemaker',
    ResourceId='endpoint/my-endpoint/variant/AllTraffic',
    ScalableDimension='sagemaker:variant:DesiredInstanceCount',
    MinCapacity=1,
    MaxCapacity=10
)

# Create scaling policy
aas.put_scaling_policy(
    PolicyName='target-tracking-policy',
    ServiceNamespace='sagemaker',
    ResourceId='endpoint/my-endpoint/variant/AllTraffic',
    ScalableDimension='sagemaker:variant:DesiredInstanceCount',
    PolicyType='TargetTrackingScaling',
    TargetTrackingScalingPolicyConfiguration={
        'TargetValue': 70.0,  # Target 70% CPU
        'PredefinedMetricSpecification': {
            'PredefinedMetricType': 'SageMakerVariantInvocationsPerInstance'
        },
        'ScaleInCooldown': 300,
        'ScaleOutCooldown': 60
    }
)
```

---

## Exam Question Patterns

### Pattern 1: Latency Monitoring
> "Alert when inference latency exceeds SLA..."

**Answer**: CloudWatch Alarm on ModelLatency metric

### Pattern 2: Error Detection
> "Get notified on model errors..."

**Answer**: CloudWatch Alarm on Invocation5XXErrors

### Pattern 3: Drift Detection
> "Alert when data drift is detected..."

**Answer**: CloudWatch Alarm on Model Monitor metrics

### Pattern 4: Auto Scaling
> "Scale endpoint based on traffic..."

**Answer**: Application Auto Scaling with CloudWatch metrics

### Pattern 5: Automation
> "Trigger deployment when training completes..."

**Answer**: EventBridge rule on training job state change

### Pattern 6: Log Analysis
> "Find slow predictions in logs..."

**Answer**: CloudWatch Logs Insights queries

---

## Best Practices

1. **Set meaningful thresholds**: Based on SLAs and baselines
2. **Use composite alarms**: Combine multiple conditions
3. **Create dashboards**: Operational visibility
4. **Automate responses**: EventBridge + Lambda
5. **Retain logs appropriately**: Balance cost and compliance
6. **Use anomaly detection**: For dynamic thresholds

---

## Checklist

- [ ] Know key SageMaker metrics (latency, errors, utilization)
- [ ] Understand how to create CloudWatch alarms
- [ ] Know Model Monitor CloudWatch integration
- [ ] Understand CloudWatch Logs and Insights
- [ ] Know EventBridge for ML automation
- [ ] Understand auto scaling with CloudWatch metrics

---

## Glossary

[^cloudwatch]: **CloudWatch** - AWS monitoring and observability service that collects metrics, logs, and events from AWS resources and applications for operational visibility.

[^metrics]: **Metrics** - Time-ordered data points published to CloudWatch representing the behavior of resources (e.g., CPU utilization, request count, latency).

[^alarms]: **Alarms** - CloudWatch feature that watches metrics and triggers actions (like SNS notifications or auto scaling) when thresholds are breached.

[^dashboard]: **Dashboard** - CloudWatch customizable visualization that displays metrics and alarms in a single view for operational monitoring.

[^eventbridge]: **EventBridge** - AWS serverless event bus service that routes events from AWS services, SaaS applications, and custom sources to targets like Lambda or SNS.

[^sns]: **SNS (Simple Notification Service)** - AWS messaging service for sending notifications via email, SMS, or HTTP endpoints, commonly used as an alarm action target.

[^model-latency]: **Model Latency** - SageMaker metric measuring the time (in milliseconds) the model takes to respond to an inference request, excluding network overhead.

[^invocation-errors]: **Invocation Errors** - SageMaker metrics tracking 4XX (client) and 5XX (server) errors during endpoint invocations, indicating issues with requests or model.

---

## Congratulations!

You've completed all 16 projects in the AWS ML Associate exam preparation path. Review each module and practice with the sample code to solidify your understanding.

**Next Steps:**
1. Review all project summaries
2. Take practice exams
3. Focus on weak areas
4. Schedule your exam!
