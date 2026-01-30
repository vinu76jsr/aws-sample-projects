# 09 - Amazon Bedrock RAG Application

> **Exam Weight**: Growing focus on Generative AI
> **Priority**: MEDIUM-HIGH - Newer but important topic

## What is Amazon Bedrock?

Amazon Bedrock is a fully managed service that offers a choice of high-performing foundation models (FMs) from leading AI companies through a single API. It's AWS's primary generative AI service.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        AMAZON BEDROCK ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    FOUNDATION MODELS                             │   │
│  ├─────────────┬─────────────┬─────────────┬─────────────┬─────────┤   │
│  │   Amazon    │  Anthropic  │    Meta     │   Cohere    │ Mistral │   │
│  │   Titan     │   Claude    │    Llama    │   Command   │         │   │
│  └─────────────┴─────────────┴─────────────┴─────────────┴─────────┘   │
│                                    │                                    │
│                    ┌───────────────┼───────────────┐                   │
│                    ▼               ▼               ▼                   │
│             ┌───────────┐   ┌───────────┐   ┌───────────┐             │
│             │   Text    │   │   Image   │   │ Embedding │             │
│             │Generation │   │Generation │   │           │             │
│             └───────────┘   └───────────┘   └───────────┘             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Foundation Models (KNOW FOR EXAM)

| Provider | Model | Use Case | Exam Focus |
|----------|-------|----------|------------|
| **Amazon** | Titan Text | General text generation | Cost-effective |
| **Amazon** | Titan Embeddings | Vector embeddings | RAG applications |
| **Anthropic** | Claude | Complex reasoning, coding | High quality |
| **Meta** | Llama 2/3 | Open-source alternative | Customizable |
| **Cohere** | Command | Enterprise text | Multilingual |
| **Stability AI** | Stable Diffusion | Image generation | Creative |

---

## Key Bedrock Features

### 1. Model Inference

```python
import boto3
import json

bedrock = boto3.client('bedrock-runtime')

# Invoke Claude model
response = bedrock.invoke_model(
    modelId='anthropic.claude-3-sonnet-20240229-v1:0',
    contentType='application/json',
    accept='application/json',
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [
            {"role": "user", "content": "Explain machine learning briefly."}
        ]
    })
)

result = json.loads(response['body'].read())
print(result['content'][0]['text'])
```

### 2. Embeddings (for RAG)

```python
# Generate embeddings with Titan
response = bedrock.invoke_model(
    modelId='amazon.titan-embed-text-v1',
    contentType='application/json',
    accept='application/json',
    body=json.dumps({
        "inputText": "This is text to embed"
    })
)

result = json.loads(response['body'].read())
embedding = result['embedding']  # Vector of floats
```

### 3. Knowledge Bases (Managed RAG)

```
┌─────────────────────────────────────────────────────────────┐
│                    KNOWLEDGE BASE RAG                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────┐   ┌─────────────┐   ┌─────────────────────┐   │
│  │   S3    │──▶│  Embedding  │──▶│  Vector Database    │   │
│  │  Docs   │   │    Model    │   │  (OpenSearch/etc)   │   │
│  └─────────┘   └─────────────┘   └─────────────────────┘   │
│                                            │                │
│                                            ▼                │
│  ┌─────────┐   ┌─────────────┐   ┌─────────────────────┐   │
│  │  Query  │──▶│  Retrieve   │──▶│    FM + Context     │   │
│  │         │   │  Relevant   │   │     Generation      │   │
│  └─────────┘   └─────────────┘   └─────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4. Fine-Tuning (Customization)

| Method | Description | Use Case |
|--------|-------------|----------|
| **Continued Pre-training** | Train on domain data | Domain adaptation |
| **Fine-tuning** | Train on task examples | Specific tasks |
| **PEFT/LoRA** | Parameter-efficient tuning | Limited compute |

---

## RAG (Retrieval Augmented Generation)

### Why RAG?

- **Problem**: LLMs have knowledge cutoff, hallucinate
- **Solution**: Retrieve relevant context, augment prompts
- **Result**: Accurate, up-to-date, grounded responses

### RAG Architecture

```python
# Simplified RAG flow

# 1. Index documents (offline)
def index_documents(documents):
    chunks = chunk_documents(documents)
    embeddings = []
    for chunk in chunks:
        embedding = get_embedding(chunk)
        embeddings.append({'text': chunk, 'vector': embedding})
    store_in_vector_db(embeddings)

# 2. Query (online)
def rag_query(question):
    # Get question embedding
    question_embedding = get_embedding(question)

    # Retrieve relevant chunks
    relevant_chunks = vector_db.similarity_search(
        question_embedding,
        top_k=5
    )

    # Build prompt with context
    context = "\n".join([chunk['text'] for chunk in relevant_chunks])
    prompt = f"""Use the following context to answer the question.

Context:
{context}

Question: {question}

Answer:"""

    # Generate response
    response = invoke_llm(prompt)
    return response
```

---

## Bedrock Knowledge Bases (Managed RAG)

```python
import boto3

bedrock_agent = boto3.client('bedrock-agent')

# Create knowledge base
response = bedrock_agent.create_knowledge_base(
    name='my-knowledge-base',
    roleArn=role_arn,
    knowledgeBaseConfiguration={
        'type': 'VECTOR',
        'vectorKnowledgeBaseConfiguration': {
            'embeddingModelArn': 'arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v1'
        }
    },
    storageConfiguration={
        'type': 'OPENSEARCH_SERVERLESS',
        'opensearchServerlessConfiguration': {
            'collectionArn': opensearch_collection_arn,
            'vectorIndexName': 'bedrock-kb-index',
            'fieldMapping': {
                'vectorField': 'embedding',
                'textField': 'text',
                'metadataField': 'metadata'
            }
        }
    }
)

# Create data source
bedrock_agent.create_data_source(
    knowledgeBaseId=knowledge_base_id,
    name='s3-source',
    dataSourceConfiguration={
        'type': 'S3',
        's3Configuration': {
            'bucketArn': f'arn:aws:s3:::{bucket_name}'
        }
    }
)

# Sync data source (ingest documents)
bedrock_agent.start_ingestion_job(
    knowledgeBaseId=knowledge_base_id,
    dataSourceId=data_source_id
)
```

---

## Bedrock Agents

Agents combine LLMs with actions (tools).

```
┌─────────────────────────────────────────────────────────────┐
│                      BEDROCK AGENT                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  User Query ──▶ Agent ──┬──▶ Knowledge Base (RAG)          │
│                         │                                   │
│                         ├──▶ Lambda (Actions)               │
│                         │                                   │
│                         └──▶ External APIs                  │
│                                                             │
│  Agent orchestrates:                                        │
│  1. Understand user intent                                  │
│  2. Plan actions                                            │
│  3. Execute actions                                         │
│  4. Formulate response                                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Guardrails

Control model inputs and outputs.

```python
# Create guardrail
response = bedrock.create_guardrail(
    name='content-filter',
    description='Filter harmful content',
    blockedInputMessaging='Sorry, I cannot process this request.',
    blockedOutputsMessaging='Sorry, I cannot provide this response.',
    contentPolicyConfig={
        'filtersConfig': [
            {'type': 'SEXUAL', 'inputStrength': 'HIGH', 'outputStrength': 'HIGH'},
            {'type': 'VIOLENCE', 'inputStrength': 'HIGH', 'outputStrength': 'HIGH'},
            {'type': 'HATE', 'inputStrength': 'HIGH', 'outputStrength': 'HIGH'},
        ]
    },
    wordPolicyConfig={
        'wordsConfig': [
            {'text': 'competitor-name'}
        ]
    }
)
```

---

## Exam Question Patterns

### Pattern 1: RAG Application
> "Need to answer questions using company documents..."

**Answer**: Bedrock Knowledge Bases (managed RAG)

### Pattern 2: Embeddings
> "Generate vector representations for semantic search..."

**Answer**: Titan Embeddings model

### Pattern 3: Model Selection
> "Need high-quality reasoning with safety..."

**Answer**: Anthropic Claude

### Pattern 4: Content Filtering
> "Ensure model doesn't generate harmful content..."

**Answer**: Bedrock Guardrails

### Pattern 5: Custom Domain
> "Adapt model to company-specific terminology..."

**Answer**: Fine-tuning or continued pre-training

### Pattern 6: Cost Optimization
> "Cost-effective text generation..."

**Answer**: Amazon Titan Text (AWS native, competitive pricing)

---

## Bedrock vs SageMaker

| Feature | Bedrock | SageMaker |
|---------|---------|-----------|
| **Focus** | Foundation models | Custom ML |
| **Models** | Pre-trained FMs | Train your own |
| **RAG** | Built-in Knowledge Bases | Build yourself |
| **Customization** | Fine-tuning | Full control |
| **Complexity** | Simple API | More complex |
| **Use Case** | GenAI applications | Full ML lifecycle |

---

## Checklist

- [ ] Understand foundation models available in Bedrock
- [ ] Know RAG architecture and when to use it
- [ ] Understand Knowledge Bases for managed RAG
- [ ] Know Bedrock Agents for action-oriented tasks
- [ ] Understand Guardrails for content filtering
- [ ] Know when to use Bedrock vs SageMaker

---

## Next Steps

After completing this module, proceed to:
- [10 - Rekognition App](../10-rekognition-app/) - Computer vision AI service
