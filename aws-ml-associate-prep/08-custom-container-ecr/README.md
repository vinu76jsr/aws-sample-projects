# 08 - Custom Containers with Amazon ECR

> **Exam Weight**: Part of ML Model Development domain (26%)
> **Priority**: MEDIUM - For custom algorithms and frameworks

## What is Amazon ECR?

Amazon Elastic Container Registry (ECR) is a fully managed Docker container registry. For ML, it's used to store custom training and inference containers when built-in algorithms don't meet your needs.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    CUSTOM CONTAINER WORKFLOW                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐              │
│  │ Dockerfile  │────▶│  Build &    │────▶│    Push     │              │
│  │  + Code     │     │    Tag      │     │   to ECR    │              │
│  └─────────────┘     └─────────────┘     └─────────────┘              │
│                                                  │                      │
│                                                  ▼                      │
│                                          ┌─────────────┐               │
│                                          │     ECR     │               │
│                                          │ Repository  │               │
│                                          └─────────────┘               │
│                                                  │                      │
│                              ┌───────────────────┴───────────────────┐ │
│                              ▼                                       ▼ │
│                      ┌─────────────┐                         ┌─────────┐│
│                      │  Training   │                         │Inference││
│                      │    Job      │                         │Endpoint ││
│                      └─────────────┘                         └─────────┘│
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## When to Use Custom Containers

| Scenario | Use Custom Container? | Alternative |
|----------|----------------------|-------------|
| Custom ML framework | Yes | - |
| Proprietary algorithm | Yes | - |
| Specific library versions | Yes | Requirements.txt |
| Built-in algorithm works | No | SageMaker built-in |
| Minor preprocessing | No | Script Mode |
| Custom inference logic | Yes | Inference script |

---

## Container Types

### 1. Training Container

```dockerfile
# Training container Dockerfile
FROM python:3.9-slim

# Install dependencies
RUN pip install scikit-learn pandas numpy boto3

# Copy training code
COPY train.py /opt/ml/code/train.py

# Set environment variables
ENV SAGEMAKER_PROGRAM train.py

# SageMaker expects training script at this path
ENTRYPOINT ["python", "/opt/ml/code/train.py"]
```

### 2. Inference Container

```dockerfile
# Inference container Dockerfile
FROM python:3.9-slim

# Install dependencies
RUN pip install flask gunicorn scikit-learn pandas numpy

# Copy inference code
COPY inference.py /opt/ml/code/inference.py
COPY serve /opt/ml/code/serve

# SageMaker invokes /serve script
ENTRYPOINT ["python", "/opt/ml/code/serve"]

# Health check endpoint
EXPOSE 8080
```

### 3. Combined Container (Training + Inference)

```dockerfile
# Combined container
FROM python:3.9-slim

RUN pip install scikit-learn pandas numpy flask gunicorn

COPY train.py /opt/ml/code/train.py
COPY serve.py /opt/ml/code/serve.py

# Container decides mode based on how it's invoked
# Training: python train.py
# Inference: python serve.py
```

---

## SageMaker Container Contract (EXAM CRITICAL)

### Directory Structure

```
/opt/ml/
├── input/
│   ├── config/
│   │   ├── hyperparameters.json     # Training hyperparameters
│   │   ├── resourceConfig.json      # Cluster configuration
│   │   └── inputdataconfig.json     # Data channel info
│   └── data/
│       ├── train/                   # Training data channel
│       └── validation/              # Validation data channel
│
├── model/                           # SAVE MODEL HERE (training)
│                                    # LOAD MODEL FROM HERE (inference)
│
├── output/
│   └── failure                      # Write failure message here
│
└── code/                            # Your scripts
```

### Required Endpoints for Inference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/ping` | GET | Health check (return 200) |
| `/invocations` | POST | Inference requests |

### Exam Tip: Know the Paths
- Training saves model to: `/opt/ml/model/`
- Inference loads model from: `/opt/ml/model/`
- Training data in: `/opt/ml/input/data/<channel>/`
- Hyperparameters in: `/opt/ml/input/config/hyperparameters.json`

---

## Building and Pushing to ECR

```bash
# Set variables
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=us-east-1
REPO_NAME=my-ml-container
TAG=latest

# Create ECR repository
aws ecr create-repository --repository-name ${REPO_NAME}

# Authenticate Docker to ECR
aws ecr get-login-password --region ${REGION} | \
    docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com

# Build container
docker build -t ${REPO_NAME}:${TAG} .

# Tag for ECR
docker tag ${REPO_NAME}:${TAG} ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${REPO_NAME}:${TAG}

# Push to ECR
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${REPO_NAME}:${TAG}
```

---

## Sample Training Script

```python
#!/usr/bin/env python
"""
Custom training script following SageMaker contract.
"""

import os
import json
import pickle
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# SageMaker paths (EXAM: Know these!)
MODEL_DIR = os.environ.get('SM_MODEL_DIR', '/opt/ml/model')
TRAIN_DIR = os.environ.get('SM_CHANNEL_TRAIN', '/opt/ml/input/data/train')
HYPERPARAMS_PATH = '/opt/ml/input/config/hyperparameters.json'


def load_hyperparameters():
    """Load hyperparameters from SageMaker config."""
    with open(HYPERPARAMS_PATH, 'r') as f:
        return json.load(f)


def train():
    # Load hyperparameters
    params = load_hyperparameters()
    n_estimators = int(params.get('n_estimators', 100))
    max_depth = int(params.get('max_depth', 10))

    # Load training data
    train_file = os.path.join(TRAIN_DIR, 'train.csv')
    df = pd.read_csv(train_file)

    X = df.drop('target', axis=1)
    y = df['target']

    # Train model
    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth
    )
    model.fit(X, y)

    # CRITICAL: Save to /opt/ml/model/
    model_path = os.path.join(MODEL_DIR, 'model.pkl')
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)

    print(f"Model saved to {model_path}")


if __name__ == '__main__':
    train()
```

---

## Sample Inference Script

```python
#!/usr/bin/env python
"""
Custom inference script with required endpoints.
"""

import os
import json
import pickle
import flask
import pandas as pd

app = flask.Flask(__name__)

# Load model (EXAM: Load from /opt/ml/model/)
MODEL_PATH = '/opt/ml/model/model.pkl'
model = None


def load_model():
    global model
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)


@app.route('/ping', methods=['GET'])
def ping():
    """
    Health check endpoint.
    EXAM TIP: Must return 200 for SageMaker health checks.
    """
    health = model is not None
    status = 200 if health else 404
    return flask.Response(status=status)


@app.route('/invocations', methods=['POST'])
def invoke():
    """
    Inference endpoint.
    EXAM TIP: This handles all inference requests.
    """
    # Get content type
    content_type = flask.request.content_type

    # Parse input based on content type
    if content_type == 'text/csv':
        data = flask.request.data.decode('utf-8')
        df = pd.read_csv(io.StringIO(data), header=None)
    elif content_type == 'application/json':
        data = flask.request.get_json()
        df = pd.DataFrame(data)
    else:
        return flask.Response(
            response=f"Unsupported content type: {content_type}",
            status=415
        )

    # Make predictions
    predictions = model.predict(df)

    # Return predictions
    return flask.Response(
        response=json.dumps(predictions.tolist()),
        status=200,
        mimetype='application/json'
    )


if __name__ == '__main__':
    load_model()
    app.run(host='0.0.0.0', port=8080)
```

---

## Using Custom Container in SageMaker

```python
import sagemaker
from sagemaker.estimator import Estimator

# Your ECR image URI
image_uri = f"{account_id}.dkr.ecr.{region}.amazonaws.com/my-ml-container:latest"

# Create estimator with custom container
estimator = Estimator(
    image_uri=image_uri,
    role=role,
    instance_count=1,
    instance_type='ml.m5.xlarge',
    output_path=f's3://{bucket}/models/',
    hyperparameters={
        'n_estimators': 100,
        'max_depth': 10
    }
)

# Train
estimator.fit({'train': 's3://bucket/train/'})

# Deploy
predictor = estimator.deploy(
    initial_instance_count=1,
    instance_type='ml.m5.large'
)
```

---

## Bring Your Own Container (BYOC) vs Script Mode

| Approach | When to Use | Complexity |
|----------|------------|------------|
| **Script Mode** | Custom code, standard framework | Low |
| **BYOC** | Custom framework, dependencies | High |
| **Extend Image** | Add libraries to SageMaker image | Medium |

### Script Mode Example

```python
# Script mode - use SageMaker container, provide your script
estimator = Estimator(
    image_uri=sagemaker.image_uris.retrieve('sklearn', region, '1.0-1'),
    role=role,
    entry_point='train.py',  # Your script
    source_dir='scripts/',   # Directory with your code
    instance_type='ml.m5.xlarge',
    ...
)
```

---

## Exam Question Patterns

### Pattern 1: Custom Framework
> "Need to use a proprietary ML framework not supported by SageMaker..."

**Answer**: Build custom container, push to ECR

### Pattern 2: Path Knowledge
> "Where should training script save model artifacts?"

**Answer**: `/opt/ml/model/`

### Pattern 3: Inference Endpoints
> "What endpoints must inference container implement?"

**Answer**: `/ping` (GET) and `/invocations` (POST)

### Pattern 4: Container Choice
> "Want to use PyTorch with custom preprocessing..."

**Answer**: Script Mode (use SageMaker PyTorch container + custom script)

### Pattern 5: Health Check
> "Endpoint not becoming healthy..."

**Answer**: Check `/ping` endpoint returns 200

---

## Checklist

- [ ] Know when to use custom containers vs Script Mode
- [ ] Understand the /opt/ml/ directory structure
- [ ] Know required inference endpoints (/ping, /invocations)
- [ ] Understand how to build and push to ECR
- [ ] Know the container contract for training and inference

---

## Next Steps

After completing this module, proceed to:
- [09 - Bedrock RAG](../09-bedrock-rag/) - Generative AI with Amazon Bedrock
