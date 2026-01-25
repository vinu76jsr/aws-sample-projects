#!/bin/bash

echo "🚀 AWS Textract Quick Start"
echo ""

# Check if boto3 is installed
if ! python3 -c "import boto3" 2>/dev/null; then
    echo "📦 Installing boto3..."
    pip install boto3
else
    echo "✅ boto3 already installed"
fi

# Check AWS credentials
if aws sts get-caller-identity &>/dev/null; then
    echo "✅ AWS credentials configured"
    echo ""
    echo "Your AWS Account ID: $(aws sts get-caller-identity --query Account --output text)"
else
    echo "⚠️  AWS credentials not configured"
    echo ""
    echo "Run: aws configure"
    echo "Then enter your Access Key ID and Secret Access Key"
    exit 1
fi

# Download sample invoice if it doesn't exist
if [ ! -f "sample_receipt.png" ]; then
    echo ""
    echo "📥 Downloading sample receipt..."
    curl -o sample_receipt.png \
      "https://templates.invoicehome.com/invoice-template-us-neat-750px.png" \
      -L -s
    echo "✅ Sample receipt downloaded"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Try it now:"
echo "  python3 simple_textract.py sample_receipt.png"
echo ""
