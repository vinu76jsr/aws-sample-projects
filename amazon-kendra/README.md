# Amazon Kendra Sample Project

A Python sample project demonstrating how to use Amazon Kendra for intelligent enterprise search.

## Prerequisites

- Python 3.8+
- AWS Account (Kendra is available in most regions)
- AWS CLI installed and configured (optional but recommended)
- AWS credentials configured (via environment variables, AWS CLI, or IAM role)

---

## AWS Setup Guide (Before Running the Project)

Before you can run this sample project, you need to create the required AWS resources. Follow these steps:

### Step 1: Create an IAM Role for Kendra

Kendra needs an IAM role to access CloudWatch Logs and optionally S3.

1. Go to **AWS Console > IAM > Roles > Create Role**
2. Select **Custom trust policy** as the trusted entity type
3. Paste this trust policy (allows Kendra to assume the role):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "kendra.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

4. Click **Next** and attach the policy `CloudWatchLogsFullAccess` (or create a custom policy - see below)
5. Name the role (e.g., `KendraIndexRole`)
6. Create the role and **copy the Role ARN** (you'll need this for `KENDRA_ROLE_ARN`)

**Custom IAM Policy (minimum permissions):**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudwatch:PutMetricData"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "cloudwatch:namespace": "AWS/Kendra"
        }
      }
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:DescribeLogGroups"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:DescribeLogStreams",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:log-group:/aws/kendra/*"
    }
  ]
}
```

### Step 2: Create a Kendra Index

**Option A: Using AWS Console (Recommended for beginners)**

1. Go to **AWS Console > Amazon Kendra**
2. Click **Create Index**
3. Configure the index:
   - **Index name**: Choose a descriptive name (e.g., `my-sample-index`)
   - **Description**: Optional description
   - **IAM role**: Select the role you created in Step 1
   - **Edition**: Choose **Developer Edition** for learning/testing
     - Developer Edition: ~$810/month, up to 10,000 documents
     - Enterprise Edition: Higher capacity, multi-AZ (production use)
4. Click **Create**
5. **Wait 15-30 minutes** for the index to become ACTIVE
6. Once active, **copy the Index ID** from the index details page

**Option B: Using AWS CLI**

```bash
# Create the index
aws kendra create-index \
  --name "my-sample-index" \
  --description "Sample index for learning Kendra" \
  --edition DEVELOPER_EDITION \
  --role-arn "arn:aws:iam::YOUR_ACCOUNT_ID:role/KendraIndexRole"

# The command returns an index ID - save this!

# Check index status (wait until Status is ACTIVE)
aws kendra describe-index --id YOUR_INDEX_ID
```

**Option C: Using this project's code**

After completing the basic setup, you can also create an index programmatically:

```python
from src.index_manager import create_index

response = create_index(
    name="my-sample-index",
    description="Sample index for learning Kendra"
)
print(f"Index ID: {response['Id']}")
```

### Step 3: (Optional) Create an S3 Bucket for Documents

If you want to use S3 as a document data source:

1. Go to **AWS Console > S3 > Create Bucket**
2. Choose a globally unique bucket name
3. Select the same region as your Kendra index
4. Keep default settings and create the bucket
5. Add S3 permissions to your Kendra role:

```json
{
  "Effect": "Allow",
  "Action": [
    "s3:GetObject"
  ],
  "Resource": "arn:aws:s3:::YOUR_BUCKET_NAME/*"
},
{
  "Effect": "Allow",
  "Action": [
    "s3:ListBucket"
  ],
  "Resource": "arn:aws:s3:::YOUR_BUCKET_NAME"
}
```

### Step 4: Configure Your AWS Credentials

Make sure your local environment can authenticate with AWS. Choose one method:

**Method A: AWS CLI (Recommended)**

```bash
aws configure
# Enter your Access Key ID, Secret Access Key, and default region
```

**Method B: Environment Variables**

```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_REGION="us-east-1"
```

**Method C: AWS Credentials File**

Create/edit `~/.aws/credentials`:

```ini
[default]
aws_access_key_id = your-access-key
aws_secret_access_key = your-secret-key
```

### Step 5: Verify Your Setup

```bash
# Verify AWS credentials are working
aws sts get-caller-identity

# Verify Kendra index is accessible
aws kendra describe-index --id YOUR_INDEX_ID
```

---

## Important Cost Information

**Amazon Kendra is not a free service.** Be aware of the costs:

| Edition | Base Cost | Document Cost | Query Limit |
|---------|-----------|---------------|-------------|
| Developer | ~$810/month | $0.40/document/month | 4,000 queries/day |
| Enterprise | ~$1,008/hour | Additional costs | Higher limits |

**Tips to minimize costs:**
- Use Developer Edition for learning
- Delete your index when not actively using it
- Monitor usage in AWS Cost Explorer

---

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Configure environment variables:

```bash
cp .env.example .env
# Edit .env with your AWS credentials and Kendra index ID
```

## Configuration

Set these environment variables in your `.env` file:

| Variable | Description |
|----------|-------------|
| `AWS_REGION` | AWS region (default: us-east-1) |
| `KENDRA_INDEX_ID` | Your Kendra index ID |
| `KENDRA_ROLE_ARN` | IAM role ARN for Kendra operations |
| `S3_BUCKET_NAME` | Optional: S3 bucket for document storage |

## Project Structure

```
amazon-kendra-sample/
├── src/
│   ├── __init__.py
│   ├── config.py           # Configuration management
│   ├── kendra_client.py    # AWS client initialization
│   ├── index_manager.py    # Index CRUD operations
│   ├── document_manager.py # Document ingestion
│   └── search.py           # Query and search functions
├── data/
│   └── sample_documents.json
├── main.py                 # Example usage
├── requirements.txt
└── README.md
```

## Usage

### List Indexes

```python
from src.index_manager import list_indexes

indexes = list_indexes()
for idx in indexes:
    print(f"{idx['Name']}: {idx['Status']}")
```

### Add Documents

```python
from src.document_manager import add_documents

documents = [
    {
        "Id": "doc-1",
        "Title": "My Document",
        "Content": "This is the document content..."
    }
]

add_documents(documents)
```

### Search

```python
from src.search import search_and_print, query

# Simple search with formatted output
search_and_print("What is machine learning?")

# Programmatic search
response = query("How do I configure Kendra?")
for item in response["ResultItems"]:
    print(item["DocumentTitle"]["Text"])
```

### Create an Index

```python
from src.index_manager import create_index

# Requires KENDRA_ROLE_ARN to be set
response = create_index(
    name="my-search-index",
    description="Index for my documents"
)
```

## Running the Demo

```bash
python main.py
```

## IAM Permissions

Your IAM role/user needs these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "kendra:*"
      ],
      "Resource": "*"
    }
  ]
}
```

For production, scope down permissions to specific resources.

## Cleanup

To avoid ongoing charges, delete your Kendra resources when done:

```bash
python cleanup.py
```

This script will:
- Show your index details
- Ask for confirmation (type `DELETE`)
- Delete the Kendra index

**Note:** You can optionally delete the IAM role (IAM roles are free, so no cost impact):
- AWS Console > IAM > Roles > Delete `KendraIndexRole`

## Resources

- [Amazon Kendra Documentation](https://docs.aws.amazon.com/kendra/)
- [Boto3 Kendra Reference](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/kendra.html)
- [Kendra Pricing](https://aws.amazon.com/kendra/pricing/)
