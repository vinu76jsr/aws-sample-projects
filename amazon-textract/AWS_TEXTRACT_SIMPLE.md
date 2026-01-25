# Simple AWS Textract Task

**Goal**: Extract data from a receipt/invoice image using AWS Textract

**Time**: 30-60 minutes

**What you'll extract**:
- Vendor name
- Total amount
- Date
- Tax
- Line items (description, quantity, price)

---

## Setup (5 minutes)

### 1. Install boto3
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

That's it!

---

## Usage

### Step 1: Get a sample invoice

Download a sample or use your own:
```bash
# Download sample receipt
curl -o sample_receipt.png \
  "https://templates.invoicehome.com/invoice-template-us-neat-750px.png"
```

Or take a photo of any receipt on your phone and upload it.

### Step 2: Run the script

```bash
python simple_textract.py sample_receipt.png
```

### Step 3: Check the output

You'll see:
```
📄 Processing: sample_receipt.png
==================================================

🔍 Calling AWS Textract...

✅ Extraction Complete!

📋 SUMMARY:
--------------------------------------------------
VENDOR_NAME              : ABC Company            (Confidence: 99.8%)
INVOICE_RECEIPT_DATE     : 01/15/2026            (Confidence: 99.5%)
TOTAL                    : $1,234.56             (Confidence: 99.9%)
TAX                      : $123.45               (Confidence: 99.6%)

📝 LINE ITEMS:
--------------------------------------------------

Item 1:
  ITEM                : Professional Services
  QUANTITY            : 40
  PRICE               : $1,000.00

Item 2:
  ITEM                : Materials
  QUANTITY            : 1
  PRICE               : $234.56

💾 Saved to: sample_receipt_extracted.json
```

The extracted data is also saved as JSON.

---

## What This Does

1. **Reads** your image/PDF
2. **Sends** it to AWS Textract
3. **Extracts** structured data:
   - Summary fields (vendor, total, date, tax)
   - Line items (each product/service)
4. **Displays** results in terminal
5. **Saves** structured JSON

---

## Cost

- **First 1,000 pages**: FREE (first 3 months)
- **After that**: $0.15 per page
- **This test**: ~$0.15 or FREE

---

## Try Different Documents

```bash
# Try with a receipt
python simple_textract.py grocery_receipt.jpg

# Try with an invoice
python simple_textract.py invoice.pdf

# Try with a utility bill
python simple_textract.py electric_bill.pdf
```

---

## Understanding the Output

The script extracts:

### Summary Fields
Common fields Textract finds:
- `VENDOR_NAME` - Who issued the document
- `TOTAL` - Total amount
- `TAX` - Tax amount
- `INVOICE_RECEIPT_DATE` - Date
- `INVOICE_RECEIPT_ID` - Invoice/receipt number
- `SUBTOTAL` - Amount before tax

### Line Items
For each product/service:
- `ITEM` - Description
- `QUANTITY` - How many
- `UNIT_PRICE` - Price per unit
- `PRICE` - Total for this line

---

## Common Issues

**Error: "Unable to locate credentials"**
```bash
# Fix: Configure AWS
aws configure
```

**Error: "An error occurred (InvalidParameterException)"**
- Check file format (must be JPG, PNG, or PDF)
- Check file size (max 10MB for synchronous calls)

**Error: "An error occurred (AccessDeniedException)"**
- Your AWS user needs Textract permissions
- Add `AmazonTextractFullAccess` policy to your IAM user

---

## Next Steps (Optional)

Want to do more? Try:

1. **Add S3 upload**: Upload to S3 instead of local file
2. **Add validation**: Check if required fields are present
3. **Add database**: Store extracted data in DynamoDB
4. **Batch processing**: Process multiple files at once

---

## That's It!

This is a simple introduction to AWS Textract. The whole task should take less than an hour including setup.

**Key takeaway**: AWS Textract automatically extracts structured data from documents without any training or configuration. Just send the image and get the data back!
