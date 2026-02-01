# 06 - AWS Step Functions[^step-functions] for ML Workflows

> **Exam Weight**: Part of Deployment & Orchestration domain (22%)
> **Priority**: MEDIUM-HIGH - Alternative to SageMaker Pipelines

## What is AWS Step Functions?

AWS Step Functions is a serverless orchestration service that lets you coordinate multiple AWS services into workflows using visual state machines[^state-machine]. For ML, it's used to orchestrate complex workflows involving multiple AWS services.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     STEP FUNCTIONS ML WORKFLOW                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐  │
│  │  Glue   │──▶│SageMaker│──▶│  Wait   │──▶│ Lambda  │──▶│ Deploy  │  │
│  │  ETL    │   │Training │   │  for    │   │  Eval   │   │  Model  │  │
│  └─────────┘   └─────────┘   │Complete │   └─────────┘   └─────────┘  │
│                              └─────────┘                               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Step Functions vs SageMaker Pipelines

| Feature | Step Functions | SageMaker Pipelines |
|---------|---------------|---------------------|
| **Scope** | Any AWS service | SageMaker-centric |
| **ML Integration** | Via service integrations | Native, purpose-built |
| **Visual Builder** | Workflow Studio | Studio Pipeline designer |
| **Pricing** | Per state transition | Per pipeline step |
| **Use Case** | Multi-service workflows | Pure ML pipelines |
| **Model Registry** | Manual integration | Built-in |

### Exam Tip: When to Choose
- **Step Functions**: Complex workflows with multiple AWS services
- **SageMaker Pipelines**: Pure ML training/deployment pipelines

---

## State Types (KNOW FOR EXAM)

| State Type | Purpose | ML Use Case |
|------------|---------|-------------|
| **Task**[^task-state] | Execute work | Invoke Lambda, SageMaker, Glue |
| **Choice**[^choice-state] | Branching logic | Route based on model metrics |
| **Wait**[^wait-state] | Pause execution | Wait for async job completion |
| **Parallel** | Concurrent execution | Train multiple models |
| **Map** | Iterate over items | Process multiple datasets |
| **Pass** | Transform data | Modify state input/output |
| **Succeed** | End successfully | Mark workflow complete |
| **Fail** | End with error | Handle failures |

---

## SageMaker Service Integrations

### Synchronous (Wait for Completion)

```json
{
  "Type": "Task",
  "Resource": "arn:aws:states:::sagemaker:createTrainingJob.sync",
  "Parameters": {
    "TrainingJobName.$": "$.training_job_name",
    "AlgorithmSpecification": {
      "TrainingImage": "123456789.dkr.ecr.us-east-1.amazonaws.com/xgboost:1",
      "TrainingInputMode": "File"
    },
    "RoleArn": "arn:aws:iam::123456789:role/SageMakerRole",
    "InputDataConfig": [...],
    "OutputDataConfig": {...}
  }
}
```

### Asynchronous (Fire and Forget)

```json
{
  "Type": "Task",
  "Resource": "arn:aws:states:::sagemaker:createTrainingJob",
  "Parameters": {...}
}
```

### Exam Tip: .sync Integration[^sync-integration]
- `.sync` = Wait for completion (synchronous)
- No suffix = Start and continue (asynchronous)
- `.waitForTaskToken` = Wait for callback

---

## Common ML Workflow Pattern

```json
{
  "Comment": "ML Training Pipeline",
  "StartAt": "DataPreprocessing",
  "States": {
    "DataPreprocessing": {
      "Type": "Task",
      "Resource": "arn:aws:states:::glue:startJobRun.sync",
      "Parameters": {
        "JobName": "preprocessing-job"
      },
      "Next": "TrainModel"
    },
    "TrainModel": {
      "Type": "Task",
      "Resource": "arn:aws:states:::sagemaker:createTrainingJob.sync",
      "Parameters": {
        "TrainingJobName.$": "States.Format('training-{}', $$.Execution.Name)",
        "AlgorithmSpecification": {...},
        "InputDataConfig": [...],
        "OutputDataConfig": {...},
        "ResourceConfig": {
          "InstanceType": "ml.m5.xlarge",
          "InstanceCount": 1,
          "VolumeSizeInGB": 30
        },
        "StoppingCondition": {
          "MaxRuntimeInSeconds": 3600
        }
      },
      "Next": "EvaluateModel"
    },
    "EvaluateModel": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456789:function:evaluate-model",
      "Next": "CheckAccuracy"
    },
    "CheckAccuracy": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.accuracy",
          "NumericGreaterThanEquals": 0.8,
          "Next": "DeployModel"
        }
      ],
      "Default": "FailWorkflow"
    },
    "DeployModel": {
      "Type": "Task",
      "Resource": "arn:aws:states:::sagemaker:createEndpoint",
      "Parameters": {...},
      "End": true
    },
    "FailWorkflow": {
      "Type": "Fail",
      "Error": "ModelQualityError",
      "Cause": "Model accuracy below threshold"
    }
  }
}
```

---

## Parallel Model Training

```json
{
  "TrainModels": {
    "Type": "Parallel",
    "Branches": [
      {
        "StartAt": "TrainXGBoost",
        "States": {
          "TrainXGBoost": {
            "Type": "Task",
            "Resource": "arn:aws:states:::sagemaker:createTrainingJob.sync",
            "Parameters": {...},
            "End": true
          }
        }
      },
      {
        "StartAt": "TrainLinearLearner",
        "States": {
          "TrainLinearLearner": {
            "Type": "Task",
            "Resource": "arn:aws:states:::sagemaker:createTrainingJob.sync",
            "Parameters": {...},
            "End": true
          }
        }
      }
    ],
    "Next": "SelectBestModel"
  }
}
```

---

## Map State for Batch Processing

```json
{
  "ProcessDatasets": {
    "Type": "Map",
    "ItemsPath": "$.datasets",
    "MaxConcurrency": 5,
    "Iterator": {
      "StartAt": "ProcessDataset",
      "States": {
        "ProcessDataset": {
          "Type": "Task",
          "Resource": "arn:aws:states:::sagemaker:createProcessingJob.sync",
          "Parameters": {
            "ProcessingJobName.$": "States.Format('process-{}', $.dataset_name)"
          },
          "End": true
        }
      }
    },
    "Next": "CombineResults"
  }
}
```

---

## Error Handling[^retry-catch]

```json
{
  "TrainModel": {
    "Type": "Task",
    "Resource": "arn:aws:states:::sagemaker:createTrainingJob.sync",
    "Parameters": {...},
    "Retry": [
      {
        "ErrorEquals": ["SageMaker.ResourceLimitExceededException"],
        "IntervalSeconds": 60,
        "MaxAttempts": 3,
        "BackoffRate": 2.0
      }
    ],
    "Catch": [
      {
        "ErrorEquals": ["States.ALL"],
        "Next": "HandleError"
      }
    ],
    "Next": "EvaluateModel"
  }
}
```

### Exam Tip: Error Handling
- **Retry**: Automatic retry with backoff
- **Catch**: Route to error handling state
- Use both for robust workflows

---

## Input/Output Processing

### InputPath, OutputPath, ResultPath

```json
{
  "TrainModel": {
    "Type": "Task",
    "Resource": "...",
    "InputPath": "$.training_config",      // Filter input
    "ResultPath": "$.training_result",     // Where to put result
    "OutputPath": "$.training_result",     // Filter output
    "Next": "NextState"
  }
}
```

### Parameters with Intrinsic Functions

```json
{
  "Parameters": {
    "TrainingJobName.$": "States.Format('job-{}-{}', $.model_type, $$.Execution.Name)",
    "Timestamp.$": "$$.State.EnteredTime",
    "ExecutionId.$": "$$.Execution.Id"
  }
}
```

### Exam Tip: $ vs $$
- `$` - References input data
- `$$` - References context object (execution info)

---

## Triggering Step Functions

### EventBridge Rule (Scheduled)

```json
{
  "ScheduleExpression": "rate(1 day)",
  "Targets": [{
    "Arn": "arn:aws:states:us-east-1:123456789:stateMachine:MLPipeline",
    "RoleArn": "arn:aws:iam::123456789:role/EventBridgeRole",
    "Input": "{\"source\": \"scheduled\"}"
  }]
}
```

### S3 Event Trigger

```json
{
  "source": ["aws.s3"],
  "detail-type": ["Object Created"],
  "detail": {
    "bucket": {"name": ["training-data"]}
  }
}
```

---

## Express vs Standard Workflows

| Feature | Standard | Express |
|---------|----------|---------|
| **Duration** | Up to 1 year | Up to 5 minutes |
| **Execution** | Exactly-once | At-least-once |
| **Pricing** | Per state transition | Per execution + duration |
| **Use Case** | Long-running ML jobs | Quick data processing |

### Exam Tip
- **Standard**: ML training workflows (long-running)
- **Express**: Real-time data processing, inference preprocessing

---

## Exam Question Patterns

### Pattern 1: Multi-Service Orchestration
> "Coordinate Glue ETL, SageMaker training, and SNS notification..."

**Answer**: Step Functions (orchestrates multiple services)

### Pattern 2: Parallel Training
> "Train multiple models simultaneously and compare..."

**Answer**: Step Functions Parallel state

### Pattern 3: Conditional Deployment
> "Deploy only if model accuracy exceeds threshold..."

**Answer**: Choice state with accuracy condition

### Pattern 4: Error Recovery
> "Retry training on resource limits, notify on other errors..."

**Answer**: Retry + Catch blocks in state definition

### Pattern 5: Wait for Completion
> "Ensure training completes before evaluation..."

**Answer**: Use `.sync` suffix on SageMaker integration

---

## Checklist

- [ ] Understand state types (Task, Choice, Parallel, Map, Wait)
- [ ] Know synchronous vs asynchronous integrations (.sync)
- [ ] Understand error handling (Retry, Catch)
- [ ] Know input/output processing (InputPath, ResultPath, OutputPath)
- [ ] Understand Standard vs Express workflows
- [ ] Know when to use Step Functions vs SageMaker Pipelines

---

## Glossary

[^step-functions]: **Step Functions** - An AWS serverless orchestration service that coordinates multiple AWS services into visual workflows. It uses Amazon States Language (ASL) to define state machines for complex, multi-step processes.

[^state-machine]: **State Machine** - A workflow definition in Step Functions that consists of a series of states (steps) and transitions. State machines define the order of execution, branching logic, and error handling for workflows.

[^task-state]: **Task State** - A state type in Step Functions that performs a unit of work, such as invoking a Lambda function, starting a SageMaker training job, or calling another AWS service.

[^choice-state]: **Choice State** - A state type that adds branching logic to a workflow. It evaluates conditions on the input and transitions to different states based on the results, similar to an if-else statement.

[^wait-state]: **Wait State** - A state type that pauses the workflow execution for a specified duration or until a specific timestamp. Useful for waiting between steps or implementing delays.

[^sync-integration]: **.sync Integration** - A Step Functions integration pattern that waits for an asynchronous AWS service operation to complete before proceeding. Adding `.sync` to the resource ARN makes the task synchronous.

[^retry-catch]: **Retry/Catch** - Error handling mechanisms in Step Functions. Retry automatically retries failed states with configurable backoff. Catch routes errors to specified states for handling, enabling graceful failure recovery.

---

## Next Steps

After completing this module, proceed to:
- [07 - Model Monitor](../07-model-monitor/) - Model observability and drift detection
