# 14 - Amazon EMR for Spark ML

> **Exam Weight**: Part of Data Preparation domain (28%)
> **Priority**: MEDIUM - Big data ML processing

## What is Amazon EMR?

Amazon EMR (Elastic MapReduce) is a managed big data platform for running Apache Spark, Hadoop, and other frameworks at scale. For ML, it's used for distributed data processing and training.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         AMAZON EMR FOR ML                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      EMR CLUSTER                                │   │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐   │   │
│  │  │  Master   │  │   Core    │  │   Core    │  │   Task    │   │   │
│  │  │   Node    │  │   Node    │  │   Node    │  │   Node    │   │   │
│  │  └───────────┘  └───────────┘  └───────────┘  └───────────┘   │   │
│  │       │              │              │              │          │   │
│  │       └──────────────┴──────────────┴──────────────┘          │   │
│  │                           │                                    │   │
│  │                    ┌──────┴──────┐                            │   │
│  │                    │  SPARK ML   │                            │   │
│  │                    │  LIBRARY    │                            │   │
│  │                    └─────────────┘                            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              │                                          │
│              ┌───────────────┼───────────────┐                         │
│              ▼               ▼               ▼                         │
│         ┌─────────┐    ┌─────────┐    ┌─────────┐                     │
│         │   S3    │    │   S3    │    │   S3    │                     │
│         │ (Input) │    │(Output) │    │ (Model) │                     │
│         └─────────┘    └─────────┘    └─────────┘                     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## EMR Node Types (KNOW FOR EXAM)

| Node Type | Purpose | Required | Spot Eligible |
|-----------|---------|----------|---------------|
| **Master** | Cluster coordination, resource management | Yes | No (production) |
| **Core** | Run tasks + store HDFS data | Yes | Careful (data loss) |
| **Task** | Run tasks only (no storage) | No | Yes (safe) |

### Exam Tip: Spot Instances
- **Master**: Don't use Spot in production
- **Core**: Risk of data loss if terminated
- **Task**: Safe for Spot (no data storage)

---

## EMR Deployment Options

| Option | Use Case | Exam Scenario |
|--------|----------|---------------|
| **EMR on EC2** | Full control, HDFS | Traditional big data |
| **EMR on EKS** | Kubernetes integration | Container workloads |
| **EMR Serverless** | No cluster management | Ad-hoc processing |
| **EMR Studio** | Notebooks, development | Data exploration |

---

## Spark MLlib

Spark's machine learning library for distributed ML.

### Supported Algorithms

| Category | Algorithms |
|----------|------------|
| **Classification** | Logistic Regression, Decision Trees, Random Forest, GBT, Naive Bayes |
| **Regression** | Linear Regression, Decision Trees, Random Forest, GBT |
| **Clustering** | K-Means, LDA, Gaussian Mixture |
| **Recommendation** | ALS (Alternating Least Squares) |
| **Feature Engineering** | PCA, Word2Vec, TF-IDF, Normalizer, StandardScaler |

### Basic Example

```python
from pyspark.ml import Pipeline
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.feature import VectorAssembler, StringIndexer
from pyspark.ml.evaluation import BinaryClassificationEvaluator

# Load data
df = spark.read.parquet("s3://bucket/data/")

# Feature engineering
assembler = VectorAssembler(
    inputCols=["feature1", "feature2", "feature3"],
    outputCol="features"
)

indexer = StringIndexer(inputCol="label", outputCol="labelIndex")

# Model
rf = RandomForestClassifier(
    featuresCol="features",
    labelCol="labelIndex",
    numTrees=100
)

# Pipeline
pipeline = Pipeline(stages=[assembler, indexer, rf])

# Train
model = pipeline.fit(train_df)

# Evaluate
predictions = model.transform(test_df)
evaluator = BinaryClassificationEvaluator(labelCol="labelIndex")
auc = evaluator.evaluate(predictions)
print(f"AUC: {auc}")

# Save model to S3
model.write().overwrite().save("s3://bucket/models/rf-model")
```

---

## EMR + SageMaker Integration

### Pattern 1: EMR for Processing, SageMaker for Training

```
┌─────────┐     ┌─────────┐     ┌─────────────┐
│   S3    │────▶│   EMR   │────▶│  SageMaker  │
│  (Raw)  │     │  (ETL)  │     │  Training   │
└─────────┘     └─────────┘     └─────────────┘
```

### Pattern 2: EMR for Distributed Training

```python
# Use SageMaker Spark library on EMR
from sagemaker_pyspark import SageMakerEstimator
from sagemaker_pyspark.algorithms import XGBoostSageMakerEstimator

xgb = XGBoostSageMakerEstimator(
    sagemakerRole=role,
    trainingInstanceType="ml.m5.xlarge",
    trainingInstanceCount=1,
    endpointInstanceType="ml.m5.large",
    endpointInitialInstanceCount=1
)

xgb.fit(training_df)
```

---

## EMR Step Execution

Submit jobs as steps to the cluster.

```python
import boto3

emr = boto3.client('emr')

# Add Spark step
response = emr.add_job_flow_steps(
    JobFlowId='j-XXXXXXXXXXXXX',
    Steps=[
        {
            'Name': 'ML Training Job',
            'ActionOnFailure': 'CONTINUE',
            'HadoopJarStep': {
                'Jar': 'command-runner.jar',
                'Args': [
                    'spark-submit',
                    '--deploy-mode', 'cluster',
                    '--master', 'yarn',
                    's3://bucket/scripts/train.py',
                    '--data', 's3://bucket/data/',
                    '--output', 's3://bucket/models/'
                ]
            }
        }
    ]
)
```

---

## EMR Serverless

Run Spark jobs without managing clusters.

```python
import boto3

emr_serverless = boto3.client('emr-serverless')

# Create application
app = emr_serverless.create_application(
    name='ml-app',
    releaseLabel='emr-6.9.0',
    type='SPARK'
)

# Submit job
job = emr_serverless.start_job_run(
    applicationId=app['applicationId'],
    executionRoleArn=role,
    jobDriver={
        'sparkSubmit': {
            'entryPoint': 's3://bucket/scripts/train.py',
            'sparkSubmitParameters': '--conf spark.executor.cores=4'
        }
    },
    configurationOverrides={
        'monitoringConfiguration': {
            's3MonitoringConfiguration': {
                'logUri': 's3://bucket/logs/'
            }
        }
    }
)
```

---

## EMR vs Glue vs SageMaker Processing

| Feature | EMR | Glue | SageMaker Processing |
|---------|-----|------|---------------------|
| **Engine** | Spark, Hadoop, etc. | Spark (managed) | Any container |
| **Management** | Cluster management | Serverless | Serverless |
| **ML Libraries** | MLlib, custom | Limited | Full flexibility |
| **Use Case** | Complex big data | ETL-focused | ML preprocessing |
| **Cost Model** | Per instance-hour | Per DPU-hour | Per instance-hour |

### Exam Tip: When to Choose
- **EMR**: Complex Spark ML, need full Spark control
- **Glue**: ETL-focused, serverless preferred
- **SageMaker Processing**: ML-specific processing, sklearn, etc.

---

## Exam Question Patterns

### Pattern 1: Large Scale ML
> "Train model on petabytes of data..."

**Answer**: EMR with Spark MLlib

### Pattern 2: Cost Optimization
> "Use Spot instances for ML processing..."

**Answer**: EMR Task nodes with Spot

### Pattern 3: Serverless Big Data
> "Process big data without cluster management..."

**Answer**: EMR Serverless or Glue

### Pattern 4: Custom Spark
> "Need specific Spark version and libraries..."

**Answer**: EMR on EC2

### Pattern 5: Integration
> "Preprocess in Spark, train in SageMaker..."

**Answer**: EMR for processing → S3 → SageMaker

---

## Checklist

- [ ] Know EMR node types and Spot instance usage
- [ ] Understand Spark MLlib algorithms
- [ ] Know EMR deployment options (EC2, EKS, Serverless)
- [ ] Understand EMR + SageMaker integration patterns
- [ ] Know when to use EMR vs Glue vs SageMaker

---

## Next Steps

After completing this module, proceed to:
- [15 - Athena Analysis](../15-athena-analysis/) - Query ML data with SQL
