# AWS ML Engineer Associate - Exam Cheat Sheet

Quick reference for key concepts tested on the MLA-C01 exam.

---

## SageMaker Built-in Algorithms

| Algorithm | Type | Use Case | Input Format |
|-----------|------|----------|--------------|
| **XGBoost** | Classification/Regression | Tabular data, structured | CSV, LibSVM, Parquet |
| **Linear Learner** | Classification/Regression | Binary/multiclass, regression | RecordIO, CSV |
| **BlazingText** | NLP | Text classification, Word2Vec | Text file (one sentence/line) |
| **Image Classification** | CV | Image labeling | RecordIO, image files |
| **Object Detection** | CV | Bounding boxes | RecordIO, JSON |
| **Semantic Segmentation** | CV | Pixel-level classification | PNG images |
| **K-Means** | Clustering | Unsupervised grouping | RecordIO, CSV |
| **PCA** | Dimensionality Reduction | Feature reduction | RecordIO, CSV |
| **Random Cut Forest** | Anomaly Detection | Outlier detection | RecordIO, CSV |
| **DeepAR** | Time Series | Forecasting | JSON Lines |
| **Factorization Machines** | Recommendation | Sparse data, click prediction | RecordIO |

---

## SageMaker Instance Types

| Prefix | Type | Use Case |
|--------|------|----------|
| **ml.t** | General (burstable) | Development, testing |
| **ml.m** | General purpose | Balanced workloads |
| **ml.c** | Compute optimized | CPU-intensive training |
| **ml.p** | GPU (NVIDIA) | Deep learning training |
| **ml.g** | GPU (graphics) | Inference, smaller models |
| **ml.inf** | Inferentia | High-throughput inference |

**Key Points:**
- Training: Use `ml.p` for deep learning, `ml.c` for classical ML
- Inference: Use `ml.inf` for cost-effective, `ml.g` for flexibility
- Spot instances: Up to 90% savings for training (use checkpoints!)

---

## S3 Storage Classes

| Class | Use Case | Retrieval |
|-------|----------|-----------|
| **Standard** | Frequent access | Immediate |
| **Intelligent-Tiering** | Unknown patterns | Automatic |
| **Standard-IA** | Infrequent, quick access | Immediate |
| **One Zone-IA** | Non-critical, infrequent | Immediate |
| **Glacier Instant** | Archive, immediate access | Milliseconds |
| **Glacier Flexible** | Archive, hours access | Minutes to hours |
| **Glacier Deep Archive** | Long-term archive | 12-48 hours |

**ML Data Patterns:**
- Raw data → Standard or Intelligent-Tiering
- Processed features → Standard-IA after 30 days
- Old model artifacts → Glacier after 90 days

---

## AWS Glue Key Concepts

| Concept | Purpose |
|---------|---------|
| **Data Catalog** | Metadata store (tables, schemas) |
| **Crawlers** | Auto-discover schema from S3 |
| **ETL Jobs** | Transform data (PySpark/Python) |
| **Job Bookmarks** | Track processed data, avoid reprocessing |
| **DynamicFrame** | Schema-flexible DataFrame |
| **Glue Studio** | Visual ETL builder |

**Exam Tips:**
- Crawlers populate the Data Catalog
- Job bookmarks = incremental processing
- DynamicFrame handles schema inconsistencies

---

## SageMaker Feature Store

| Store Type | Latency | Use Case |
|------------|---------|----------|
| **Online Store** | Single-digit ms | Real-time inference |
| **Offline Store** | Minutes | Batch training, analysis |

**Key Features:**
- Point-in-time queries (avoid data leakage)
- Automatic sync between online/offline
- Integrates with Athena for SQL queries

---

## SageMaker Pipelines Steps

| Step | Purpose |
|------|---------|
| `ProcessingStep` | Data preprocessing |
| `TrainingStep` | Model training |
| `CreateModelStep` | Create model artifact |
| `TransformStep` | Batch inference |
| `ConditionStep` | Branching logic |
| `RegisterModel` | Add to Model Registry |
| `TuningStep` | Hyperparameter optimization |

---

## Model Monitor Types

| Monitor | Detects |
|---------|---------|
| **Data Quality** | Feature drift, missing values |
| **Model Quality** | Accuracy degradation |
| **Bias Drift** | Fairness metric changes |
| **Feature Attribution** | Explainability changes |

**Baseline:** Always create from training data

---

## Container Paths (/opt/ml/)

```
/opt/ml/
├── input/
│   ├── config/          # hyperparameters.json
│   └── data/
│       └── {channel}/   # train/, validation/
├── model/               # Save model artifacts here
├── output/              # failure file
└── code/                # Your scripts
```

**Remember:** SageMaker mounts these automatically

---

## Amazon Bedrock

| Model Provider | Models |
|----------------|--------|
| **Anthropic** | Claude (3, 3.5) |
| **Amazon** | Titan (Text, Embeddings, Image) |
| **AI21 Labs** | Jurassic |
| **Cohere** | Command, Embed |
| **Meta** | Llama 2 |
| **Stability AI** | Stable Diffusion |

**RAG Pattern:**
1. Embed documents → Vector store
2. User query → Embed query
3. Semantic search → Find relevant chunks
4. Augment prompt → Send to LLM

---

## AI Services Quick Reference

| Service | Use Case | Key API |
|---------|----------|---------|
| **Rekognition** | Image/video analysis | `detect_faces`, `detect_labels`, `compare_faces` |
| **Comprehend** | NLP text analysis | `detect_sentiment`, `detect_entities`, `detect_pii` |
| **Textract** | Document extraction | `detect_document_text`, `analyze_document` |
| **Translate** | Language translation | `translate_text` |
| **Polly** | Text-to-speech | `synthesize_speech` |
| **Transcribe** | Speech-to-text | `start_transcription_job` |

---

## EMR Node Types

| Node | Role | Spot? |
|------|------|-------|
| **Master** | Coordinates cluster | No (critical) |
| **Core** | Store HDFS + process | Sometimes |
| **Task** | Processing only | Yes (ideal for Spot) |

**EMR vs Glue:**
- EMR: More control, persistent clusters, complex Spark
- Glue: Serverless, simpler, auto-scaling

---

## Lambda for ML

| Limit | Value |
|-------|-------|
| Memory | 128 MB - 10 GB |
| Timeout | 15 minutes max |
| Package size | 50 MB (zip), 250 MB (unzipped) |
| Container image | 10 GB |
| Ephemeral storage | 512 MB - 10 GB |

**When to use Lambda vs SageMaker:**
- Lambda: Small models, low latency, infrequent calls
- SageMaker: Large models, high throughput, GPUs needed

---

## CloudWatch Metrics for SageMaker

| Metric | Namespace |
|--------|-----------|
| `Invocations` | AWS/SageMaker |
| `ModelLatency` | AWS/SageMaker |
| `Invocation4XXErrors` | AWS/SageMaker |
| `Invocation5XXErrors` | AWS/SageMaker |
| `CPUUtilization` | /aws/sagemaker/Endpoints |
| `MemoryUtilization` | /aws/sagemaker/Endpoints |
| `GPUUtilization` | /aws/sagemaker/Endpoints |

---

## Cost Optimization Tips

1. **Spot Instances**: Training jobs (up to 90% savings)
2. **Savings Plans**: Predictable inference workloads
3. **Multi-Model Endpoints**: Multiple models, one endpoint
4. **Serverless Inference**: Sporadic traffic
5. **Inference Recommender**: Find optimal instance type
6. **S3 Lifecycle Policies**: Move old data to cheaper tiers
7. **Athena Partitioning**: Reduce data scanned (costs)

---

## Security Essentials

| Concept | Purpose |
|---------|---------|
| **VPC Endpoints** | Private connectivity to AWS services |
| **KMS** | Encryption at rest (S3, EBS, models) |
| **IAM Roles** | Service permissions |
| **Security Groups** | Network-level access control |
| **Private Subnets** | Isolate training/inference |

**SageMaker Security:**
- Enable network isolation for training
- Use VPC endpoints for S3 access
- Encrypt model artifacts with KMS

---

## Exam Day Reminders

1. **Read questions carefully** - Look for keywords (cost, latency, scale)
2. **Eliminate wrong answers** - Usually 2 are obviously wrong
3. **SageMaker is usually the answer** - For ML workloads
4. **AI Services for pre-built** - No training needed
5. **Cost questions** - Spot, Serverless, Multi-model
6. **Real-time vs Batch** - Endpoint vs Transform job
7. **Managed vs Custom** - Built-in algorithms first, custom if needed

---

## Quick Decision Tree

```
Need ML model?
├── Pre-trained capability exists?
│   └── YES → AI Services (Rekognition, Comprehend, etc.)
│   └── NO → Train custom model
│       ├── Tabular data?
│       │   └── XGBoost, Linear Learner
│       ├── Text data?
│       │   └── BlazingText, Comprehend Custom
│       ├── Image data?
│       │   └── Image Classification, Object Detection
│       └── Time series?
│           └── DeepAR

Deployment type?
├── Real-time, always on → SageMaker Endpoint
├── Real-time, sporadic → Serverless Inference
├── Batch processing → Transform Job
└── Lightweight, serverless → Lambda

Data processing?
├── Simple transformations → SageMaker Processing
├── Complex ETL → Glue or EMR
└── SQL queries → Athena
```

---

**Good luck on your exam!** 🎯
