# Lab 11: Amazon Comprehend NLP

## Overview
Use Amazon Comprehend[^comprehend] for natural language processing[^nlp] tasks.

**Duration**: 30-45 minutes
**Cost**: ~$1
**Prerequisites**: AWS Account

---

## Architecture Overview

```mermaid
flowchart TB
    subgraph Input["fa:fa-file-alt Text Input"]
        Single[fa:fa-file Single Document]
        Batch[fa:fa-copy Batch Documents]
        Async[fa:fa-clock Async Jobs]
    end

    subgraph Comprehend["fa:fa-language Amazon Comprehend APIs"]
        Sentiment[fa:fa-smile DetectSentiment<br/>Positive/Negative/Neutral]
        Entities[fa:fa-tags DetectEntities<br/>Person/Location/Org]
        KeyPhrases[fa:fa-key DetectKeyPhrases<br/>Important Terms]
        Language[fa:fa-globe DetectDominantLanguage]
        PII[fa:fa-user-secret DetectPiiEntities<br/>Personal Data]
        Syntax[fa:fa-spell-check DetectSyntax<br/>Part of Speech]
    end

    subgraph Custom["fa:fa-cogs Custom Models"]
        Classifier[fa:fa-sitemap Custom Classifier]
        EntityRec[fa:fa-crosshairs Custom Entity Recognition]
    end

    subgraph Output["fa:fa-file-alt Results"]
        JSON[fa:fa-code JSON Response]
        Scores[fa:fa-percentage Confidence Scores]
        Positions[fa:fa-map-marker-alt Text Positions]
    end

    Input --> Comprehend
    Input --> Custom
    Comprehend --> Output
    Custom --> Output

    style Input fill:#e3f2fd
    style Comprehend fill:#fff3e0
    style Custom fill:#e8f5e9
    style Output fill:#fce4ec
```

### Sentiment Analysis Flow

```mermaid
flowchart LR
    Text["fa:fa-comment Customer Review"] --> API[fa:fa-brain DetectSentiment]

    API --> Scores

    subgraph Scores["fa:fa-chart-pie Sentiment Scores"]
        Pos[fa:fa-smile Positive: 0.85]
        Neg[fa:fa-frown Negative: 0.05]
        Neu[fa:fa-meh Neutral: 0.08]
        Mix[fa:fa-random Mixed: 0.02]
    end

    Scores --> Result[fa:fa-check-circle Overall: POSITIVE]

    style Scores fill:#e8f5e9
```

### Entity Types

```mermaid
flowchart TB
    subgraph EntityTypes["fa:fa-tags Detected Entity Types"]
        PERSON[fa:fa-user PERSON<br/>Names of people]
        LOCATION[fa:fa-map-marker-alt LOCATION<br/>Places, addresses]
        ORG[fa:fa-building ORGANIZATION<br/>Companies, agencies]
        DATE[fa:fa-calendar DATE<br/>Dates and times]
        QUANTITY[fa:fa-hashtag QUANTITY<br/>Numbers, percentages]
        EVENT[fa:fa-calendar-check EVENT<br/>Named events]
        TITLE[fa:fa-id-badge TITLE<br/>Job titles, works]
        OTHER[fa:fa-ellipsis-h OTHER<br/>Miscellaneous]
    end

    Text[Input Text] --> EntityTypes

    style EntityTypes fill:#fff3e0
```

### PII Detection for Compliance

```mermaid
sequenceDiagram
    participant App as Application
    participant Comp as Comprehend
    participant Store as Data Store

    App->>Comp: DetectPiiEntities(text)
    Comp-->>App: PII locations + types

    alt PII Found
        App->>App: Mask/Redact PII
        App->>Store: Store sanitized data
    else No PII
        App->>Store: Store original data
    end
```

---

## Lab Objectives

- [ ] Perform sentiment analysis[^sentiment-analysis]
- [ ] Extract entities[^entity-recognition] from text
- [ ] Detect key phrases[^key-phrases]
- [ ] Identify PII[^pii-detection] data

---

## Part 1: Sentiment Analysis

```python
import boto3

comprehend = boto3.client('comprehend')

# Sample texts
texts = [
    "I love this product! It's absolutely amazing and exceeded my expectations.",
    "The service was terrible. I'm very disappointed with my purchase.",
    "The product arrived on time. It works as described.",
    "Great quality but shipping was slow. Mixed feelings overall."
]

print("Sentiment Analysis:")
print("-" * 50)

for text in texts:
    response = comprehend.detect_sentiment(
        Text=text,
        LanguageCode='en'
    )

    print(f"Text: {text[:50]}...")
    print(f"Sentiment: {response['Sentiment']}")
    print(f"Scores: Pos={response['SentimentScore']['Positive']:.2f}, "
          f"Neg={response['SentimentScore']['Negative']:.2f}")
    print()
```

---

## Part 2: Entity Recognition

```python
# Sample text with entities
text = """
Amazon Web Services was founded in 2006 and is headquartered in Seattle.
The CEO Andy Jassy announced new AI services at re:Invent 2024.
AWS has data centers across 99 availability zones worldwide.
"""

response = comprehend.detect_entities(
    Text=text,
    LanguageCode='en'
)

print("Named Entities:")
print("-" * 50)
for entity in response['Entities']:
    print(f"  {entity['Text']}")
    print(f"    Type: {entity['Type']}")
    print(f"    Confidence: {entity['Score']:.2f}")
    print()
```

---

## Part 3: Key Phrase Extraction

```python
text = """
Machine learning models require large amounts of training data
to achieve high accuracy. Feature engineering is a critical step
in the model development process. Deep learning has revolutionized
computer vision and natural language processing applications.
"""

response = comprehend.detect_key_phrases(
    Text=text,
    LanguageCode='en'
)

print("Key Phrases:")
print("-" * 50)
for phrase in response['KeyPhrases']:
    print(f"  {phrase['Text']} (Confidence: {phrase['Score']:.2f})")
```

---

## Part 4: PII Detection

```python
text = """
Customer John Smith placed an order today.
Contact email: john.smith@example.com
Phone: 555-123-4567
Credit card ending in 4242
SSN: 123-45-6789
"""

response = comprehend.detect_pii_entities(
    Text=text,
    LanguageCode='en'
)

print("PII Detected:")
print("-" * 50)
for entity in response['Entities']:
    # Get the actual text using offsets
    pii_text = text[entity['BeginOffset']:entity['EndOffset']]
    print(f"  Type: {entity['Type']}")
    print(f"  Text: {pii_text}")
    print(f"  Confidence: {entity['Score']:.2f}")
    print()
```

---

## Part 5: Language Detection

```python
texts = [
    "Hello, how are you today?",
    "Bonjour, comment allez-vous?",
    "Hola, cómo estás?",
    "こんにちは、お元気ですか？"
]

print("Language Detection:")
print("-" * 50)
for text in texts:
    response = comprehend.detect_dominant_language(Text=text)
    lang = response['Languages'][0]
    print(f"  '{text[:30]}...'")
    print(f"    Language: {lang['LanguageCode']} ({lang['Score']:.2f})")
    print()
```

---

## Part 6: Batch Processing (Optional)

```python
# For large-scale processing, use async batch jobs
# This is more cost-effective for >25,000 characters

# Example: Start batch job
# response = comprehend.start_entities_detection_job(
#     InputDataConfig={
#         'S3Uri': 's3://bucket/input/',
#         'InputFormat': 'ONE_DOC_PER_LINE'
#     },
#     OutputDataConfig={
#         'S3Uri': 's3://bucket/output/'
#     },
#     DataAccessRoleArn=role_arn,
#     LanguageCode='en'
# )
```

---

## Lab Summary

| Concept | What You Did |
|---------|--------------|
| **Sentiment** | Analyzed positive/negative/neutral |
| **Entities** | Extracted names, places, dates |
| **Key Phrases** | Identified important phrases |
| **PII** | Detected personal information |

---

## Exam Relevance

- ✅ Comprehend API capabilities
- ✅ Entity types (PERSON, ORGANIZATION, etc.)
- ✅ PII detection for compliance
- ✅ Batch processing for scale
- ✅ Custom classifiers[^custom-classifier] for domain-specific tasks

---

## Glossary

[^comprehend]: **Amazon Comprehend** - A fully managed NLP service that uses machine learning to extract insights, entities, sentiment, and key phrases from text.

[^sentiment-analysis]: **Sentiment Analysis** - An NLP technique that determines the emotional tone of text, classifying it as positive, negative, neutral, or mixed.

[^entity-recognition]: **Entity Recognition** - The process of identifying and categorizing named entities in text such as people, organizations, locations, dates, and quantities.

[^key-phrases]: **Key Phrases** - Important noun phrases extracted from text that represent the main topics or concepts discussed in the document.

[^pii-detection]: **PII Detection** - The identification of Personally Identifiable Information in text, such as names, addresses, phone numbers, SSNs, and credit card numbers.

[^nlp]: **NLP (Natural Language Processing)** - A field of AI focused on enabling computers to understand, interpret, and generate human language.

[^custom-classifier]: **Custom Classifier** - A Comprehend feature that allows training custom text classification models for domain-specific categorization tasks.

---

## Next Lab

Continue to [Lab 12: Textract Docs](../12-textract-docs/LAB.md) →
