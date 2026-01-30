# 11 - Amazon Comprehend NLP

> **Exam Weight**: Part of AI Services knowledge
> **Priority**: MEDIUM - Pre-built NLP service

## What is Amazon Comprehend?

Amazon Comprehend is a natural language processing (NLP) service that uses machine learning to find insights and relationships in text.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    AMAZON COMPREHEND CAPABILITIES                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  PRE-TRAINED                          CUSTOM                           │
│  ────────────                          ──────                           │
│  • Sentiment Analysis                 • Custom Classification          │
│  • Entity Recognition                 • Custom Entity Recognition      │
│  • Key Phrase Extraction                                               │
│  • Language Detection                 COMPREHEND MEDICAL               │
│  • PII Detection                      ──────────────────               │
│  • Syntax Analysis                    • Medical Entity Extraction      │
│  • Topic Modeling                     • PHI Detection                  │
│                                       • ICD-10/RxNorm Linking          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Key APIs (KNOW FOR EXAM)

| API | Purpose | Output |
|-----|---------|--------|
| `detect_sentiment` | Sentiment analysis | POSITIVE, NEGATIVE, NEUTRAL, MIXED |
| `detect_entities` | Named entity recognition | PERSON, LOCATION, ORGANIZATION, etc. |
| `detect_key_phrases` | Key phrase extraction | Important phrases |
| `detect_dominant_language` | Language detection | Language code |
| `detect_pii_entities` | PII detection | EMAIL, SSN, PHONE, etc. |
| `detect_syntax` | Part-of-speech tagging | NOUN, VERB, ADJ, etc. |

---

## Basic Usage

### Sentiment Analysis

```python
import boto3

comprehend = boto3.client('comprehend')

response = comprehend.detect_sentiment(
    Text="I love this product! It's amazing.",
    LanguageCode='en'
)

print(f"Sentiment: {response['Sentiment']}")  # POSITIVE
print(f"Scores: {response['SentimentScore']}")
# {'Positive': 0.99, 'Negative': 0.001, 'Neutral': 0.005, 'Mixed': 0.004}
```

### Entity Recognition

```python
response = comprehend.detect_entities(
    Text="Amazon was founded by Jeff Bezos in Seattle in 1994.",
    LanguageCode='en'
)

for entity in response['Entities']:
    print(f"{entity['Text']}: {entity['Type']} ({entity['Score']:.2f})")
# Amazon: ORGANIZATION (0.99)
# Jeff Bezos: PERSON (0.99)
# Seattle: LOCATION (0.98)
# 1994: DATE (0.99)
```

### Entity Types

| Type | Description | Example |
|------|-------------|---------|
| PERSON | Individuals | "Jeff Bezos" |
| LOCATION | Places | "Seattle" |
| ORGANIZATION | Companies, groups | "Amazon" |
| DATE | Dates | "January 2024" |
| QUANTITY | Numerical values | "100 dollars" |
| COMMERCIAL_ITEM | Products | "iPhone" |
| EVENT | Events | "Olympics" |

### Key Phrase Extraction

```python
response = comprehend.detect_key_phrases(
    Text="Machine learning is transforming healthcare with predictive analytics.",
    LanguageCode='en'
)

for phrase in response['KeyPhrases']:
    print(f"{phrase['Text']} ({phrase['Score']:.2f})")
# Machine learning (0.99)
# healthcare (0.98)
# predictive analytics (0.97)
```

### PII Detection

```python
response = comprehend.detect_pii_entities(
    Text="Contact John at john@email.com or 555-123-4567",
    LanguageCode='en'
)

for entity in response['Entities']:
    print(f"{entity['Type']}: Position {entity['BeginOffset']}-{entity['EndOffset']}")
# NAME: Position 8-12
# EMAIL: Position 16-30
# PHONE: Position 34-46
```

### PII Types

| Type | Description |
|------|-------------|
| EMAIL | Email addresses |
| PHONE | Phone numbers |
| SSN | Social security numbers |
| CREDIT_DEBIT_NUMBER | Credit card numbers |
| NAME | Person names |
| ADDRESS | Physical addresses |
| DATE_TIME | Dates with time |
| BANK_ACCOUNT_NUMBER | Bank accounts |

---

## Batch Processing

For large-scale processing, use batch/async APIs.

```python
# Start batch job
response = comprehend.start_entities_detection_job(
    InputDataConfig={
        'S3Uri': 's3://bucket/input/',
        'InputFormat': 'ONE_DOC_PER_LINE'
    },
    OutputDataConfig={
        'S3Uri': 's3://bucket/output/'
    },
    DataAccessRoleArn=role_arn,
    LanguageCode='en'
)

job_id = response['JobId']

# Check status
response = comprehend.describe_entities_detection_job(JobId=job_id)
print(f"Status: {response['EntitiesDetectionJobProperties']['JobStatus']}")
```

---

## Custom Classification

Train custom text classifiers.

```python
# Create custom classifier
response = comprehend.create_document_classifier(
    DocumentClassifierName='support-ticket-classifier',
    DataAccessRoleArn=role_arn,
    InputDataConfig={
        'DataFormat': 'COMPREHEND_CSV',
        'S3Uri': 's3://bucket/training-data.csv'  # label,text format
    },
    OutputDataConfig={
        'S3Uri': 's3://bucket/output/'
    },
    LanguageCode='en',
    Mode='MULTI_CLASS'  # or MULTI_LABEL
)

# After training, create endpoint
response = comprehend.create_endpoint(
    EndpointName='ticket-classifier-endpoint',
    ModelArn=classifier_arn,
    DesiredInferenceUnits=1
)

# Classify text
response = comprehend.classify_document(
    Text="I can't login to my account",
    EndpointArn=endpoint_arn
)
# {'Classes': [{'Name': 'account-issue', 'Score': 0.95}, ...]}
```

### Training Data Format

```csv
# COMPREHEND_CSV format: label,text
BILLING,I need to update my payment method
TECHNICAL,The app crashes when I open it
ACCOUNT,Reset my password please
```

---

## Custom Entity Recognition

Train to recognize domain-specific entities.

```python
response = comprehend.create_entity_recognizer(
    RecognizerName='product-recognizer',
    DataAccessRoleArn=role_arn,
    InputDataConfig={
        'EntityTypes': [
            {'Type': 'PRODUCT'},
            {'Type': 'FEATURE'}
        ],
        'Documents': {
            'S3Uri': 's3://bucket/documents/'
        },
        'Annotations': {
            'S3Uri': 's3://bucket/annotations.csv'
        }
    },
    LanguageCode='en'
)
```

---

## Comprehend Medical

Specialized for healthcare text.

```python
comprehend_medical = boto3.client('comprehendmedical')

# Detect medical entities
response = comprehend_medical.detect_entities_v2(
    Text="Patient has type 2 diabetes and takes metformin 500mg twice daily."
)

for entity in response['Entities']:
    print(f"{entity['Text']}: {entity['Category']} - {entity['Type']}")
# type 2 diabetes: MEDICAL_CONDITION - DX_NAME
# metformin: MEDICATION - GENERIC_NAME
# 500mg: MEDICATION - DOSAGE
```

### Medical Entity Categories

| Category | Description |
|----------|-------------|
| MEDICATION | Drug names, dosage |
| MEDICAL_CONDITION | Diagnoses, symptoms |
| ANATOMY | Body parts |
| PROTECTED_HEALTH_INFORMATION | PHI data |
| TEST_TREATMENT_PROCEDURE | Medical procedures |
| TIME_EXPRESSION | Treatment timing |

---

## Exam Question Patterns

### Pattern 1: Sentiment Analysis
> "Analyze customer feedback sentiment..."

**Answer**: Comprehend detect_sentiment

### Pattern 2: Entity Extraction
> "Extract names, places, dates from documents..."

**Answer**: Comprehend detect_entities

### Pattern 3: PII Detection
> "Identify personal information in text..."

**Answer**: Comprehend detect_pii_entities

### Pattern 4: Custom Categories
> "Classify support tickets into categories..."

**Answer**: Comprehend Custom Classification

### Pattern 5: Medical Text
> "Extract medication information from clinical notes..."

**Answer**: Comprehend Medical

### Pattern 6: Large Scale
> "Process millions of documents..."

**Answer**: Comprehend batch jobs (async API)

---

## Comprehend vs Bedrock

| Feature | Comprehend | Bedrock |
|---------|------------|---------|
| **Type** | Pre-trained NLP tasks | Foundation models |
| **Tasks** | Sentiment, entities, etc. | General text generation |
| **Custom** | Train classifiers | Fine-tune FMs |
| **Use Case** | Structured NLP tasks | Open-ended generation |

---

## Checklist

- [ ] Know main Comprehend APIs and outputs
- [ ] Understand entity types and PII types
- [ ] Know custom classification and entity recognition
- [ ] Understand batch processing for scale
- [ ] Know Comprehend Medical for healthcare

---

## Next Steps

After completing this module, proceed to:
- [12 - Textract Docs](../12-textract-docs/) - Document AI
