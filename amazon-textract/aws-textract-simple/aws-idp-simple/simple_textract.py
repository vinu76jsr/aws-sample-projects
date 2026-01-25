#!/usr/bin/env python3
"""
Simple AWS Textract Demo - Extract data from invoices/receipts

Task: Upload a receipt/invoice image and extract:
- Vendor name
- Total amount
- Date
- Line items

Time: 30-60 minutes
"""

import boto3
import json
import sys
from pathlib import Path

def process_invoice(image_path):
    """Extract data from invoice using AWS Textract"""
    
    # Initialize Textract client
    textract = boto3.client('textract', region_name='us-east-1')
    
    print(f"\n📄 Processing: {image_path}")
    print("=" * 70)
    
    # Read the image file
    with open(image_path, 'rb') as document:
        image_bytes = document.read()
    
    # Call AWS Textract AnalyzeExpense API
    print("\n🔍 Calling AWS Textract...")
    response = textract.analyze_expense(
        Document={'Bytes': image_bytes}
    )



    
    # Extract and display results
    print("\n✅ Extraction Complete!\n")
    
    for doc in response.get('ExpenseDocuments', []):
        # Print summary fields
        print("📋 SUMMARY:")
        print("-" * 70)
        
        summary_data = {}
        for field in doc.get('SummaryFields', []):
            field_type = field.get('Type', {}).get('Text', 'Unknown')
            value = field.get('ValueDetection', {}).get('Text', 'N/A')
            confidence = field.get('ValueDetection', {}).get('Confidence', 0)
            
            summary_data[field_type] = value
            print(f"{field_type:25s}: {value:30s} (Confidence: {confidence:.1f}%)")
        
        # Print line items
        print("\n📝 LINE ITEMS:")
        print("-" * 70)
        
        line_items = []
        for group in doc.get('LineItemGroups', []):
            for idx, item in enumerate(group.get('LineItems', []), 1):
                print(f"\nItem {idx}:")
                item_data = {}
                for field in item.get('LineItemExpenseFields', []):
                    field_type = field.get('Type', {}).get('Text', 'Unknown')
                    value = field.get('ValueDetection', {}).get('Text', 'N/A')
                    item_data[field_type] = value
                    print(f"  {field_type:20s}: {value}")
                line_items.append(item_data)
        
        # Save structured output
        output = {
            'summary': summary_data,
            'line_items': line_items
        }
        
        output_file = Path(image_path).stem + '_extracted.json'
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n💾 Saved to: {output_file}")
        print("\nExtracted Data Summary:")
        print(f"  Vendor: {summary_data.get('VENDOR_NAME', 'N/A')}")
        print(f"  Total:  {summary_data.get('TOTAL', 'N/A')}")
        print(f"  Date:   {summary_data.get('INVOICE_RECEIPT_DATE', 'N/A')}")
        print(f"  Items:  {len(line_items)}")

def main():
    if len(sys.argv) < 2:
        print("\nUsage: python simple_textract.py <invoice_image.jpg|pdf>")
        print("\nExample:")
        print("  python simple_textract.py sample_receipt.jpg")
        print("\nSupported formats: JPG, PNG, PDF")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not Path(image_path).exists():
        print(f"❌ Error: File not found: {image_path}")
        sys.exit(1)
    
    try:
        process_invoice(image_path)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nMake sure you have:")
        print("  1. AWS credentials configured (aws configure)")
        print("  2. boto3 installed (pip install boto3)")
        print("  3. AWS account with Textract access")
        sys.exit(1)

if __name__ == '__main__':
    main()
