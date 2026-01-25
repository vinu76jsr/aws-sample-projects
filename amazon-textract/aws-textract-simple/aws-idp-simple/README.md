# AWS Intelligent Document Processing (IDP) - Learning Guide

A hands-on tutorial for learning Intelligent Document Processing using AWS services.

---

## What is IDP?

**Intelligent Document Processing (IDP)** combines AI/ML technologies to automate the extraction, classification, and processing of data from documents. It goes beyond simple OCR by understanding document structure, context, and meaning.

### Why IDP Matters

| Traditional Approach | IDP Approach |
|---------------------|--------------|
| Manual data entry | Automated extraction |
| Hours per document | Seconds per document |
| Error-prone | Consistent accuracy |
| Doesn't scale | Handles any volume |
| Fixed templates only | Understands any layout |

### The IDP Pipeline

```
┌─────────────┐    ┌────────────────┐    ┌─────────────┐    ┌────────────┐
│  INGESTION  │───>│ CLASSIFICATION │───>│  EXTRACTION │───>│ VALIDATION │
│  (receive)  │    │ (what type?)   │    │ (pull data) │    │  (verify)  │
└─────────────┘    └────────────────┘    └─────────────┘    └────────────┘
                                                                   │
┌─────────────┐    ┌────────────────┐                              │
│ INTEGRATION │<───│   ENRICHMENT   │<─────────────────────────────┘
│  (export)   │    │  (normalize)   │
└─────────────┘    └────────────────┘
```

---

## AWS Services for IDP

| Service | Purpose | Use Case |
|---------|---------|----------|
| **Amazon Textract** | Document analysis | OCR, tables, forms, queries |
| **Amazon Comprehend** | NLP | Entity extraction, sentiment |
| **Amazon A2I** | Human review | Low-confidence verification |
| **Amazon S3** | Storage | Document repository |
| **AWS Lambda** | Processing | Serverless execution |
| **Amazon DynamoDB** | Database | Store extracted data |

---

## This Project

This project demonstrates 7 core IDP capabilities:

| # | Capability | API | Description |
|---|------------|-----|-------------|
| 1 | **OCR** | `detect_document_text` | Basic text extraction |
| 2 | **Tables** | `analyze_document` (TABLES) | Structured table parsing |
| 3 | **Forms** | `analyze_document` (FORMS) | Key-value pair extraction |
| 4 | **Expenses** | `analyze_expense` | Invoice/receipt processing |
| 5 | **Queries** | `analyze_document` (QUERIES) | Natural language questions |
| 6 | **ID Documents** | `analyze_id` | Passport/license analysis |
| 7 | **Entities** | Comprehend NER | Named entity recognition |

---

## Setup (5 minutes)

### 1. Install dependencies
```bash
pip install boto3
```

### 2. Configure AWS credentials
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Region: us-east-1
```

### 3. Required IAM permissions
Your AWS user needs these policies:
- `AmazonTextractFullAccess`
- `ComprehendFullAccess`

---

## Quick Start

### Basic usage
```bash
# Extract text (OCR)
python idp_processor.py ocr sample_receipt.png

# Extract tables
python idp_processor.py tables sample_receipt.png

# Process invoice/receipt
python idp_processor.py expense sample_receipt.png

# Ask questions about a document
python idp_processor.py query sample_receipt.png --questions "What is the total?" "What is the vendor name?"
```

### Run the original simple script
```bash
python simple_textract.py sample_receipt.png
```

---

## Deep Dive: Each IDP Capability

### 1. OCR Text Extraction

**What it does:** Extracts all text from a document image.

**When to use:**
- Simple text extraction without structure
- Preprocessing for NLP tasks
- Cheapest option ($1.50 per 1000 pages)

**API:** `detect_document_text`

```bash
python idp_processor.py ocr document.pdf
```

**Output structure:**
```json
{
  "lines": [
    {"text": "Invoice #12345", "confidence": 99.5}
  ],
  "words": [...],
  "full_text": "Invoice #12345\n..."
}
```

**Key concept - Blocks:**
Textract returns "Blocks" representing detected elements:
- `PAGE` - The entire page
- `LINE` - A line of text
- `WORD` - Individual words

---

### 2. Table Extraction

**What it does:** Identifies and extracts structured tables.

**When to use:**
- Financial reports with tabular data
- Invoices with line items
- Any grid-like structured data

**API:** `analyze_document` with `FeatureTypes=['TABLES']`

```bash
python idp_processor.py tables report.png
```

**Key concept - Block Relationships:**
```
TABLE block
    └── CHILD relationship
        └── CELL blocks
            └── CHILD relationship
                └── WORD blocks (actual text)
```

**Cost:** $15 per 1000 pages

---

### 3. Form / Key-Value Extraction

**What it does:** Extracts labeled fields from forms.

**When to use:**
- Tax forms, applications, surveys
- Any document with "Label: Value" patterns
- Checkbox detection

**API:** `analyze_document` with `FeatureTypes=['FORMS']`

```bash
python idp_processor.py forms application.jpg
```

**Example extraction:**
```
Form Field: "Name"        -> Value: "John Smith"
Form Field: "Date"        -> Value: "01/15/2024"
Form Field: "Agree"       -> Value: "SELECTED"
```

**Key concept - KEY_VALUE_SET:**
- Blocks with `EntityTypes: ['KEY']` are labels
- Blocks with `EntityTypes: ['VALUE']` are values
- Keys have `VALUE` relationships to their values

**Cost:** $50 per 1000 pages (premium feature)

---

### 4. Expense/Invoice Analysis

**What it does:** Specialized extraction for invoices and receipts.

**When to use:**
- Accounts payable automation
- Receipt processing
- Financial document processing

**API:** `analyze_expense`

```bash
python idp_processor.py expense receipt.png
```

**Automatically extracts:**

| Summary Fields | Line Item Fields |
|---------------|------------------|
| VENDOR_NAME | ITEM |
| VENDOR_ADDRESS | QUANTITY |
| INVOICE_RECEIPT_DATE | UNIT_PRICE |
| INVOICE_RECEIPT_ID | PRICE |
| TOTAL, SUBTOTAL, TAX | EXPENSE_ROW |

**Why use this over generic extraction?**
- Pre-trained for financial documents
- Normalized field names
- Handles various invoice formats

**Cost:** $10 per 1000 pages

---

### 5. Query-Based Extraction

**What it does:** Answer natural language questions about documents.

**When to use:**
- Need specific information, not full extraction
- Document structure varies
- Rapid development without complex parsing

**API:** `analyze_document` with `FeatureTypes=['QUERIES']`

```bash
python idp_processor.py query invoice.pdf \
  --questions "What is the total amount?" \
              "What is the customer name?" \
              "What is the due date?"
```

**Best practices:**
- Be specific: "What is the invoice total?" > "What is the amount?"
- Max 15 queries per API call
- Match how data appears in documents

**Cost:** $15 per 1000 pages (charged per page, not per query)

---

### 6. ID Document Analysis

**What it does:** Extracts data from identity documents.

**When to use:**
- KYC (Know Your Customer) processes
- Customer onboarding
- Age/identity verification

**API:** `analyze_id`

```bash
python idp_processor.py id drivers_license.jpg
```

**Supported documents:**
- US Passports
- US Driver's Licenses (all states)
- US State IDs

**Extracted fields:**
- FIRST_NAME, LAST_NAME, MIDDLE_NAME
- DATE_OF_BIRTH, DATE_OF_EXPIRY
- DOCUMENT_NUMBER, ADDRESS
- ID_TYPE, CLASS, ENDORSEMENTS

**Security note:** ID documents contain PII. Ensure proper encryption and compliance (GDPR, CCPA).

**Cost:** $15 per 1000 pages

---

### 7. Entity Extraction (NLP)

**What it does:** Identifies named entities using NLP.

**When to use:**
- Contract analysis
- Resume parsing
- News/content analysis

**Services:** Textract (OCR) + Comprehend (NLP)

```bash
python idp_processor.py entities contract.pdf
```

**Entity types detected:**
| Type | Examples |
|------|----------|
| PERSON | "John Smith", "Jane Doe" |
| ORGANIZATION | "Amazon", "Acme Corp" |
| LOCATION | "New York", "123 Main St" |
| DATE | "January 15, 2024" |
| QUANTITY | "100 units", "$500" |
| COMMERCIAL_ITEM | "iPhone", "Model X" |

**Key concept - Two-stage pipeline:**
1. Textract extracts text (OCR)
2. Comprehend analyzes text (NLP)

This pattern is common in IDP - combining services for capabilities no single service provides.

---

## Full Pipeline

Run all extraction methods on a single document:

```bash
python idp_processor.py full document.pdf \
  --questions "What is the total?" \
  --include-id
```

**Production IDP pipelines typically include:**

1. **Ingestion** - Accept from email, upload, scan
2. **Preprocessing** - Deskew, denoise, convert
3. **Classification** - Determine document type
4. **Extraction** - Run appropriate APIs
5. **Post-processing** - Normalize, validate
6. **Human Review** - Amazon A2I for low confidence
7. **Integration** - Push to downstream systems

---

## Cost Reference

| API | Cost per 1000 pages |
|-----|---------------------|
| detect_document_text (OCR) | $1.50 |
| analyze_expense | $10.00 |
| analyze_document (Tables) | $15.00 |
| analyze_document (Queries) | $15.00 |
| analyze_id | $15.00 |
| analyze_document (Forms) | $50.00 |
| Comprehend (entities) | ~$0.0001/character |

**Free tier:** First 1000 pages free (first 3 months)

---

## Output Files

Each command saves a JSON file:

| Command | Output File |
|---------|-------------|
| ocr | `{filename}_ocr.json` |
| tables | `{filename}_tables.json` |
| forms | `{filename}_forms.json` |
| expense | `{filename}_expense.json` |
| query | `{filename}_queries.json` |
| id | `{filename}_id.json` |
| entities | `{filename}_entities.json` |
| full | `{filename}_full_idp.json` |

---

## Troubleshooting

**Error: "Unable to locate credentials"**
```bash
aws configure
```

**Error: "InvalidParameterException"**
- Check file format (JPG, PNG, PDF, TIFF)
- Check file size (< 10MB for sync calls)

**Error: "AccessDeniedException"**
- Add required IAM policies to your user

**Error: "UnsupportedDocumentException"**
- Document may be corrupted or unsupported format
- Try converting to PNG

---

## Learning Resources

- [AWS Textract Documentation](https://docs.aws.amazon.com/textract/)
- [AWS Comprehend Documentation](https://docs.aws.amazon.com/comprehend/)
- [IDP on AWS](https://aws.amazon.com/intelligent-document-processing/)
- [Textract Best Practices](https://docs.aws.amazon.com/textract/latest/dg/bestpractices.html)

---

## Project Structure

```
aws-idp-simple/
├── idp_processor.py      # Full IDP toolkit (7 capabilities)
├── simple_textract.py    # Simple expense extraction
├── sample_receipt.png    # Sample document
└── README.md             # This guide
```

---

## Next Steps

After mastering this tutorial:

1. **Add S3 integration** - Process documents from S3
2. **Build async processing** - Handle large documents
3. **Add human review** - Integrate Amazon A2I
4. **Create a web API** - API Gateway + Lambda
5. **Store results** - DynamoDB or RDS
6. **Add classification** - Route by document type

---

## Key Takeaways

1. **IDP != OCR** - IDP understands structure and meaning, not just text
2. **Choose the right API** - Each Textract API is optimized for specific use cases
3. **Combine services** - Textract + Comprehend = more powerful extraction
4. **Confidence matters** - Use confidence scores to trigger human review
5. **Cost varies** - Simple OCR is cheap, Forms extraction is expensive