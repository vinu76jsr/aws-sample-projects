"""
AWS Client Factory Module
=========================

WHAT THIS MODULE DOES:
This module creates and returns AWS service clients using the boto3 library.
It provides factory functions that other modules use to interact with AWS services.

WHAT IS BOTO3?
--------------
boto3 is the official AWS SDK (Software Development Kit) for Python.
- "boto" comes from the Portuguese word for "dolphin" (Amazon river dolphins!)
- It allows Python code to interact with AWS services like Kendra, S3, EC2, etc.
- boto3 handles authentication, API calls, retries, and response parsing

HOW BOTO3 AUTHENTICATION WORKS:
-------------------------------
boto3 automatically looks for AWS credentials in this order (credential chain):

1. Environment variables:
   - AWS_ACCESS_KEY_ID
   - AWS_SECRET_ACCESS_KEY
   - AWS_SESSION_TOKEN (optional, for temporary credentials)

2. Shared credential file (~/.aws/credentials):
   [default]
   aws_access_key_id = YOUR_KEY
   aws_secret_access_key = YOUR_SECRET

3. AWS config file (~/.aws/config):
   [default]
   region = us-east-1

4. IAM role (if running on EC2, Lambda, ECS, etc.):
   - AWS automatically provides credentials to the instance/container

5. Container credentials (ECS/EKS)

LEARNING TIP: For local development, use environment variables or ~/.aws/credentials.
For production on AWS infrastructure, use IAM roles (more secure, no hardcoded keys).

WHAT IS A "CLIENT" IN BOTO3?
----------------------------
A client is a low-level interface to an AWS service. It maps directly to the
AWS service API. Each method on the client corresponds to an API operation.

Client vs Resource:
- Client: Low-level, 1-to-1 mapping with service API, works with dictionaries
- Resource: Higher-level, object-oriented interface (not available for all services)

For Kendra, only the client interface is available (no resource interface).
"""

import boto3
from .config import Config

# =============================================================================
# PYTHON IMPORT PATTERN: Relative Imports
# =============================================================================
# "from .config import Config" uses a RELATIVE import
# The dot (.) means "from the same package (src folder)"
#
# Relative imports:
#   from .module import X      # Same directory
#   from ..module import X     # Parent directory
#
# Absolute imports:
#   from src.config import Config  # Full path from project root
#
# Relative imports are preferred within a package for maintainability.
# =============================================================================


def get_kendra_client():
    """
    Create and return an Amazon Kendra client.

    WHAT IS AMAZON KENDRA?
    ----------------------
    Amazon Kendra is an intelligent enterprise search service that:
    - Uses machine learning to understand natural language queries
    - Returns direct answers, not just document links
    - Indexes content from multiple sources (S3, SharePoint, databases, etc.)
    - Understands context and intent (semantic search)

    Example: Instead of searching "PTO policy" and getting 50 documents,
    Kendra might return: "Employees receive 15 days of PTO per year."

    HOW THIS FUNCTION WORKS:
    ------------------------
    boto3.client(service_name, **kwargs) creates a low-level service client.

    Parameters:
    - service_name: The AWS service to connect to ("kendra", "s3", "ec2", etc.)
    - region_name: The AWS region where the service runs

    Returns:
    - A client object with methods for all Kendra API operations like:
      - create_index()
      - batch_put_document()
      - query()
      - delete_index()
      - etc.

    WHY CREATE A NEW CLIENT EACH TIME?
    ----------------------------------
    boto3 clients are lightweight and thread-safe. Creating a new client
    each time is a common pattern that ensures:
    1. Fresh credentials (important if using temporary credentials)
    2. No shared state issues
    3. Simple, stateless functions

    For high-performance applications, you might reuse a single client.

    Returns:
        botocore.client.Kendra: A Kendra service client
    """
    return boto3.client(
        "kendra",  # Service name - tells boto3 which AWS service to use
        region_name=Config.AWS_REGION  # Which AWS region to connect to
    )


def get_s3_client():
    """
    Create and return an Amazon S3 client.

    WHAT IS AMAZON S3?
    ------------------
    Amazon S3 (Simple Storage Service) is object storage:
    - Stores any amount of data as "objects" in "buckets"
    - Highly durable (99.999999999% - "11 nines")
    - Objects can be files of any type (documents, images, videos, etc.)
    - Commonly used with Kendra as a document source

    S3 TERMINOLOGY:
    ---------------
    - Bucket: A container for objects (like a top-level folder)
    - Object: A file stored in S3 (has a key, value, and metadata)
    - Key: The unique identifier for an object within a bucket (like a file path)
    - Prefix: A partial key used to organize objects (like folders, but S3 is flat)

    Example S3 paths:
    - s3://my-bucket/documents/report.pdf
    - Bucket: "my-bucket", Key: "documents/report.pdf"

    HOW S3 WORKS WITH KENDRA:
    -------------------------
    1. Store your documents in an S3 bucket
    2. Create an S3 data source in Kendra pointing to that bucket
    3. Kendra crawls the bucket and indexes the documents
    4. Set up a sync schedule to keep content up-to-date

    Supported file types: PDF, HTML, Word, PowerPoint, plain text, and more!

    Returns:
        botocore.client.S3: An S3 service client
    """
    return boto3.client(
        "s3",  # Service name for Simple Storage Service
        region_name=Config.AWS_REGION  # Region where your S3 bucket is located
    )


# =============================================================================
# LEARNING EXERCISE:
# =============================================================================
# Try these commands to explore boto3 clients:
#
# >>> from src.kendra_client import get_kendra_client
# >>> kendra = get_kendra_client()
# >>> dir(kendra)  # See all available methods
#
# >>> # List all Kendra indexes in your account:
# >>> response = kendra.list_indices()
# >>> print(response)
#
# >>> # See what operations are available:
# >>> print([m for m in dir(kendra) if not m.startswith('_')])
#
# COMMON KENDRA CLIENT METHODS:
# - create_index() - Create a new search index
# - describe_index() - Get index details
# - list_indices() - List all indexes
# - batch_put_document() - Add documents directly
# - query() - Search the index
# - get_query_suggestions() - Get autocomplete suggestions
# - create_data_source() - Add a data source (S3, SharePoint, etc.)
# - start_data_source_sync_job() - Sync documents from data source
# =============================================================================


# =============================================================================
# DESIGN PATTERN: Factory Functions
# =============================================================================
# This module uses the "Factory" design pattern. Factory functions:
# - Create and return objects
# - Hide the complexity of object creation
# - Make it easy to change how objects are created in one place
# - Allow for dependency injection in tests (swap in mock clients)
#
# In larger applications, you might use:
# - Dependency Injection frameworks
# - Connection pools for clients
# - Singleton pattern to reuse a single client
# =============================================================================
