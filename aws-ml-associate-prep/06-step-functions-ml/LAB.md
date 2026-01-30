# Lab 06: AWS Step Functions for ML Workflows

## Overview
In this lab, you'll create a Step Functions state machine that orchestrates an ML workflow with multiple AWS services.

**Duration**: 45-60 minutes
**Cost**: ~$1-2
**Prerequisites**: Understanding of SageMaker basics

---

## Lab Objectives

- [ ] Create a Step Functions state machine for ML
- [ ] Integrate SageMaker training with Step Functions
- [ ] Implement error handling and retries
- [ ] Use Choice states for conditional logic

---

## Part 1: Create State Machine

### Step 1.1: Create IAM Role

```bash
# Create trust policy
cat > stepfunctions-trust.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Principal": {"Service": "states.amazonaws.com"},
        "Action": "sts:AssumeRole"
    }]
}
EOF

aws iam create-role \
    --role-name StepFunctionsMLRole \
    --assume-role-policy-document file://stepfunctions-trust.json

# Attach policies
aws iam attach-role-policy --role-name StepFunctionsMLRole \
    --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess
aws iam attach-role-policy --role-name StepFunctionsMLRole \
    --policy-arn arn:aws:iam::aws:policy/AWSLambda_FullAccess
aws iam attach-role-policy --role-name StepFunctionsMLRole \
    --policy-arn arn:aws:iam::aws:policy/AmazonSNSFullAccess

export SF_ROLE_ARN=$(aws iam get-role --role-name StepFunctionsMLRole --query 'Role.Arn' --output text)
echo "Role ARN: $SF_ROLE_ARN"
```

### Step 1.2: Create State Machine Definition

Create `ml-workflow.json`:

```json
{
  "Comment": "ML Training Workflow",
  "StartAt": "ValidateInput",
  "States": {
    "ValidateInput": {
      "Type": "Pass",
      "Parameters": {
        "training_job_name.$": "States.Format('ml-job-{}', $$.Execution.Name)",
        "input_data.$": "$.input_data",
        "output_path.$": "$.output_path",
        "instance_type.$": "$.instance_type"
      },
      "Next": "StartTraining"
    },
    "StartTraining": {
      "Type": "Task",
      "Resource": "arn:aws:states:::sagemaker:createTrainingJob.sync",
      "Parameters": {
        "TrainingJobName.$": "$.training_job_name",
        "AlgorithmSpecification": {
          "TrainingImage": "YOUR_XGBOOST_IMAGE",
          "TrainingInputMode": "File"
        },
        "RoleArn": "YOUR_SAGEMAKER_ROLE",
        "InputDataConfig": [
          {
            "ChannelName": "train",
            "DataSource": {
              "S3DataSource": {
                "S3DataType": "S3Prefix",
                "S3Uri.$": "$.input_data"
              }
            },
            "ContentType": "text/csv"
          }
        ],
        "OutputDataConfig": {
          "S3OutputPath.$": "$.output_path"
        },
        "ResourceConfig": {
          "InstanceType.$": "$.instance_type",
          "InstanceCount": 1,
          "VolumeSizeInGB": 10
        },
        "StoppingCondition": {
          "MaxRuntimeInSeconds": 3600
        },
        "HyperParameters": {
          "objective": "binary:logistic",
          "num_round": "100"
        }
      },
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
          "ResultPath": "$.error",
          "Next": "NotifyFailure"
        }
      ],
      "Next": "CheckTrainingStatus"
    },
    "CheckTrainingStatus": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.TrainingJobStatus",
          "StringEquals": "Completed",
          "Next": "NotifySuccess"
        }
      ],
      "Default": "NotifyFailure"
    },
    "NotifySuccess": {
      "Type": "Pass",
      "Parameters": {
        "status": "SUCCESS",
        "message": "Training completed successfully",
        "model_artifacts.$": "$.ModelArtifacts.S3ModelArtifacts"
      },
      "End": true
    },
    "NotifyFailure": {
      "Type": "Pass",
      "Parameters": {
        "status": "FAILED",
        "message": "Training failed",
        "error.$": "$.error"
      },
      "End": true
    }
  }
}
```

### Step 1.3: Update and Create State Machine

```bash
# Get your account ID and region
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=$(aws configure get region)

# Get XGBoost image URI
XGBOOST_IMAGE="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/sagemaker-xgboost:1.5-1"
# Or use the public image
XGBOOST_IMAGE="683313688378.dkr.ecr.${REGION}.amazonaws.com/sagemaker-xgboost:1.5-1"

# Get SageMaker role
SAGEMAKER_ROLE=$(aws iam get-role --role-name SageMakerLabRole --query 'Role.Arn' --output text 2>/dev/null || echo "YOUR_SAGEMAKER_ROLE_ARN")

# Update the JSON file with actual values
sed -i "s|YOUR_XGBOOST_IMAGE|$XGBOOST_IMAGE|g" ml-workflow.json
sed -i "s|YOUR_SAGEMAKER_ROLE|$SAGEMAKER_ROLE|g" ml-workflow.json

# Create state machine
aws stepfunctions create-state-machine \
    --name MLTrainingWorkflow \
    --definition file://ml-workflow.json \
    --role-arn $SF_ROLE_ARN

STATE_MACHINE_ARN=$(aws stepfunctions list-state-machines --query "stateMachines[?name=='MLTrainingWorkflow'].stateMachineArn" --output text)
echo "State Machine ARN: $STATE_MACHINE_ARN"
```

---

## Part 2: Execute State Machine

### Step 2.1: Prepare Input

```bash
# Create execution input
cat > execution-input.json << 'EOF'
{
    "input_data": "s3://YOUR_BUCKET/train/",
    "output_path": "s3://YOUR_BUCKET/models/",
    "instance_type": "ml.m5.large"
}
EOF
```

### Step 2.2: Start Execution

```bash
# Start execution
EXECUTION_ARN=$(aws stepfunctions start-execution \
    --state-machine-arn $STATE_MACHINE_ARN \
    --input file://execution-input.json \
    --query 'executionArn' \
    --output text)

echo "Execution started: $EXECUTION_ARN"

# Monitor execution
while true; do
    STATUS=$(aws stepfunctions describe-execution \
        --execution-arn $EXECUTION_ARN \
        --query 'status' --output text)
    echo "Status: $STATUS"

    if [ "$STATUS" != "RUNNING" ]; then
        break
    fi
    sleep 30
done

# Get execution history
aws stepfunctions get-execution-history \
    --execution-arn $EXECUTION_ARN \
    --query 'events[*].{Type:type,State:stateEnteredEventDetails.name}'
```

---

## Part 3: Clean Up

```bash
# Delete state machine
aws stepfunctions delete-state-machine --state-machine-arn $STATE_MACHINE_ARN

# Delete IAM role
aws iam detach-role-policy --role-name StepFunctionsMLRole \
    --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess
aws iam detach-role-policy --role-name StepFunctionsMLRole \
    --policy-arn arn:aws:iam::aws:policy/AWSLambda_FullAccess
aws iam detach-role-policy --role-name StepFunctionsMLRole \
    --policy-arn arn:aws:iam::aws:policy/AmazonSNSFullAccess
aws iam delete-role --role-name StepFunctionsMLRole

rm -f ml-workflow.json execution-input.json stepfunctions-trust.json
```

---

## Lab Summary

| Concept | What You Did |
|---------|--------------|
| **State Machine** | Created workflow with multiple states |
| **SageMaker Integration** | Used .sync for synchronous training |
| **Error Handling** | Implemented Retry and Catch |
| **Choice State** | Added conditional logic |

---

## Exam Relevance

- ✅ Step Functions state types
- ✅ .sync vs async integrations
- ✅ Error handling patterns
- ✅ When to use Step Functions vs SageMaker Pipelines

---

## Next Lab

Continue to [Lab 07: Model Monitor](../07-model-monitor/LAB.md) →
