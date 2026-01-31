# AWS Machine Learning Engineer Associate - Exam Preparation

A hands-on project-based learning path for the **AWS Certified Machine Learning Engineer - Associate (MLA-C01)** certification.

**Quick Links:** [Cheat Sheet](./CHEATSHEET.md) | [Start Learning](#learning-path--projects)

## Exam Overview

| Attribute | Details |
|-----------|---------|
| **Exam Code** | MLA-C01 |
| **Duration** | 170 minutes |
| **Questions** | 85 questions |
| **Passing Score** | 720/1000 |
| **Cost** | $150 USD |
| **Format** | Multiple choice, multiple response |

## Exam Domains

| Domain | Weight | Status |
|--------|--------|--------|
| 1. Data Preparation & Feature Engineering | 28% | ⬜ |
| 2. ML Model Development | 26% | ⬜ |
| 3. Deployment & Orchestration | 22% | ⬜ |
| 4. Monitoring & Security | 24% | ⬜ |

---

## Learning Path & Projects

Each project contains:
- **README.md** - Concepts, theory, and exam-relevant notes
- **LAB.md** - Hands-on exercises with step-by-step instructions
- **Code examples** - Python/CLI scripts to run

### Phase 1: Core Foundation (60% of exam weight)

| # | Project | Service Focus | Domain | Status |
|---|---------|---------------|--------|--------|
| 01 | [SageMaker Basics](./01-sagemaker-basics/) | Amazon SageMaker | 1, 2, 3 | ⬜ |
| 02 | [S3 Data Lake](./02-s3-data-lake/) | Amazon S3 | 1 | ⬜ |
| 03 | [Glue ETL](./03-glue-etl/) | AWS Glue | 1 | ⬜ |
| 04 | [Feature Store](./04-feature-store/) | SageMaker Feature Store | 1 | ⬜ |

### Phase 2: MLOps & Automation (High Priority)

| # | Project | Service Focus | Domain | Status |
|---|---------|---------------|--------|--------|
| 05 | [SageMaker Pipelines](./05-sagemaker-pipelines/) | SageMaker Pipelines | 3 | ⬜ |
| 06 | [Step Functions ML](./06-step-functions-ml/) | AWS Step Functions | 3 | ⬜ |
| 07 | [Model Monitor](./07-model-monitor/) | SageMaker Model Monitor | 4 | ⬜ |
| 08 | [Custom Container](./08-custom-container-ecr/) | Amazon ECR | 2 | ⬜ |

### Phase 3: AI Services (Medium Priority)

| # | Project | Service Focus | Domain | Status |
|---|---------|---------------|--------|--------|
| 09 | [Bedrock RAG](./09-bedrock-rag/) | Amazon Bedrock | 2 | ⬜ |
| 10 | [Rekognition App](./10-rekognition-app/) | Amazon Rekognition | 2 | ⬜ |
| 11 | [Comprehend NLP](./11-comprehend-nlp/) | Amazon Comprehend | 2 | ⬜ |
| 12 | [Textract Docs](./12-textract-docs/) | Amazon Textract | 2 | ⬜ |

### Phase 4: Supporting Services (Lower Priority)

| # | Project | Service Focus | Domain | Status |
|---|---------|---------------|--------|--------|
| 13 | [Lambda Inference](./13-lambda-inference/) | AWS Lambda | 3 | ⬜ |
| 14 | [EMR Spark ML](./14-emr-spark-ml/) | Amazon EMR | 1 | ⬜ |
| 15 | [Athena Analysis](./15-athena-analysis/) | Amazon Athena | 1 | ⬜ |
| 16 | [CloudWatch Alerts](./16-cloudwatch-alerts/) | CloudWatch + EventBridge | 4 | ⬜ |

---

## Key Services Quick Reference

### Tier 1: Must Master (Appears in 60%+ questions)

| Service | Primary Use | Exam Focus |
|---------|-------------|------------|
| **Amazon SageMaker** | End-to-end ML platform | Training, deployment, built-in algorithms, instance types |
| **Amazon S3** | Object storage | Data lake, versioning, lifecycle, access points |
| **AWS Glue** | ETL & Data Catalog | Data preparation, crawlers, jobs, schema detection |
| **SageMaker Feature Store** | Feature management | Online/offline store, feature groups |

### Tier 2: Important (Appears in 25%+ questions)

| Service | Primary Use | Exam Focus |
|---------|-------------|------------|
| **SageMaker Pipelines** | ML CI/CD | Pipeline steps, automation, model registry |
| **Step Functions** | Workflow orchestration | State machines, error handling |
| **Model Monitor** | Model observability | Data drift, model drift, bias detection |
| **Amazon ECR** | Container registry | Custom training/inference containers |
| **Amazon Bedrock** | Generative AI | Foundation models, RAG, fine-tuning |

### Tier 3: Know the Basics (Occasional questions)

| Service | Primary Use | Exam Focus |
|---------|-------------|------------|
| **Rekognition** | Image/Video AI | Labels, faces, text detection |
| **Comprehend** | NLP | Sentiment, entities, PII detection |
| **Textract** | Document AI | Forms, tables, queries |
| **Transcribe** | Speech-to-text | Transcription, custom vocabulary |
| **Lambda** | Serverless compute | Real-time inference, event triggers |
| **EMR** | Big data | Spark ML, distributed processing |

---

## Exam Tips

### What to Focus On

1. **SageMaker Instance Types**: Know when to use ml.m5, ml.p3, ml.g4dn, ml.inf1
2. **SageMaker Built-in Algorithms**: XGBoost, Linear Learner, BlazingText, Image Classification
3. **Data Formats**: RecordIO, Parquet, CSV, Pipe mode vs File mode
4. **Deployment Options**: Real-time, Batch, Async, Serverless endpoints
5. **Feature Store**: Online vs Offline, feature groups, ingestion patterns
6. **Model Monitor**: Data quality, model quality, bias drift, feature attribution drift
7. **Security**: IAM roles, VPC configs, encryption at rest/transit

### Common Exam Scenarios

- "Most cost-effective way to..." → Think Spot instances, serverless, right-sizing
- "Lowest latency..." → Think real-time endpoints, ml.inf1 (Inferentia)
- "Process large dataset..." → Think Pipe mode, distributed training, EMR
- "Automate retraining..." → Think Pipelines, Step Functions, EventBridge
- "Detect drift..." → Think Model Monitor
- "Feature reuse across teams..." → Think Feature Store

---

## Progress Tracker

- [ ] Phase 1 Complete
- [ ] Phase 2 Complete
- [ ] Phase 3 Complete
- [ ] Phase 4 Complete
- [ ] Practice Exams Complete
- [ ] Exam Scheduled
- [ ] **CERTIFIED!**

---

## Resources

- [AWS ML Engineer Associate Exam Guide](https://aws.amazon.com/certification/certified-machine-learning-engineer-associate/)
- [AWS Skill Builder](https://skillbuilder.aws/)
- [SageMaker Documentation](https://docs.aws.amazon.com/sagemaker/)
- [AWS ML Blog](https://aws.amazon.com/blogs/machine-learning/)
