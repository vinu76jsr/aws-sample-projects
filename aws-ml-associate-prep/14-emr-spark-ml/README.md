# 14 - Amazon EMR for Spark ML

> **Exam Weight**: Part of Data Preparation domain (28%)
> **Priority**: MEDIUM - Big data ML processing

## What is Amazon EMR?

Amazon EMR[^emr] (Elastic MapReduce) is a managed big data platform for running Apache Spark[^spark], Hadoop, and other frameworks at scale. For ML, it's used for distributed data processing and training.

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
| **Master**[^master-node] | Cluster coordination, resource management | Yes | No (production) |
| **Core**[^core-node] | Run tasks + store HDFS data | Yes | Careful (data loss) |
| **Task**[^task-node] | Run tasks only (no storage) | No | Yes (safe) |

### Exam Tip: Spot Instances[^spot-instances]
- **Master**: Don't use Spot in production
- **Core**: Risk of data loss if terminated
- **Task**: Safe for Spot (no data storage)

---

## EMR Deployment Options

| Option | Use Case | Exam Scenario |
|--------|----------|---------------|
| **EMR on EC2** | Full control, HDFS | Traditional big data |
| **EMR on EKS** | Kubernetes integration | Container workloads |
| **EMR Serverless**[^emr-serverless] | No cluster management | Ad-hoc processing |
| **EMR Studio** | Notebooks, development | Data exploration |

---

## Spark MLlib[^mllib]

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

## YARN[^yarn] Resource Management

YARN manages cluster resources in EMR:

```python
# spark-submit with YARN configuration
spark-submit \
    --master yarn \
    --deploy-mode cluster \
    --num-executors 10 \
    --executor-memory 4g \
    --executor-cores 2 \
    train.py
```

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

## Glossary

[^emr]: **EMR (Elastic MapReduce)** - AWS managed big data platform that simplifies running Apache Spark, Hadoop, Hive, and other frameworks for processing vast amounts of data.

[^spark]: **Spark** - Apache Spark is an open-source unified analytics engine for large-scale data processing, providing high-level APIs and an optimized engine for general execution graphs.

[^mllib]: **MLlib** - Apache Spark's scalable machine learning library providing common ML algorithms (classification, regression, clustering) designed for distributed computing.

[^master-node]: **Master Node** - The EMR node that coordinates the cluster, runs YARN ResourceManager, HDFS NameNode, and manages job scheduling and cluster state.

[^core-node]: **Core Node** - EMR nodes that run tasks and store data in HDFS. Losing core nodes can result in data loss if HDFS replication is insufficient.

[^task-node]: **Task Node** - EMR nodes that only run tasks without storing HDFS data. Ideal for Spot Instances since termination doesn't cause data loss.

[^spot-instances]: **Spot Instances** - AWS EC2 instances available at up to 90% discount by using spare capacity, but can be interrupted with 2-minute notice when capacity is needed.

[^yarn]: **YARN (Yet Another Resource Negotiator)** - Hadoop's cluster resource management layer that handles job scheduling and resource allocation across the cluster.

[^emr-serverless]: **EMR Serverless** - AWS service that allows running Spark and Hive applications without configuring, managing, or scaling clusters.

---

## Next Steps

After completing this module, proceed to:
- [15 - Athena Analysis](../15-athena-analysis/) - Query ML data with SQL
