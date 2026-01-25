#!/usr/bin/env python3
"""
=============================================================================
AWS INTELLIGENT DOCUMENT PROCESSING (IDP) - LEARNING GUIDE
=============================================================================

WHAT IS IDP (Intelligent Document Processing)?
----------------------------------------------
IDP is a combination of AI/ML technologies that automate the extraction,
classification, and processing of data from documents. It goes beyond simple
OCR by understanding document structure, context, and meaning.

THE IDP PIPELINE (typical stages):
----------------------------------
1. INGESTION     - Receive documents (images, PDFs, scans)
2. CLASSIFICATION - Determine document type (invoice, contract, ID, etc.)
3. EXTRACTION    - Pull out relevant data fields
4. VALIDATION    - Verify extracted data for accuracy
5. ENRICHMENT    - Add context, normalize data, link to other systems
6. INTEGRATION   - Send to downstream systems (databases, workflows)

AWS SERVICES FOR IDP:
---------------------
- Amazon Textract  : OCR + intelligent document understanding
- Amazon Comprehend: NLP for entity extraction, sentiment, key phrases
- Amazon A2I       : Human review workflows for low-confidence results
- Amazon S3        : Document storage
- AWS Lambda       : Serverless processing
- Amazon DynamoDB  : Storing extracted data

THIS FILE DEMONSTRATES:
-----------------------
1. OCR Text Extraction      - Basic text recognition (detect_document_text)
2. Table Extraction         - Structured table parsing (analyze_document/TABLES)
3. Form Extraction          - Key-value pairs from forms (analyze_document/FORMS)
4. Expense Analysis         - Invoice/receipt processing (analyze_expense)
5. Query-based Extraction   - Natural language queries (analyze_document/QUERIES)
6. ID Document Analysis     - Passports, licenses (analyze_id)
7. Entity Extraction        - NLP with Amazon Comprehend

Usage:
    python idp_processor.py <command> <file_path> [options]

Commands:
    ocr       - Extract all text from document
    tables    - Extract tables from document
    forms     - Extract key-value pairs from forms
    expense   - Analyze invoices/receipts
    query     - Ask questions about document (requires --questions)
    id        - Analyze ID documents (passport, license)
    entities  - Extract named entities from document text
    full      - Run complete IDP pipeline
"""

import boto3
import json
import sys
import argparse
from pathlib import Path
from datetime import datetime


class IDPProcessor:
    """
    Comprehensive Intelligent Document Processing using AWS services.

    LEARNING NOTE: This class encapsulates all IDP operations. In production,
    you might split these into separate microservices or Lambda functions
    for better scalability and separation of concerns.
    """

    def __init__(self, region='us-east-1'):
        """
        Initialize AWS service clients.

        LEARNING NOTE - AWS Clients:
        - Each AWS service has its own client (boto3.client)
        - Clients are thread-safe and can be reused
        - Region matters! Some features may not be available in all regions
        - Textract is available in: us-east-1, us-east-2, us-west-2, eu-west-1, etc.
        """
        self.region = region

        # Textract: The core service for document analysis
        # Handles OCR, tables, forms, queries, expenses, and ID documents
        self.textract = boto3.client('textract', region_name=region)

        # Comprehend: NLP service for entity extraction, sentiment, etc.
        # Used to extract meaning from the text that Textract extracts
        self.comprehend = boto3.client('comprehend', region_name=region)

    def _read_document(self, file_path):
        """
        Read document bytes from file.

        LEARNING NOTE - Document Input Options:
        1. Bytes (used here): Good for small documents (<10MB), synchronous
        2. S3 Reference: Required for large documents or async processing

        Supported formats: PNG, JPEG, TIFF, PDF (single/multi-page)
        """
        with open(file_path, 'rb') as f:
            return f.read()

    def _save_output(self, data, file_path, suffix):
        """Save extracted data to JSON file for downstream processing."""
        output_file = Path(file_path).stem + f'_{suffix}.json'
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return output_file

    # =========================================================================
    # 1. OCR TEXT EXTRACTION
    # =========================================================================
    def extract_text(self, file_path):
        """
        Extract all text from document using basic OCR.

        API: detect_document_text

        LEARNING NOTE - When to use this:
        - Simple text extraction without structure
        - When you just need the raw text content
        - Preprocessing step for NLP tasks
        - Cheapest Textract option ($1.50 per 1000 pages)

        LEARNING NOTE - Response Structure:
        The API returns "Blocks" - each block represents a detected element:
        - PAGE: The entire page
        - LINE: A line of text (what humans see as a line)
        - WORD: Individual words

        Blocks have:
        - Text: The actual content
        - Confidence: How sure Textract is (0-100%)
        - Geometry: Position on page (BoundingBox, Polygon)

        EXAMPLE RESPONSE STRUCTURE:
        {
            "Blocks": [
                {"BlockType": "PAGE", "Id": "abc123", ...},
                {"BlockType": "LINE", "Text": "Invoice #12345", "Confidence": 99.5, ...},
                {"BlockType": "WORD", "Text": "Invoice", "Confidence": 99.8, ...},
                {"BlockType": "WORD", "Text": "#12345", "Confidence": 99.2, ...}
            ]
        }
        """
        print(f"\n{'='*70}")
        print("OCR TEXT EXTRACTION")
        print(f"{'='*70}")

        image_bytes = self._read_document(file_path)

        # Call the simplest Textract API - just detect text
        response = self.textract.detect_document_text(
            Document={'Bytes': image_bytes}
        )

        # Process the blocks by type
        # LEARNING NOTE: We separate LINEs and WORDs because:
        # - LINEs preserve reading order and are good for display
        # - WORDs are useful for word-level analysis or search
        lines = []
        words = []

        for block in response.get('Blocks', []):
            if block['BlockType'] == 'LINE':
                lines.append({
                    'text': block['Text'],
                    'confidence': block['Confidence'],
                    # BoundingBox: relative coordinates (0-1) for element position
                    # Useful for understanding document layout
                    'bbox': block['Geometry']['BoundingBox']
                })
            elif block['BlockType'] == 'WORD':
                words.append({
                    'text': block['Text'],
                    'confidence': block['Confidence']
                })

        # Display results
        print(f"\nDetected {len(lines)} lines, {len(words)} words\n")
        print("EXTRACTED TEXT:")
        print("-" * 70)
        for line in lines:
            print(f"  {line['text']} (Confidence: {line['confidence']:.1f}%)")

        result = {
            'type': 'ocr_extraction',
            'file': str(file_path),
            'lines': lines,
            'words': words,
            'full_text': '\n'.join([l['text'] for l in lines]),
            'statistics': {
                'total_lines': len(lines),
                'total_words': len(words),
                'avg_confidence': sum(l['confidence'] for l in lines) / len(lines) if lines else 0
            }
        }

        output_file = self._save_output(result, file_path, 'ocr')
        print(f"\nSaved to: {output_file}")

        return result

    # =========================================================================
    # 2. TABLE EXTRACTION
    # =========================================================================
    def extract_tables(self, file_path):
        """
        Extract tables from document.

        API: analyze_document with FeatureTypes=['TABLES']

        LEARNING NOTE - When to use this:
        - Documents with tabular data (invoices, reports, forms)
        - Financial statements, schedules, inventories
        - Any structured grid-like data

        LEARNING NOTE - How Table Detection Works:
        Textract identifies tables and their cells, understanding:
        - Row and column structure
        - Merged cells (spanning multiple rows/columns)
        - Header rows vs data rows
        - Cell content (text within each cell)

        LEARNING NOTE - Block Relationships:
        Tables use a hierarchical structure connected by "Relationships":
        - TABLE block has CHILD relationship to CELL blocks
        - CELL blocks have CHILD relationship to WORD blocks

        This is why we build a "block_map" - to efficiently navigate these
        relationships and reconstruct the table structure.

        COST: $15 per 1000 pages (more expensive than basic OCR)
        """
        print(f"\n{'='*70}")
        print("TABLE EXTRACTION")
        print(f"{'='*70}")

        image_bytes = self._read_document(file_path)

        # analyze_document is more powerful than detect_document_text
        # FeatureTypes tells Textract what to look for
        response = self.textract.analyze_document(
            Document={'Bytes': image_bytes},
            FeatureTypes=['TABLES']  # Can also include 'FORMS', 'SIGNATURES'
        )

        # LEARNING NOTE - Block Map Pattern:
        # This is a common pattern when working with Textract.
        # Blocks reference each other by ID, so we create a lookup dictionary
        # to quickly find related blocks.
        blocks = response.get('Blocks', [])
        block_map = {block['Id']: block for block in blocks}

        # Find all TABLE blocks and process them
        tables = []
        for block in blocks:
            if block['BlockType'] == 'TABLE':
                table = self._process_table(block, block_map)
                tables.append(table)

        # Display results
        print(f"\nDetected {len(tables)} table(s)\n")

        for i, table in enumerate(tables, 1):
            print(f"TABLE {i}:")
            print("-" * 70)
            for row in table['rows']:
                row_text = " | ".join([cell['text'] for cell in row])
                print(f"  {row_text}")
            print()

        result = {
            'type': 'table_extraction',
            'file': str(file_path),
            'tables': tables,
            'statistics': {
                'total_tables': len(tables)
            }
        }

        output_file = self._save_output(result, file_path, 'tables')
        print(f"Saved to: {output_file}")

        return result

    def _process_table(self, table_block, block_map):
        """
        Process a TABLE block into structured row/column data.

        LEARNING NOTE - Cell Properties:
        Each CELL block contains:
        - RowIndex: 1-based row number
        - ColumnIndex: 1-based column number
        - RowSpan: How many rows the cell spans (for merged cells)
        - ColumnSpan: How many columns the cell spans
        - Relationships: Links to WORD blocks containing the text
        """
        rows = {}

        # Navigate TABLE -> CELL relationships
        for relationship in table_block.get('Relationships', []):
            if relationship['Type'] == 'CHILD':
                for cell_id in relationship['Ids']:
                    cell = block_map.get(cell_id)
                    if cell and cell['BlockType'] == 'CELL':
                        row_idx = cell['RowIndex']
                        col_idx = cell['ColumnIndex']

                        # Get text by following CELL -> WORD relationships
                        cell_text = self._get_text_from_block(cell, block_map)

                        if row_idx not in rows:
                            rows[row_idx] = {}
                        rows[row_idx][col_idx] = {
                            'text': cell_text,
                            'row': row_idx,
                            'col': col_idx,
                            'confidence': cell.get('Confidence', 0)
                        }

        # Convert dictionary to sorted list format
        table_rows = []
        for row_idx in sorted(rows.keys()):
            row = []
            for col_idx in sorted(rows[row_idx].keys()):
                row.append(rows[row_idx][col_idx])
            table_rows.append(row)

        return {'rows': table_rows, 'row_count': len(table_rows)}

    def _get_text_from_block(self, block, block_map):
        """
        Extract text from a block by following CHILD relationships.

        LEARNING NOTE: This recursive pattern is essential for Textract.
        Parent blocks (TABLE, CELL, KEY_VALUE_SET) don't contain text directly.
        You must follow relationships to find the WORD blocks that have the text.
        """
        text_parts = []

        for relationship in block.get('Relationships', []):
            if relationship['Type'] == 'CHILD':
                for child_id in relationship['Ids']:
                    child = block_map.get(child_id)
                    if child and 'Text' in child:
                        text_parts.append(child['Text'])

        return ' '.join(text_parts) if text_parts else ''

    # =========================================================================
    # 3. FORM / KEY-VALUE EXTRACTION
    # =========================================================================
    def extract_forms(self, file_path):
        """
        Extract key-value pairs from forms.

        API: analyze_document with FeatureTypes=['FORMS']

        LEARNING NOTE - What are Key-Value Pairs?
        Forms contain labeled fields like:
        - "Name: John Smith" -> Key="Name", Value="John Smith"
        - "Date: 01/15/2024" -> Key="Date", Value="01/15/2024"
        - "[ ] Agree to terms" -> Key="Agree to terms", Value="SELECTED/NOT_SELECTED"

        LEARNING NOTE - How Form Detection Works:
        Textract uses ML to identify:
        - Labels (keys) - typically left of or above the value
        - Values - the filled-in data
        - Checkboxes and their selection state

        The KEY_VALUE_SET block type has an EntityTypes field:
        - ['KEY'] - This block is a label/question
        - ['VALUE'] - This block is an answer/value

        Keys have VALUE relationships pointing to their corresponding values.

        USE CASES:
        - Tax forms, medical forms, applications
        - Any document with labeled fields
        - Surveys and questionnaires

        COST: $50 per 1000 pages (premium feature)
        """
        print(f"\n{'='*70}")
        print("FORM / KEY-VALUE EXTRACTION")
        print(f"{'='*70}")

        image_bytes = self._read_document(file_path)

        response = self.textract.analyze_document(
            Document={'Bytes': image_bytes},
            FeatureTypes=['FORMS']
        )

        blocks = response.get('Blocks', [])
        block_map = {block['Id']: block for block in blocks}

        # Find all KEY blocks and their associated VALUEs
        key_value_pairs = []

        for block in blocks:
            # Look for KEY_VALUE_SET blocks that are KEYs (not VALUEs)
            if block['BlockType'] == 'KEY_VALUE_SET' and 'KEY' in block.get('EntityTypes', []):
                key_text = self._get_text_from_block(block, block_map)
                value_text = ''
                confidence = block.get('Confidence', 0)

                # Find the associated VALUE block through relationships
                for relationship in block.get('Relationships', []):
                    if relationship['Type'] == 'VALUE':
                        for value_id in relationship['Ids']:
                            value_block = block_map.get(value_id)
                            if value_block:
                                value_text = self._get_text_from_block(value_block, block_map)

                if key_text:
                    key_value_pairs.append({
                        'key': key_text,
                        'value': value_text,
                        'confidence': confidence
                    })

        # Display results
        print(f"\nDetected {len(key_value_pairs)} key-value pair(s)\n")
        print("FORM FIELDS:")
        print("-" * 70)

        for kv in key_value_pairs:
            print(f"  {kv['key']:30s}: {kv['value']:30s} ({kv['confidence']:.1f}%)")

        result = {
            'type': 'form_extraction',
            'file': str(file_path),
            'key_value_pairs': key_value_pairs,
            'statistics': {
                'total_fields': len(key_value_pairs),
                'avg_confidence': sum(kv['confidence'] for kv in key_value_pairs) / len(key_value_pairs) if key_value_pairs else 0
            }
        }

        output_file = self._save_output(result, file_path, 'forms')
        print(f"\nSaved to: {output_file}")

        return result

    # =========================================================================
    # 4. EXPENSE ANALYSIS
    # =========================================================================
    def analyze_expense(self, file_path):
        """
        Analyze invoices and receipts.

        API: analyze_expense

        LEARNING NOTE - Why a Specialized API?
        Invoices and receipts have common patterns:
        - Vendor information
        - Date, invoice number
        - Line items with quantities and prices
        - Subtotals, taxes, totals

        analyze_expense is pre-trained to understand these patterns,
        giving you normalized field names like VENDOR_NAME, TOTAL, TAX
        instead of raw text that you'd have to interpret yourself.

        LEARNING NOTE - Response Structure:
        - ExpenseDocuments: List of documents found (usually 1)
          - SummaryFields: High-level fields (vendor, total, date)
          - LineItemGroups: Groups of line items
            - LineItems: Individual items with their fields

        FIELD TYPES (automatically identified):
        Summary: VENDOR_NAME, VENDOR_ADDRESS, INVOICE_RECEIPT_DATE,
                 INVOICE_RECEIPT_ID, TOTAL, SUBTOTAL, TAX, etc.
        Line Items: ITEM, QUANTITY, UNIT_PRICE, PRICE, etc.

        COST: $10 per 1000 pages
        """
        print(f"\n{'='*70}")
        print("EXPENSE / INVOICE ANALYSIS")
        print(f"{'='*70}")

        image_bytes = self._read_document(file_path)

        # This API is specifically designed for financial documents
        response = self.textract.analyze_expense(
            Document={'Bytes': image_bytes}
        )

        results = []

        for doc in response.get('ExpenseDocuments', []):
            # Summary fields are the key information extracted
            summary = {}
            print("\nSUMMARY FIELDS:")
            print("-" * 70)

            for field in doc.get('SummaryFields', []):
                # Type.Text gives you the normalized field name
                field_type = field.get('Type', {}).get('Text', 'Unknown')
                # ValueDetection contains the actual value and confidence
                value = field.get('ValueDetection', {}).get('Text', 'N/A')
                confidence = field.get('ValueDetection', {}).get('Confidence', 0)

                summary[field_type] = {
                    'value': value,
                    'confidence': confidence
                }
                print(f"  {field_type:25s}: {value:30s} ({confidence:.1f}%)")

            # Line items are grouped (e.g., all items from one table)
            line_items = []
            print("\nLINE ITEMS:")
            print("-" * 70)

            for group in doc.get('LineItemGroups', []):
                for idx, item in enumerate(group.get('LineItems', []), 1):
                    item_data = {}
                    print(f"\n  Item {idx}:")
                    for field in item.get('LineItemExpenseFields', []):
                        field_type = field.get('Type', {}).get('Text', 'Unknown')
                        value = field.get('ValueDetection', {}).get('Text', 'N/A')
                        item_data[field_type] = value
                        print(f"    {field_type:20s}: {value}")
                    line_items.append(item_data)

            results.append({
                'summary': summary,
                'line_items': line_items
            })

        result = {
            'type': 'expense_analysis',
            'file': str(file_path),
            'documents': results,
            'statistics': {
                'total_documents': len(results),
                'total_line_items': sum(len(r['line_items']) for r in results)
            }
        }

        output_file = self._save_output(result, file_path, 'expense')
        print(f"\nSaved to: {output_file}")

        return result

    # =========================================================================
    # 5. QUERY-BASED EXTRACTION
    # =========================================================================
    def query_document(self, file_path, questions):
        """
        Ask specific questions about a document.

        API: analyze_document with FeatureTypes=['QUERIES']

        LEARNING NOTE - What are Queries?
        Queries let you ask natural language questions about a document:
        - "What is the total amount?"
        - "What is the patient's name?"
        - "What is the expiration date?"

        Textract uses ML to understand your question, find the relevant
        part of the document, and extract the answer.

        LEARNING NOTE - When to Use Queries:
        - You need specific information, not full extraction
        - Document structure varies (can't rely on fixed positions)
        - Faster development (no need to parse complex structures)
        - Works well with unstructured documents

        LEARNING NOTE - Query Best Practices:
        - Be specific: "What is the invoice total?" > "What is the amount?"
        - Use aliases to track which answer goes with which question
        - Max 15 queries per API call
        - Questions should match how data appears in the document

        EXAMPLE QUERIES:
        - "What is the customer name?"
        - "What is the policy number?"
        - "What is the effective date?"
        - "What is the deductible amount?"

        COST: $15 per 1000 pages (charged per page, not per query)
        """
        print(f"\n{'='*70}")
        print("QUERY-BASED EXTRACTION")
        print(f"{'='*70}")

        image_bytes = self._read_document(file_path)

        # Format queries with aliases for easier tracking
        # Alias helps you match answers back to questions in the response
        queries = [{'Text': q, 'Alias': f'Q{i+1}'} for i, q in enumerate(questions)]

        response = self.textract.analyze_document(
            Document={'Bytes': image_bytes},
            FeatureTypes=['QUERIES'],
            QueriesConfig={'Queries': queries}
        )

        blocks = response.get('Blocks', [])

        # QUERY blocks contain the question, QUERY_RESULT blocks contain answers
        query_results = []
        print("\nQUERY RESULTS:")
        print("-" * 70)

        for block in blocks:
            if block['BlockType'] == 'QUERY':
                query_text = block.get('Query', {}).get('Text', '')
                alias = block.get('Query', {}).get('Alias', '')

                # Find the answer through ANSWER relationship
                answer_text = ''
                answer_confidence = 0

                for relationship in block.get('Relationships', []):
                    if relationship['Type'] == 'ANSWER':
                        for answer_id in relationship['Ids']:
                            for b in blocks:
                                if b['Id'] == answer_id and b['BlockType'] == 'QUERY_RESULT':
                                    answer_text = b.get('Text', 'No answer found')
                                    answer_confidence = b.get('Confidence', 0)

                query_results.append({
                    'question': query_text,
                    'alias': alias,
                    'answer': answer_text,
                    'confidence': answer_confidence
                })

                print(f"\n  Q: {query_text}")
                print(f"  A: {answer_text} ({answer_confidence:.1f}%)")

        result = {
            'type': 'query_extraction',
            'file': str(file_path),
            'queries': query_results,
            'statistics': {
                'total_queries': len(query_results),
                'answered': sum(1 for q in query_results if q['answer'])
            }
        }

        output_file = self._save_output(result, file_path, 'queries')
        print(f"\nSaved to: {output_file}")

        return result

    # =========================================================================
    # 6. ID DOCUMENT ANALYSIS
    # =========================================================================
    def analyze_id(self, file_path):
        """
        Analyze ID documents (passports, driver's licenses).

        API: analyze_id

        LEARNING NOTE - What is ID Analysis?
        A specialized API for identity documents that extracts:
        - Personal info: Name, DOB, Address
        - Document info: ID number, expiration date, issue date
        - Document type: PASSPORT, DRIVER_LICENSE, etc.

        LEARNING NOTE - Supported Document Types:
        - US Passports
        - US Driver's Licenses (all states)
        - US State IDs

        LEARNING NOTE - Extracted Fields:
        Common fields include:
        - FIRST_NAME, LAST_NAME, MIDDLE_NAME
        - DATE_OF_BIRTH, DATE_OF_ISSUE, DATE_OF_EXPIRY
        - DOCUMENT_NUMBER
        - ADDRESS, CITY, STATE, ZIP_CODE
        - ID_TYPE, CLASS, ENDORSEMENTS

        USE CASES:
        - Identity verification (KYC)
        - Customer onboarding
        - Age verification
        - Address verification

        SECURITY NOTE: ID documents contain PII (Personally Identifiable
        Information). Ensure proper data handling, encryption, and
        compliance with regulations (GDPR, CCPA, etc.)

        COST: $15 per 1000 pages
        """
        print(f"\n{'='*70}")
        print("ID DOCUMENT ANALYSIS")
        print(f"{'='*70}")

        image_bytes = self._read_document(file_path)

        # analyze_id expects a list of document pages
        # For multi-page documents, pass each page separately
        response = self.textract.analyze_id(
            DocumentPages=[{'Bytes': image_bytes}]
        )

        id_documents = []

        for doc in response.get('IdentityDocuments', []):
            doc_data = {
                'document_index': doc.get('DocumentIndex'),
                'fields': {}
            }

            print(f"\nID DOCUMENT FIELDS:")
            print("-" * 70)

            for field in doc.get('IdentityDocumentFields', []):
                field_type = field.get('Type', {}).get('Text', 'Unknown')
                value = field.get('ValueDetection', {}).get('Text', 'N/A')
                confidence = field.get('ValueDetection', {}).get('Confidence', 0)

                doc_data['fields'][field_type] = {
                    'value': value,
                    'confidence': confidence
                }

                print(f"  {field_type:25s}: {value:30s} ({confidence:.1f}%)")

            id_documents.append(doc_data)

        result = {
            'type': 'id_analysis',
            'file': str(file_path),
            'id_documents': id_documents,
            'statistics': {
                'total_documents': len(id_documents)
            }
        }

        output_file = self._save_output(result, file_path, 'id')
        print(f"\nSaved to: {output_file}")

        return result

    # =========================================================================
    # 7. ENTITY EXTRACTION (using Amazon Comprehend)
    # =========================================================================
    def extract_entities(self, file_path):
        """
        Extract named entities from document text using Amazon Comprehend.

        SERVICES: Textract (OCR) + Comprehend (NLP)

        LEARNING NOTE - What is Named Entity Recognition (NER)?
        NER identifies and classifies named entities in text:
        - PERSON: People's names
        - ORGANIZATION: Companies, agencies, institutions
        - LOCATION: Physical locations, addresses
        - DATE: Dates and times
        - QUANTITY: Numbers, measurements
        - COMMERCIAL_ITEM: Products
        - EVENT: Events
        - TITLE: Titles of books, songs, etc.

        LEARNING NOTE - Two-Stage Pipeline:
        1. Textract extracts text from the document (OCR)
        2. Comprehend analyzes the text for entities (NLP)

        This is a common IDP pattern - combining services for
        capabilities that no single service provides.

        LEARNING NOTE - Comprehend Capabilities Beyond NER:
        - Sentiment Analysis: Is text positive/negative?
        - Key Phrase Extraction: What are the main topics?
        - Language Detection: What language is this?
        - PII Detection: Find sensitive data
        - Custom Classification: Train your own classifiers
        - Custom Entity Recognition: Train to find your entities

        LEARNING NOTE - Text Chunking:
        Comprehend has a 5000 byte limit per request.
        For longer documents, we split the text into chunks.
        In production, you might use Comprehend's batch APIs instead.

        USE CASES:
        - Contract analysis (find parties, dates, amounts)
        - Resume parsing (find skills, companies, education)
        - News analysis (find people, organizations, locations)
        - Medical records (find medications, conditions, procedures)

        COST: Comprehend charges by character (~$0.0001 per character)
        """
        print(f"\n{'='*70}")
        print("ENTITY EXTRACTION (NLP)")
        print(f"{'='*70}")

        # Stage 1: Extract text using OCR
        print("\nStep 1: Extracting text with OCR...")
        ocr_result = self.extract_text(file_path)
        full_text = ocr_result['full_text']

        if not full_text.strip():
            print("No text found in document")
            return {'error': 'No text found'}

        # Stage 2: Analyze with Comprehend
        print("\nStep 2: Extracting entities with Amazon Comprehend...")

        # Split text into chunks (Comprehend limit: 5000 bytes per request)
        text_chunks = [full_text[i:i+5000] for i in range(0, len(full_text), 5000)]

        all_entities = []

        for chunk in text_chunks:
            if chunk.strip():
                # detect_entities finds named entities in text
                response = self.comprehend.detect_entities(
                    Text=chunk,
                    LanguageCode='en'  # Comprehend supports 12+ languages
                )
                all_entities.extend(response.get('Entities', []))

        # Group entities by type for better organization
        entities_by_type = {}
        for entity in all_entities:
            entity_type = entity['Type']
            if entity_type not in entities_by_type:
                entities_by_type[entity_type] = []
            entities_by_type[entity_type].append({
                'text': entity['Text'],
                'score': entity['Score']  # Confidence score 0-1
            })

        # Display entity results
        print("\nEXTRACTED ENTITIES:")
        print("-" * 70)

        for entity_type, entities in entities_by_type.items():
            print(f"\n  {entity_type}:")
            for e in entities[:5]:  # Show top 5 per type
                print(f"    - {e['text']} ({e['score']*100:.1f}%)")

        # Also extract key phrases - the main topics/concepts
        print("\nKEY PHRASES:")
        print("-" * 70)

        key_phrases = []
        for chunk in text_chunks:
            if chunk.strip():
                response = self.comprehend.detect_key_phrases(
                    Text=chunk,
                    LanguageCode='en'
                )
                key_phrases.extend(response.get('KeyPhrases', []))

        for phrase in key_phrases[:10]:  # Show top 10
            print(f"  - {phrase['Text']} ({phrase['Score']*100:.1f}%)")

        result = {
            'type': 'entity_extraction',
            'file': str(file_path),
            'entities_by_type': entities_by_type,
            'key_phrases': [{'text': p['Text'], 'score': p['Score']} for p in key_phrases],
            'statistics': {
                'total_entities': len(all_entities),
                'entity_types': list(entities_by_type.keys()),
                'total_key_phrases': len(key_phrases)
            }
        }

        output_file = self._save_output(result, file_path, 'entities')
        print(f"\nSaved to: {output_file}")

        return result

    # =========================================================================
    # 8. FULL IDP PIPELINE
    # =========================================================================
    def full_pipeline(self, file_path, include_id=False, questions=None):
        """
        Run complete IDP pipeline on document.

        LEARNING NOTE - Production IDP Pipelines:

        In production, a full IDP pipeline typically includes:

        1. INGESTION
           - Accept documents from multiple sources (email, upload, scan)
           - Store originals in S3 with metadata
           - Trigger processing via Lambda/Step Functions

        2. PREPROCESSING
           - Image enhancement (deskew, denoise, contrast)
           - PDF splitting for multi-page documents
           - Format conversion if needed

        3. CLASSIFICATION
           - Determine document type (invoice, contract, ID, etc.)
           - Route to appropriate extraction pipeline
           - Can use Comprehend Custom Classification

        4. EXTRACTION
           - Run appropriate Textract APIs based on document type
           - May combine multiple extraction methods

        5. POST-PROCESSING
           - Normalize data (dates, currencies, addresses)
           - Validate business rules
           - Flag low-confidence extractions for review

        6. HUMAN REVIEW (Amazon A2I)
           - Route low-confidence results to human reviewers
           - Capture corrections to improve future processing

        7. INTEGRATION
           - Transform to target schema
           - Push to downstream systems (ERP, CRM, database)
           - Trigger business workflows

        This demo runs steps 4-5 (extraction + basic processing).
        """
        print(f"\n{'#'*70}")
        print("FULL IDP PIPELINE")
        print(f"File: {file_path}")
        print(f"{'#'*70}")

        results = {
            'file': str(file_path),
            'timestamp': datetime.now().isoformat(),
            'analyses': {}
        }

        # Run each extraction method, catching errors to continue pipeline
        # In production, you'd want more sophisticated error handling

        # 1. Basic OCR - always useful as a baseline
        try:
            results['analyses']['ocr'] = self.extract_text(file_path)
        except Exception as e:
            print(f"OCR failed: {e}")

        # 2. Table extraction - for structured data
        try:
            results['analyses']['tables'] = self.extract_tables(file_path)
        except Exception as e:
            print(f"Table extraction failed: {e}")

        # 3. Form extraction - for key-value data
        try:
            results['analyses']['forms'] = self.extract_forms(file_path)
        except Exception as e:
            print(f"Form extraction failed: {e}")

        # 4. Expense analysis - for invoices/receipts
        try:
            results['analyses']['expense'] = self.analyze_expense(file_path)
        except Exception as e:
            print(f"Expense analysis failed: {e}")

        # 5. Query extraction - if questions provided
        if questions:
            try:
                results['analyses']['queries'] = self.query_document(file_path, questions)
            except Exception as e:
                print(f"Query extraction failed: {e}")

        # 6. ID analysis - optional, for identity documents
        if include_id:
            try:
                results['analyses']['id'] = self.analyze_id(file_path)
            except Exception as e:
                print(f"ID analysis failed: {e}")

        # 7. Entity extraction - NLP analysis
        try:
            results['analyses']['entities'] = self.extract_entities(file_path)
        except Exception as e:
            print(f"Entity extraction failed: {e}")

        # Save comprehensive results
        output_file = self._save_output(results, file_path, 'full_idp')

        print(f"\n{'#'*70}")
        print("PIPELINE COMPLETE")
        print(f"{'#'*70}")
        print(f"\nComprehensive results saved to: {output_file}")

        return results


def main():
    """
    CLI entry point for the IDP processor.

    LEARNING NOTE - CLI Design:
    This tool uses argparse for command-line argument parsing.
    Each command maps to a specific IDP capability.

    In production, you might:
    - Use this as a Lambda function instead of CLI
    - Create a REST API with API Gateway
    - Build a Step Functions workflow
    - Integrate with event-driven architecture (S3 triggers)
    """
    parser = argparse.ArgumentParser(
        description='AWS Intelligent Document Processing (IDP) - Learning Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
---------
  # Basic text extraction (OCR)
  python idp_processor.py ocr invoice.pdf

  # Extract tables from a report
  python idp_processor.py tables financial_report.png

  # Extract form fields
  python idp_processor.py forms tax_form.jpg

  # Analyze an invoice/receipt
  python idp_processor.py expense receipt.png

  # Ask questions about a document
  python idp_processor.py query invoice.pdf --questions "What is the total?" "What is the due date?"

  # Analyze an ID document
  python idp_processor.py id drivers_license.jpg

  # Extract entities (people, organizations, dates)
  python idp_processor.py entities contract.pdf

  # Run full IDP pipeline
  python idp_processor.py full document.pdf --questions "What is the total?"

LEARNING RESOURCES:
-------------------
  AWS Textract Documentation:
    https://docs.aws.amazon.com/textract/

  AWS Comprehend Documentation:
    https://docs.aws.amazon.com/comprehend/

  IDP on AWS:
    https://aws.amazon.com/intelligent-document-processing/
        """
    )

    parser.add_argument('command',
                        choices=['ocr', 'tables', 'forms', 'expense', 'query', 'id', 'entities', 'full'],
                        help='IDP command to run (see examples below)')
    parser.add_argument('file', help='Path to document (JPG, PNG, PDF)')
    parser.add_argument('--questions', '-q', nargs='+',
                        help='Questions for query command (use quotes for multi-word questions)')
    parser.add_argument('--include-id', action='store_true',
                        help='Include ID analysis in full pipeline')
    parser.add_argument('--region', default='us-east-1',
                        help='AWS region (default: us-east-1)')

    args = parser.parse_args()

    # Validate file exists
    if not Path(args.file).exists():
        print(f"Error: File not found: {args.file}")
        sys.exit(1)

    # Initialize processor and run requested command
    processor = IDPProcessor(region=args.region)

    try:
        if args.command == 'ocr':
            processor.extract_text(args.file)
        elif args.command == 'tables':
            processor.extract_tables(args.file)
        elif args.command == 'forms':
            processor.extract_forms(args.file)
        elif args.command == 'expense':
            processor.analyze_expense(args.file)
        elif args.command == 'query':
            if not args.questions:
                print("Error: --questions required for query command")
                print("Example: python idp_processor.py query doc.pdf --questions 'What is the total?'")
                sys.exit(1)
            processor.query_document(args.file, args.questions)
        elif args.command == 'id':
            processor.analyze_id(args.file)
        elif args.command == 'entities':
            processor.extract_entities(args.file)
        elif args.command == 'full':
            processor.full_pipeline(args.file, include_id=args.include_id, questions=args.questions)

    except Exception as e:
        print(f"\nError: {str(e)}")
        print("\nTROUBLESHOOTING:")
        print("  1. AWS credentials configured? Run: aws configure")
        print("  2. boto3 installed? Run: pip install boto3")
        print("  3. Correct permissions? Need: AmazonTextractFullAccess, ComprehendFullAccess")
        print("  4. Valid file format? Supported: JPG, PNG, PDF, TIFF")
        print("  5. File size < 10MB? Larger files need S3-based processing")
        sys.exit(1)


if __name__ == '__main__':
    main()