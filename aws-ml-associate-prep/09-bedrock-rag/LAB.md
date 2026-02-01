# Lab 09: Amazon Bedrock RAG Application

## Overview
Build a Retrieval Augmented Generation[^rag] (RAG) application using Amazon Bedrock[^bedrock].

**Duration**: 45-60 minutes
**Cost**: ~$1-2 (pay per token)
**Prerequisites**: Bedrock model access enabled

---

## Architecture Overview

```mermaid
flowchart TB
    subgraph RAG["fa:fa-project-diagram RAG Pipeline"]
        subgraph Ingestion["fa:fa-file-import Document Ingestion"]
            Docs[fa:fa-file-alt Documents]
            Chunk[fa:fa-cut Chunking]
            Embed1[fa:fa-vector-square Titan Embeddings]
        end

        subgraph VectorStore["fa:fa-database Vector Store"]
            VS[(fa:fa-th Vector Database<br/>OpenSearch/Pinecone)]
        end

        subgraph Query["fa:fa-search Query Processing"]
            Q[fa:fa-user User Query]
            Embed2[fa:fa-vector-square Query Embedding]
            Search[fa:fa-search-plus Semantic Search]
            Context[fa:fa-file-alt Retrieved Context]
        end

        subgraph Generation["fa:fa-robot Response Generation"]
            Prompt[fa:fa-edit Augmented Prompt]
            LLM[fa:fa-brain Claude/Titan LLM]
            Response[fa:fa-comment-alt Generated Response]
        end
    end

    Docs --> Chunk
    Chunk --> Embed1
    Embed1 --> VS

    Q --> Embed2
    Embed2 --> Search
    VS --> Search
    Search --> Context

    Context --> Prompt
    Q --> Prompt
    Prompt --> LLM
    LLM --> Response

    style Ingestion fill:#e3f2fd
    style VectorStore fill:#fff3e0
    style Query fill:#e8f5e9
    style Generation fill:#fce4ec
```

### Bedrock Model Invocation

```mermaid
sequenceDiagram
    participant App as fa:fa-code Application
    participant BR as fa:fa-cloud Bedrock Runtime
    participant Model as fa:fa-brain Foundation Model

    App->>BR: invoke_model(modelId, body)
    BR->>Model: Forward request
    Model->>Model: Process with LLM
    Model-->>BR: Generated response
    BR-->>App: Response JSON
```

### Knowledge Bases Architecture

```mermaid
flowchart LR
    subgraph Sources["fa:fa-database Data Sources"]
        S3[(fa:fa-database S3 Bucket)]
    end

    subgraph KB["fa:fa-book Knowledge Base"]
        Sync[fa:fa-sync Data Sync]
        Embed[Embedding Model]
        Index[Vector Index]
    end

    subgraph Query["RetrieveAndGenerate"]
        Retrieve[Retrieve]
        Augment[Augment Prompt]
        Generate[Generate Response]
    end

    S3 --> Sync
    Sync --> Embed
    Embed --> Index
    Index --> Retrieve
    Retrieve --> Augment
    Augment --> Generate

    style Sources fill:#e3f2fd
    style KB fill:#fff3e0
    style Query fill:#e8f5e9
```

---

## Lab Objectives

- [ ] Invoke foundation models[^foundation-model] via Bedrock
- [ ] Generate embeddings[^embeddings] with Titan[^titan]
- [ ] Build a simple RAG pipeline
- [ ] Understand Knowledge Bases[^knowledge-base] concepts

---

## Part 1: Basic Model Invocation

### Step 1.1: Enable Model Access

1. Go to **Amazon Bedrock Console**
2. Click **Model access** in the left menu
3. Enable access to:
   - Amazon Titan Text Express
   - Amazon Titan Embeddings
   - Anthropic Claude[^claude] (optional)

### Step 1.2: Invoke Text Model

```python
import boto3
import json

bedrock = boto3.client('bedrock-runtime')

# Invoke Titan Text
def invoke_titan(prompt, max_tokens=512):
    response = bedrock.invoke_model(
        modelId='amazon.titan-text-express-v1',
        contentType='application/json',
        accept='application/json',
        body=json.dumps({
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": max_tokens,
                "temperature": 0.7,
                "topP": 0.9
            }
        })
    )

    result = json.loads(response['body'].read())
    return result['results'][0]['outputText']

# Test
response = invoke_titan("Explain machine learning in 2 sentences.")
print(response)
```

---

## Part 2: Generate Embeddings

```python
# Generate embeddings with Titan Embeddings
def get_embedding(text):
    response = bedrock.invoke_model(
        modelId='amazon.titan-embed-text-v1',
        contentType='application/json',
        accept='application/json',
        body=json.dumps({
            "inputText": text
        })
    )

    result = json.loads(response['body'].read())
    return result['embedding']

# Test
embedding = get_embedding("Machine learning is a subset of AI")
print(f"Embedding dimension: {len(embedding)}")
print(f"First 5 values: {embedding[:5]}")
```

---

## Part 3: Build Simple RAG Pipeline

```python
import numpy as np
from typing import List

# Sample knowledge base (documents)
documents = [
    "Amazon SageMaker is a fully managed machine learning service.",
    "SageMaker provides built-in algorithms like XGBoost and Linear Learner.",
    "Model training in SageMaker uses training jobs that run on EC2 instances.",
    "SageMaker endpoints provide real-time inference for deployed models.",
    "Feature Store is used to store and manage ML features.",
    "SageMaker Pipelines enables ML CI/CD automation."
]

# Generate embeddings for all documents
doc_embeddings = [get_embedding(doc) for doc in documents]

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def retrieve_relevant_docs(query: str, top_k: int = 3) -> List[str]:
    """Retrieve most relevant documents for the query."""
    query_embedding = get_embedding(query)

    # Calculate similarities
    similarities = [
        cosine_similarity(query_embedding, doc_emb)
        for doc_emb in doc_embeddings
    ]

    # Get top-k indices
    top_indices = np.argsort(similarities)[-top_k:][::-1]

    return [documents[i] for i in top_indices]

def rag_query(question: str) -> str:
    """Answer question using RAG."""
    # Retrieve relevant context
    relevant_docs = retrieve_relevant_docs(question, top_k=3)
    context = "\n".join(relevant_docs)

    # Create augmented prompt
    prompt = f"""Use the following context to answer the question.
If the answer is not in the context, say "I don't know."

Context:
{context}

Question: {question}

Answer:"""

    # Generate response
    response = invoke_titan(prompt)
    return response

# Test RAG
question = "What is SageMaker Feature Store used for?"
answer = rag_query(question)
print(f"Question: {question}")
print(f"Answer: {answer}")
```

---

## Part 4: Using Claude Model (Optional)

```python
# Invoke Claude model
def invoke_claude(prompt, max_tokens=512):
    response = bedrock.invoke_model(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        contentType='application/json',
        accept='application/json',
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        })
    )

    result = json.loads(response['body'].read())
    return result['content'][0]['text']

# Test
response = invoke_claude("What are the key components of MLOps?")
print(response)
```

---

## Part 5: Clean Up

```python
# No resources to clean up - Bedrock is pay-per-use
print("No cleanup needed - Bedrock charges per API call only")
```

---

## Lab Challenges

### Challenge 1: Add Conversation History
Modify the Claude invocation to maintain conversation context.

### Challenge 2: Use Knowledge Bases
Create a Bedrock Knowledge Base with S3 documents.

---

## Lab Summary

| Concept | What You Did |
|---------|--------------|
| **Text Generation** | Invoked Titan Text model |
| **Embeddings** | Generated vectors with Titan Embeddings |
| **RAG** | Built retrieval + generation pipeline |
| **Claude** | Invoked Claude model (optional) |

---

## Exam Relevance

- ✅ Foundation models in Bedrock
- ✅ RAG architecture and use cases
- ✅ Embeddings for semantic search[^semantic-search]
- ✅ Knowledge Bases concept

---

## Glossary

[^bedrock]: **Amazon Bedrock** - A fully managed service that provides access to foundation models from Amazon and third-party providers through a single API, enabling generative AI application development.

[^rag]: **RAG (Retrieval Augmented Generation)** - A technique that enhances LLM responses by retrieving relevant information from a knowledge base and including it in the prompt context before generation.

[^foundation-model]: **Foundation Model** - A large AI model pre-trained on vast amounts of data that can be adapted for various downstream tasks without task-specific training.

[^embeddings]: **Embeddings** - Dense vector representations of text that capture semantic meaning, enabling similarity comparisons and semantic search operations.

[^vector-store]: **Vector Store** - A specialized database optimized for storing and querying high-dimensional vector embeddings, supporting efficient similarity search.

[^knowledge-base]: **Knowledge Base** - In Bedrock, a managed service that ingests documents, generates embeddings, and stores them for retrieval during RAG operations.

[^titan]: **Amazon Titan** - Amazon's family of foundation models available through Bedrock, including text generation and embedding models.

[^claude]: **Claude** - Anthropic's family of large language models available through Bedrock, known for helpfulness, harmlessness, and honesty.

[^semantic-search]: **Semantic Search** - A search technique that finds results based on meaning and context rather than exact keyword matching, using embeddings to measure similarity.

---

## Next Lab

Continue to [Lab 10: Rekognition App](../10-rekognition-app/LAB.md) →
