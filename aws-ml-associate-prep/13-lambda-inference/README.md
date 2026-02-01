# 13 - AWS Lambda for ML Inference

> **Exam Weight**: Part of Deployment domain
> **Priority**: MEDIUM - Serverless inference option

## What is Lambda for ML?

AWS Lambda[^lambda] can run ML inference[^inference] for lightweight models, providing a serverless[^serverless], pay-per-request option. Ideal for intermittent traffic and cost-sensitive applications.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    LAMBDA ML INFERENCE PATTERNS                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  PATTERN 1: Direct Inference            PATTERN 2: API Gateway          │
│  ──────────────────────────            ─────────────────────            │
│  ┌─────────┐   ┌─────────┐            ┌──────┐  ┌──────┐  ┌──────┐    │
│  │   S3    │──▶│ Lambda  │            │ API  │─▶│Lambda│─▶│Model │    │
│  │ Event   │   │ + Model │            │  GW  │  │      │  │(S3)  │    │
│  └─────────┘   └─────────┘            └──────┘  └──────┘  └──────┘    │
│                                                                         │
│  PATTERN 3: SageMaker Endpoint          PATTERN 4: Container Image     │
│  ──────────────────────────            ───────────────────────          │
│  ┌─────────┐   ┌─────────────┐        ┌─────────┐   ┌─────────────┐   │
│  │ Lambda  │──▶│  SageMaker  │        │ Lambda  │   │  Container  │   │
│  │         │   │  Endpoint   │        │         │◀──│   Image     │   │
│  └─────────┘   └─────────────┘        └─────────┘   │  (ECR)      │   │
│                                                      └─────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Lambda Limits (EXAM CRITICAL)

| Limit | Value | Impact on ML |
|-------|-------|--------------|
| **Memory**[^memory-size] | 128 MB - 10 GB | Model size limit |
| **Timeout**[^timeout] | 15 minutes max | Inference time limit |
| **Package Size** | 50 MB (zip), 250 MB (unzipped) | Model + dependencies |
| **Container Image** | 10 GB | Large models possible |
| **/tmp Storage** | 512 MB - 10 GB | Model loading space |
| **Concurrency** | 1000 default | Scaling limit |

### Exam Tip: Model Size
- Small models (<250 MB): Regular Lambda deployment
- Medium models (<10 GB): Container image deployment
- Large models: Use SageMaker endpoints instead

---

## Pattern 1: Direct Model Loading

```python
import json
import pickle
import boto3

# Global for reuse across invocations (warm start)
model = None
s3 = boto3.client('s3')


def load_model():
    global model
    if model is None:
        # Download model from S3 to /tmp
        s3.download_file('bucket', 'model.pkl', '/tmp/model.pkl')
        with open('/tmp/model.pkl', 'rb') as f:
            model = pickle.load(f)
    return model


def lambda_handler(event, context):
    # Load model (cached after first call)
    model = load_model()

    # Parse input
    body = json.loads(event.get('body', '{}'))
    features = body.get('features', [])

    # Make prediction
    prediction = model.predict([features])

    return {
        'statusCode': 200,
        'body': json.dumps({
            'prediction': prediction.tolist()
        })
    }
```

---

## Pattern 2: Lambda + SageMaker Endpoint

```python
import json
import boto3

runtime = boto3.client('sagemaker-runtime')

def lambda_handler(event, context):
    # Parse input
    body = json.loads(event.get('body', '{}'))

    # Invoke SageMaker endpoint
    response = runtime.invoke_endpoint(
        EndpointName='my-model-endpoint',
        ContentType='application/json',
        Body=json.dumps(body)
    )

    result = json.loads(response['Body'].read())

    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }
```

### Exam Tip: When to Use
- **Lambda only**: Small models, infrequent traffic
- **Lambda + SageMaker**: Large models, need SageMaker features

---

## Pattern 3: Container Image

For larger models (up to 10 GB).

### Dockerfile

```dockerfile
FROM public.ecr.aws/lambda/python:3.9

# Install dependencies
RUN pip install scikit-learn numpy pandas

# Copy model and handler
COPY model.pkl ${LAMBDA_TASK_ROOT}
COPY app.py ${LAMBDA_TASK_ROOT}

CMD ["app.lambda_handler"]
```

### Handler

```python
import json
import pickle

# Load model at container start
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)


def lambda_handler(event, context):
    body = json.loads(event.get('body', '{}'))
    features = body.get('features', [])

    prediction = model.predict([features])

    return {
        'statusCode': 200,
        'body': json.dumps({'prediction': prediction.tolist()})
    }
```

---

## Lambda Layers for ML

Lambda Layer[^lambda-layer] allows sharing common ML dependencies.

```bash
# Create layer with scikit-learn
mkdir python
pip install scikit-learn -t python/
zip -r sklearn-layer.zip python

# Upload to Lambda
aws lambda publish-layer-version \
    --layer-name sklearn-layer \
    --zip-file fileb://sklearn-layer.zip \
    --compatible-runtimes python3.9
```

```python
# Use layer in function
import sklearn  # Comes from layer
```

---

## Provisioned Concurrency

Eliminate cold starts[^cold-start] for consistent latency.

```python
import boto3

lambda_client = boto3.client('lambda')

# Set provisioned concurrency
response = lambda_client.put_provisioned_concurrency_config(
    FunctionName='ml-inference',
    Qualifier='prod',  # Alias or version
    ProvisionedConcurrentExecutions=10
)
```

### Exam Tip: Cold Starts
- **Problem**: First invocation loads model (slow)
- **Solution**: Provisioned Concurrency keeps instances warm
- **Cost**: Pay for provisioned capacity

---

## Event-Driven ML

Trigger inference from AWS events.

### S3 Trigger (Batch Processing)

```python
def lambda_handler(event, context):
    # Get uploaded file info
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    # Download and process file
    s3.download_file(bucket, key, '/tmp/input.csv')

    # Run batch predictions
    df = pd.read_csv('/tmp/input.csv')
    predictions = model.predict(df)

    # Save results
    output_key = key.replace('input/', 'output/')
    df['prediction'] = predictions
    df.to_csv('/tmp/output.csv', index=False)
    s3.upload_file('/tmp/output.csv', bucket, output_key)

    return {'statusCode': 200}
```

---

## Lambda vs SageMaker Endpoints

| Feature | Lambda | SageMaker Real-time | SageMaker Serverless |
|---------|--------|---------------------|---------------------|
| **Cold Start** | Yes (unless provisioned) | No | Yes |
| **Max Memory** | 10 GB | Unlimited | 6 GB |
| **Timeout** | 15 min | None | None |
| **Model Size** | <10 GB | Any | <4 GB |
| **GPU** | No | Yes | No |
| **Pricing** | Per invocation | Per hour | Per invocation |
| **Use Case** | Light inference | Heavy inference | Intermittent |

### Exam Tip: Choose Wisely
- **Lambda**: Small models, event-driven, <15 min
- **SageMaker Real-time**: Large models, consistent traffic, GPU
- **SageMaker Serverless**: Medium models, intermittent traffic

---

## Exam Question Patterns

### Pattern 1: Cost Optimization
> "Intermittent traffic, want to minimize costs..."

**Answer**: Lambda or SageMaker Serverless

### Pattern 2: Model Size
> "Model is 500 MB, need serverless..."

**Answer**: Lambda Container Image (up to 10 GB)

### Pattern 3: Event Processing
> "Run inference when new file uploaded to S3..."

**Answer**: Lambda with S3 trigger

### Pattern 4: Latency
> "Need consistent low latency, no cold starts..."

**Answer**: Lambda with Provisioned Concurrency or SageMaker Real-time

### Pattern 5: GPU Required
> "Deep learning model requires GPU..."

**Answer**: SageMaker endpoint (Lambda doesn't support GPU)

---

## Best Practices

1. **Cache Model**: Load in global scope for reuse
2. **Use Layers**: Share dependencies across functions
3. **Container Images**: For models >250 MB
4. **Provisioned Concurrency**: For latency-sensitive apps
5. **Right-size Memory**: More memory = more CPU
6. **Monitor Cold Starts**: CloudWatch Insights

---

## Checklist

- [ ] Know Lambda limits (memory, timeout, package size)
- [ ] Understand when to use Lambda vs SageMaker
- [ ] Know container image deployment for large models
- [ ] Understand provisioned concurrency for cold starts
- [ ] Know event-driven inference patterns

---

## Glossary

[^lambda]: **Lambda** - AWS's serverless compute service that runs code in response to events without provisioning or managing servers. Automatically scales and charges only for compute time consumed.

[^cold-start]: **Cold Start** - The latency incurred when a Lambda function is invoked after being idle, requiring AWS to provision a new execution environment, load the runtime, and initialize the function code.

[^lambda-layer]: **Lambda Layer** - A ZIP archive containing libraries, custom runtimes, or other dependencies that can be shared across multiple Lambda functions, reducing deployment package size.

[^api-gateway]: **API Gateway** - AWS service for creating, publishing, and managing RESTful and WebSocket APIs that can trigger Lambda functions for serverless API backends.

[^serverless]: **Serverless** - A cloud computing model where the cloud provider manages infrastructure automatically, allowing developers to focus on code while paying only for actual usage.

[^inference]: **Inference** - The process of using a trained machine learning model to make predictions on new, unseen data.

[^memory-size]: **Memory Size** - Lambda configuration (128 MB to 10 GB) that determines allocated memory and proportionally affects CPU power available to the function.

[^timeout]: **Timeout** - Maximum execution time allowed for a Lambda function (up to 15 minutes), after which the function is terminated.

---

## Next Steps

After completing this module, proceed to:
- [14 - EMR Spark ML](../14-emr-spark-ml/) - Big data ML processing
