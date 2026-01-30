# 12 - Amazon Textract

> **Exam Weight**: Part of AI Services knowledge
> **Priority**: MEDIUM - Document processing AI

## What is Amazon Textract?

Amazon Textract is a document analysis service that automatically extracts text, handwriting, and structured data (tables, forms) from documents. It goes beyond simple OCR.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      AMAZON TEXTRACT CAPABILITIES                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  DETECT TEXT              ANALYZE DOCUMENT          ANALYZE EXPENSE     │
│  ───────────              ────────────────          ───────────────     │
│  • Lines of text          • Forms (key-value)      • Invoices           │
│  • Words                  • Tables                  • Receipts           │
│  • Confidence scores      • Queries                 • Line items         │
│                           • Signatures              • Vendor info        │
│                                                                         │
│  ANALYZE ID               ANALYZE LENDING                               │
│  ──────────               ───────────────                               │
│  • Driver's license       • Mortgage documents                          │
│  • Passport               • Loan applications                           │
│  • ID cards               • Financial statements                        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Key APIs (KNOW FOR EXAM)

| API | Purpose | Use Case |
|-----|---------|----------|
| `detect_document_text` | Basic OCR | Extract all text |
| `analyze_document` | Structured extraction | Forms, tables, queries |
| `analyze_expense` | Receipt/invoice processing | Expense reports |
| `analyze_id` | ID document processing | Identity verification |
| `start_document_analysis` | Async for multi-page | Large PDFs |

---

## Basic Text Detection

```python
import boto3

textract = boto3.client('textract')

# From S3
response = textract.detect_document_text(
    Document={
        'S3Object': {
            'Bucket': 'my-bucket',
            'Name': 'document.pdf'
        }
    }
)

for block in response['Blocks']:
    if block['BlockType'] == 'LINE':
        print(block['Text'])
```

---

## Form Extraction (Key-Value Pairs)

```python
response = textract.analyze_document(
    Document={
        'S3Object': {'Bucket': 'bucket', 'Name': 'form.pdf'}
    },
    FeatureTypes=['FORMS']  # Extract key-value pairs
)

# Parse form fields
key_map = {}
value_map = {}
block_map = {}

for block in response['Blocks']:
    block_id = block['Id']
    block_map[block_id] = block

    if block['BlockType'] == 'KEY_VALUE_SET':
        if 'KEY' in block['EntityTypes']:
            key_map[block_id] = block
        else:
            value_map[block_id] = block

# Extract key-value pairs
for key_id, key_block in key_map.items():
    key_text = get_text(key_block, block_map)
    value_block = find_value_block(key_block, value_map)
    value_text = get_text(value_block, block_map)
    print(f"{key_text}: {value_text}")

# Output example:
# Name: John Smith
# Date of Birth: 01/15/1990
# Account Number: 123456789
```

---

## Table Extraction

```python
response = textract.analyze_document(
    Document={'S3Object': {'Bucket': 'bucket', 'Name': 'table.pdf'}},
    FeatureTypes=['TABLES']  # Extract tables
)

# Tables are represented as cells with row/column indices
for block in response['Blocks']:
    if block['BlockType'] == 'TABLE':
        print("Found table")

    if block['BlockType'] == 'CELL':
        row = block['RowIndex']
        col = block['ColumnIndex']
        text = get_text(block, block_map)
        print(f"Row {row}, Col {col}: {text}")
```

---

## Queries (Specific Questions)

Ask specific questions about the document.

```python
response = textract.analyze_document(
    Document={'S3Object': {'Bucket': 'bucket', 'Name': 'invoice.pdf'}},
    FeatureTypes=['QUERIES'],
    QueriesConfig={
        'Queries': [
            {'Text': 'What is the invoice number?'},
            {'Text': 'What is the total amount?'},
            {'Text': 'What is the due date?'}
        ]
    }
)

for block in response['Blocks']:
    if block['BlockType'] == 'QUERY_RESULT':
        print(f"Answer: {block['Text']}, Confidence: {block['Confidence']:.2f}")
```

### Exam Tip: Queries
- Best for extracting specific information
- Works even if location varies between documents
- Combine with FORMS/TABLES for comprehensive extraction

---

## Expense Analysis

Specialized for invoices and receipts.

```python
response = textract.analyze_expense(
    Document={'S3Object': {'Bucket': 'bucket', 'Name': 'receipt.jpg'}}
)

for doc in response['ExpenseDocuments']:
    # Summary fields
    for field in doc['SummaryFields']:
        print(f"{field['Type']['Text']}: {field['ValueDetection']['Text']}")
        # VENDOR_NAME: Amazon
        # TOTAL: $125.50
        # INVOICE_RECEIPT_DATE: 2024-01-15

    # Line items
    for group in doc['LineItemGroups']:
        for item in group['LineItems']:
            for field in item['LineItemExpenseFields']:
                print(f"  {field['Type']['Text']}: {field['ValueDetection']['Text']}")
```

### Expense Fields

| Field Type | Description |
|------------|-------------|
| VENDOR_NAME | Merchant name |
| TOTAL | Total amount |
| SUBTOTAL | Pre-tax amount |
| TAX | Tax amount |
| INVOICE_RECEIPT_DATE | Document date |
| INVOICE_RECEIPT_ID | Invoice/receipt number |
| ITEM | Line item description |
| QUANTITY | Item quantity |
| UNIT_PRICE | Per-unit price |

---

## ID Document Analysis

```python
response = textract.analyze_id(
    DocumentPages=[
        {'S3Object': {'Bucket': 'bucket', 'Name': 'drivers-license.jpg'}}
    ]
)

for doc in response['IdentityDocuments']:
    for field in doc['IdentityDocumentFields']:
        print(f"{field['Type']['Text']}: {field['ValueDetection']['Text']}")
        # FIRST_NAME: John
        # LAST_NAME: Smith
        # DATE_OF_BIRTH: 01/15/1990
        # DOCUMENT_NUMBER: D1234567
        # EXPIRATION_DATE: 01/15/2028
```

---

## Async Processing (Multi-page PDFs)

For large documents, use async APIs.

```python
# Start async job
response = textract.start_document_analysis(
    DocumentLocation={
        'S3Object': {'Bucket': 'bucket', 'Name': 'large-document.pdf'}
    },
    FeatureTypes=['FORMS', 'TABLES'],
    NotificationChannel={
        'SNSTopicArn': 'arn:aws:sns:...',
        'RoleArn': 'arn:aws:iam:...'
    }
)

job_id = response['JobId']

# Get results (after notification or polling)
response = textract.get_document_analysis(JobId=job_id)

# Handle pagination
next_token = response.get('NextToken')
while next_token:
    response = textract.get_document_analysis(JobId=job_id, NextToken=next_token)
    # Process blocks...
    next_token = response.get('NextToken')
```

---

## Textract vs Rekognition (OCR)

| Feature | Textract | Rekognition |
|---------|----------|-------------|
| **Focus** | Document analysis | Image/video analysis |
| **OCR** | Advanced (forms, tables) | Basic (scene text) |
| **Structured Data** | Yes (key-value, tables) | No |
| **Queries** | Yes | No |
| **Use Case** | Documents, forms | Photos, signs, video |

### Exam Tip: When to Choose
- **Document with forms/tables** → Textract
- **Photo with text (sign, license plate)** → Rekognition DetectText
- **Invoice processing** → Textract AnalyzeExpense

---

## Exam Question Patterns

### Pattern 1: Form Processing
> "Extract key-value pairs from application forms..."

**Answer**: Textract AnalyzeDocument with FORMS

### Pattern 2: Table Extraction
> "Extract tabular data from financial reports..."

**Answer**: Textract AnalyzeDocument with TABLES

### Pattern 3: Invoice Processing
> "Automate expense report processing..."

**Answer**: Textract AnalyzeExpense

### Pattern 4: Specific Information
> "Extract only invoice number and total amount..."

**Answer**: Textract Queries feature

### Pattern 5: Identity Verification
> "Extract information from driver's licenses..."

**Answer**: Textract AnalyzeID

### Pattern 6: Large Documents
> "Process 100-page PDF..."

**Answer**: Textract start_document_analysis (async)

---

## Checklist

- [ ] Know Textract APIs and their purposes
- [ ] Understand FORMS vs TABLES vs QUERIES features
- [ ] Know AnalyzeExpense for invoices/receipts
- [ ] Know AnalyzeID for identity documents
- [ ] Understand async processing for large documents
- [ ] Know when to use Textract vs Rekognition

---

## Next Steps

After completing this module, proceed to:
- [13 - Lambda Inference](../13-lambda-inference/) - Serverless ML inference
