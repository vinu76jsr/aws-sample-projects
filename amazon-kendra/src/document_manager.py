"""
Document Manager Module - Ingesting Content into Kendra
========================================================

WHAT THIS MODULE DOES:
This module handles adding (ingesting) documents into a Kendra index
and managing document sources. Documents are the content that users
will search through.

HOW KENDRA DOCUMENT INGESTION WORKS:
------------------------------------
There are two main ways to add documents to Kendra:

1. DIRECT INGESTION (BatchPutDocument API):
   - You send document content directly to Kendra
   - Good for: Small document sets, real-time updates, custom sources
   - Limit: 10 documents per batch, 50MB total per call

2. DATA SOURCE CONNECTORS:
   - Kendra crawls documents from a source (S3, SharePoint, etc.)
   - Good for: Large document sets, automatic syncing
   - Kendra extracts text from PDFs, Word docs, HTML, etc.

DOCUMENT STRUCTURE:
-------------------
Every document in Kendra has:
- Id: Unique identifier (you provide this)
- Title: Document title (displayed in search results)
- Content/Blob: The actual document text
- Attributes: Optional metadata (author, date, category, etc.)

SUPPORTED CONTENT TYPES:
------------------------
When using BatchPutDocument:
- PLAIN_TEXT: Plain text content
- HTML: HTML content (Kendra extracts text)
- PDF: PDF documents
- MS_WORD: Word documents (.doc, .docx)
- PPT: PowerPoint files

When using S3 data source, Kendra auto-detects file types.

DOCUMENT ATTRIBUTES (FACETS):
-----------------------------
Attributes are metadata fields that enable:
- Filtering search results (e.g., "show only HR documents")
- Faceted search (e.g., "5 results in Category: HR")
- Boosting relevance (e.g., prioritize recent documents)

Built-in attributes: _created_at, _last_updated_at, _source_uri, _version
Custom attributes: You define these (e.g., "Department", "Author", "Status")
"""

from .kendra_client import get_kendra_client
from .config import Config


def add_documents(documents: list, index_id: str = None) -> dict:
    """
    Add documents directly to a Kendra index using the BatchPutDocument API.

    WHAT THIS FUNCTION DOES:
    ------------------------
    Takes a list of documents and uploads them to Kendra for indexing.
    This is the "direct" approach to adding content - you provide the
    text directly rather than pointing Kendra to a file storage location.

    WHEN TO USE THIS FUNCTION:
    --------------------------
    - Adding a few documents at a time
    - Content that isn't stored in S3/SharePoint/databases
    - Real-time updates (e.g., adding a new FAQ immediately)
    - Testing and development

    WHEN NOT TO USE THIS FUNCTION:
    ------------------------------
    - Bulk loading thousands of documents (use S3 data source instead)
    - Documents stored in supported systems (S3, SharePoint, etc.)
    - When you need automatic syncing/updates

    Args:
        documents (list): List of document dictionaries. Each must have:
            Required:
                - "Id": Unique identifier (string, you choose this)
                - "Content": The text content of the document

            Optional:
                - "Title": Document title (displayed in results)
                - "Attributes": List of metadata attributes

        index_id (str, optional): Which index to add documents to.
                                 Defaults to KENDRA_INDEX_ID from config.

    Returns:
        dict: Response from AWS containing:
            {
                'FailedDocuments': [
                    {
                        'Id': 'doc-123',
                        'ErrorCode': 'InvalidDocument',
                        'ErrorMessage': 'Content too large'
                    },
                    ...
                ],
                'ResponseMetadata': {...}
            }

    DOCUMENT FORMAT EXAMPLES:
    -------------------------
    Basic document:
    >>> doc = {
    ...     "Id": "faq-001",
    ...     "Title": "What is Kendra?",
    ...     "Content": "Amazon Kendra is an intelligent search service..."
    ... }

    Document with attributes (for filtering):
    >>> doc = {
    ...     "Id": "policy-hr-001",
    ...     "Title": "PTO Policy",
    ...     "Content": "Employees receive 15 days of paid time off...",
    ...     "Attributes": [
    ...         {
    ...             "Key": "_category",         # Built-in attribute
    ...             "Value": {"StringValue": "HR"}
    ...         },
    ...         {
    ...             "Key": "Department",        # Custom attribute
    ...             "Value": {"StringValue": "Human Resources"}
    ...         },
    ...         {
    ...             "Key": "_created_at",       # Built-in timestamp
    ...             "Value": {"DateValue": "2024-01-15T00:00:00Z"}
    ...         }
    ...     ]
    ... }

    LIMITS AND CONSTRAINTS:
    -----------------------
    - Max 10 documents per batch call
    - Max 50MB total content size per call
    - Max 5MB per individual document
    - Max 40,000 characters per document (for search purposes)
    """
    client = get_kendra_client()

    # Use provided index_id or fall back to environment config
    index_id = index_id or Config.KENDRA_INDEX_ID

    # ==========================================================================
    # FORMAT DOCUMENTS FOR KENDRA API
    # ==========================================================================
    # The Kendra API expects a specific format different from our input.
    # We need to convert our simple dict format to Kendra's expected structure.
    formatted_docs = []

    for doc in documents:
        # Build the document structure expected by Kendra
        formatted_doc = {
            # Id: Required. Your unique identifier for this document.
            # Use something meaningful like "faq-001" or "policy-hr-vacation"
            # This ID is used for updates and deletes later.
            "Id": doc["Id"],

            # Title: Optional but highly recommended.
            # This appears in search results and helps users identify documents.
            # .get() provides a default empty string if not specified.
            "Title": doc.get("Title", ""),

            # Blob: The actual document content as bytes.
            # IMPORTANT: Content must be encoded as UTF-8 bytes, not a string!
            # This is because Kendra supports binary content (PDFs, etc.)
            # .encode("utf-8") converts the string to bytes.
            "Blob": doc["Content"].encode("utf-8"),

            # ContentType: Tells Kendra how to interpret the Blob.
            # Options: PLAIN_TEXT, HTML, PDF, MS_WORD, PPT
            # Since we're sending text strings, we use PLAIN_TEXT.
            "ContentType": "PLAIN_TEXT",
        }

        # ==========================================================================
        # OPTIONAL: Add document attributes (metadata)
        # ==========================================================================
        # Attributes enable filtering and faceting in search results.
        # Example use case: "Show me only documents from the HR department"
        if "Attributes" in doc:
            formatted_doc["Attributes"] = doc["Attributes"]

        formatted_docs.append(formatted_doc)

    # ==========================================================================
    # CALL THE BATCH PUT DOCUMENT API
    # ==========================================================================
    # This sends documents to Kendra for indexing.
    # "Batch" means multiple documents in one API call (more efficient).
    response = client.batch_put_document(
        IndexId=index_id,        # Which index to add documents to
        Documents=formatted_docs,  # The formatted document list
    )

    # ==========================================================================
    # HANDLE PARTIAL FAILURES
    # ==========================================================================
    # BatchPutDocument can partially succeed - some docs indexed, some failed.
    # Always check FailedDocuments to ensure all your content was indexed!
    failed = response.get("FailedDocuments", [])

    if failed:
        # Some documents failed - log details for debugging
        print(f"Warning: {len(failed)} documents failed to index")
        for f in failed:
            print(f"  - {f['Id']}: {f.get('ErrorMessage', 'Unknown error')}")

    # Calculate and report success count
    success_count = len(documents) - len(failed)
    print(f"Successfully submitted {success_count} documents")

    # Note: "submitted" doesn't mean "indexed"!
    # Indexing happens asynchronously and takes a few seconds to minutes.
    # Documents won't appear in search results immediately.

    return response


def delete_documents(document_ids: list, index_id: str = None) -> dict:
    """
    Delete documents from a Kendra index.

    WHAT THIS FUNCTION DOES:
    ------------------------
    Removes specified documents from the index. Once deleted, the
    documents will no longer appear in search results.

    WHEN TO USE THIS FUNCTION:
    --------------------------
    - Removing outdated content
    - Removing sensitive/incorrect information
    - Cleaning up test data
    - Implementing document lifecycle management

    Note: If you're using a data source (like S3), Kendra can
    automatically remove deleted files during sync. This function
    is mainly for directly-added documents.

    Args:
        document_ids (list): List of document ID strings to delete.
                            These are the IDs you specified when adding documents.
                            Example: ["doc-001", "doc-002", "faq-vacation"]

        index_id (str, optional): Which index to delete from.
                                 Defaults to KENDRA_INDEX_ID from config.

    Returns:
        dict: Response from AWS containing:
            {
                'FailedDocuments': [...],  # Any documents that failed to delete
                'ResponseMetadata': {...}
            }

    EXAMPLE USAGE:
    --------------
    >>> # Delete specific documents
    >>> delete_documents(["old-faq-001", "deprecated-policy-002"])
    Deleted 2 documents

    >>> # Delete all test documents (by ID pattern)
    >>> test_ids = ["test-1", "test-2", "test-3"]
    >>> delete_documents(test_ids)

    LIMITS:
    -------
    - Max 10 document IDs per batch call
    - For larger deletions, call this function multiple times
    """
    client = get_kendra_client()
    index_id = index_id or Config.KENDRA_INDEX_ID

    # Call the batch_delete_document API
    # Note the parameter name is "DocumentIdList", not "DocumentIds"
    response = client.batch_delete_document(
        IndexId=index_id,
        DocumentIdList=document_ids,  # List of IDs to delete
    )

    print(f"Deleted {len(document_ids)} documents")
    return response


def create_s3_data_source(
    name: str,
    bucket_name: str,
    inclusion_prefixes: list = None,
    index_id: str = None,
) -> dict:
    """
    Create an S3 data source for automatic document ingestion.

    WHAT THIS FUNCTION DOES:
    ------------------------
    Sets up a connection between your S3 bucket and Kendra index.
    Once configured, Kendra can automatically crawl your bucket
    and index all supported documents.

    DATA SOURCE VS BATCH PUT:
    -------------------------
    BatchPutDocument:              S3 Data Source:
    - You send content directly    - Kendra reads from S3
    - Good for small batches       - Good for large collections
    - Manual updates               - Automatic syncing
    - Any content source           - Documents must be in S3

    HOW S3 DATA SOURCES WORK:
    -------------------------
    1. You create a data source pointing to an S3 bucket
    2. Kendra uses the IAM role to access the bucket
    3. You start a "sync job" to crawl the bucket
    4. Kendra extracts text from supported file types
    5. Documents are indexed and searchable
    6. Re-run sync to pick up new/modified/deleted files

    SUPPORTED FILE TYPES IN S3:
    ---------------------------
    - Plain text (.txt)
    - HTML (.html, .htm)
    - PDF (.pdf)
    - Microsoft Word (.doc, .docx)
    - Microsoft PowerPoint (.ppt, .pptx)
    - Microsoft Excel (.xls, .xlsx) - for structured data

    Args:
        name (str): A name for this data source.
                   Example: "Company-Docs-S3", "HR-Policies-Bucket"
                   This appears in the AWS Console.

        bucket_name (str): The S3 bucket name (NOT the full ARN or URL).
                          Example: "my-company-documents"
                          NOT: "s3://my-company-documents"
                          NOT: "arn:aws:s3:::my-company-documents"

        inclusion_prefixes (list, optional): List of S3 key prefixes to include.
                          Only objects with these prefixes will be indexed.
                          Example: ["documents/", "policies/hr/"]
                          If None, entire bucket is indexed.

        index_id (str, optional): Which index to add this data source to.

    Returns:
        dict: Response containing:
            {
                'Id': 'ds-abc123...',  # Data source ID (needed for sync)
                'ResponseMetadata': {...}
            }

    EXAMPLE USAGE:
    --------------
    >>> # Index entire bucket
    >>> response = create_s3_data_source(
    ...     name="All-Company-Docs",
    ...     bucket_name="my-company-bucket"
    ... )
    >>> data_source_id = response['Id']

    >>> # Index only specific folders
    >>> response = create_s3_data_source(
    ...     name="HR-Policies",
    ...     bucket_name="my-company-bucket",
    ...     inclusion_prefixes=["hr/policies/", "hr/procedures/"]
    ... )

    IAM ROLE REQUIREMENTS:
    ----------------------
    The KENDRA_ROLE_ARN must have permissions to:
    - s3:GetObject on the bucket objects
    - s3:ListBucket on the bucket
    - kms:Decrypt if the bucket is encrypted

    Example IAM policy for the role:
    {
        "Effect": "Allow",
        "Action": ["s3:GetObject"],
        "Resource": "arn:aws:s3:::my-bucket/*"
    },
    {
        "Effect": "Allow",
        "Action": ["s3:ListBucket"],
        "Resource": "arn:aws:s3:::my-bucket"
    }
    """
    client = get_kendra_client()
    index_id = index_id or Config.KENDRA_INDEX_ID

    # Build the S3 configuration object
    s3_config = {
        # The bucket containing your documents
        "BucketName": bucket_name,
    }

    # Optionally restrict which objects to index
    # This is useful for large buckets where you only want certain folders
    if inclusion_prefixes:
        s3_config["InclusionPrefixes"] = inclusion_prefixes
        # You can also use ExclusionPrefixes to skip certain folders
        # Example: "InclusionPrefixes": ["docs/"], "ExclusionPrefixes": ["docs/archive/"]

    # Create the data source
    response = client.create_data_source(
        IndexId=index_id,           # Which index this data source belongs to
        Name=name,                   # Human-readable name
        Type="S3",                   # Data source type (S3, SHAREPOINT, etc.)
        Configuration={
            "S3Configuration": s3_config  # S3-specific settings
        },
        RoleArn=Config.KENDRA_ROLE_ARN,  # IAM role for accessing S3
    )

    print(f"Data source created. ID: {response['Id']}")
    print("Note: Call sync_data_source() to start indexing documents.")
    return response


def sync_data_source(data_source_id: str, index_id: str = None) -> dict:
    """
    Start a sync job for a data source.

    WHAT THIS FUNCTION DOES:
    ------------------------
    Triggers Kendra to crawl the data source and index all documents.
    This is how you get documents from S3 (or other sources) into Kendra.

    SYNC JOB PROCESS:
    -----------------
    1. You call this function to start a sync
    2. Kendra begins crawling the data source
    3. For each document found:
       a. Download the file
       b. Extract text (OCR for images in PDFs, etc.)
       c. Index the content
    4. Track new, modified, and deleted documents
    5. Update the index accordingly

    SYNC BEHAVIOR:
    --------------
    - First sync: Indexes ALL documents
    - Subsequent syncs: Only processes changes (incremental)
    - Deleted files: Removed from index
    - Modified files: Re-indexed

    SYNC DURATION:
    --------------
    Depends on document count and size:
    - 100 documents: A few minutes
    - 10,000 documents: 30+ minutes
    - 100,000 documents: Several hours

    You can monitor sync status via:
    - AWS Console
    - describe_data_source_sync_job() API
    - CloudWatch metrics

    Args:
        data_source_id (str): The data source ID returned from create_s3_data_source()
                             Format: "ds-abc123..." or full ARN

        index_id (str, optional): Which index the data source belongs to.

    Returns:
        dict: Response containing:
            {
                'ExecutionId': 'exec-xyz789...',  # Unique ID for this sync job
                'ResponseMetadata': {...}
            }

    EXAMPLE USAGE:
    --------------
    >>> # Start a sync job
    >>> response = sync_data_source("ds-abc123...")
    Sync started. Execution ID: exec-xyz789...

    >>> # You can monitor the sync with:
    >>> # client.describe_data_source_sync_job(
    >>> #     Id=data_source_id,
    >>> #     IndexId=index_id
    >>> # )

    SCHEDULING SYNCS:
    -----------------
    For production, you typically want automatic syncs.
    You can configure a schedule when creating the data source:

    >>> client.create_data_source(
    ...     ...,
    ...     Schedule="cron(0 12 * * ? *)"  # Sync daily at noon UTC
    ... )

    Schedule format: cron() or rate() expressions
    - cron(0 12 * * ? *)  = Every day at 12:00 UTC
    - rate(1 day)         = Every 24 hours
    - rate(2 hours)       = Every 2 hours
    """
    client = get_kendra_client()
    index_id = index_id or Config.KENDRA_INDEX_ID

    # Start the sync job
    # This is asynchronous - returns immediately, sync runs in background
    response = client.start_data_source_sync_job(
        Id=data_source_id,   # Which data source to sync
        IndexId=index_id,    # Which index it belongs to
    )

    print(f"Sync started. Execution ID: {response['ExecutionId']}")
    print("Note: Sync runs in background. Check status in AWS Console or via API.")
    return response


# =============================================================================
# LEARNING EXERCISES:
# =============================================================================
#
# EXERCISE 1: Add documents and search
# ------------------------------------
# >>> from src.document_manager import add_documents
# >>> from src.search import search_and_print
# >>>
# >>> # Create some test documents
# >>> docs = [
# ...     {
# ...         "Id": "test-001",
# ...         "Title": "Python Basics",
# ...         "Content": "Python is a programming language known for its simplicity."
# ...     },
# ...     {
# ...         "Id": "test-002",
# ...         "Title": "JavaScript Guide",
# ...         "Content": "JavaScript is used for web development and runs in browsers."
# ...     }
# ... ]
# >>>
# >>> # Add them to Kendra
# >>> add_documents(docs)
# >>>
# >>> # Wait a minute for indexing, then search
# >>> import time
# >>> time.sleep(60)
# >>> search_and_print("What is Python?")
#
#
# EXERCISE 2: Using document attributes for filtering
# ---------------------------------------------------
# >>> docs_with_attrs = [
# ...     {
# ...         "Id": "hr-policy-001",
# ...         "Title": "Vacation Policy",
# ...         "Content": "Employees get 15 days of vacation per year.",
# ...         "Attributes": [
# ...             {"Key": "_category", "Value": {"StringValue": "HR"}}
# ...         ]
# ...     },
# ...     {
# ...         "Id": "it-policy-001",
# ...         "Title": "Password Policy",
# ...         "Content": "Passwords must be 12 characters minimum.",
# ...         "Attributes": [
# ...             {"Key": "_category", "Value": {"StringValue": "IT"}}
# ...         ]
# ...     }
# ... ]
# >>> add_documents(docs_with_attrs)
# >>>
# >>> # Now you can filter searches by category!
# >>> # (requires setting up attribute in index configuration)
#
#
# COMMON ERRORS AND SOLUTIONS:
# ----------------------------
#
# ValidationException - Document content too large:
#   - Max 5MB per document, 50MB total per batch
#   - Split large documents or use S3 data source
#
# InvalidDocumentException - Unsupported content:
#   - Check ContentType matches actual content
#   - Ensure content is valid UTF-8
#
# ThrottlingException - Too many requests:
#   - Kendra has rate limits
#   - Add delays between batch calls
#   - Use S3 data source for bulk imports
#
# ResourceNotFoundException - Index not found:
#   - Check index_id is correct
#   - Verify index exists and is ACTIVE
#
# AccessDeniedException:
#   - IAM role lacks required permissions
#   - Check CloudWatch Logs and S3 permissions
#
# =============================================================================


# =============================================================================
# ADVANCED TOPIC: Document Access Control Lists (ACLs)
# =============================================================================
# Kendra supports document-level access control:
#
# >>> doc_with_acl = {
# ...     "Id": "confidential-001",
# ...     "Title": "Salary Information",
# ...     "Content": "Executive salaries...",
# ...     "AccessControlList": [
# ...         {
# ...             "Name": "HR-Team",      # Group name
# ...             "Type": "GROUP",
# ...             "Access": "ALLOW"
# ...         },
# ...         {
# ...             "Name": "john@company.com",  # User email
# ...             "Type": "USER",
# ...             "Access": "ALLOW"
# ...         }
# ...     ]
# ... }
#
# When querying, you pass the user's identity and groups.
# Kendra only returns documents the user has access to.
# This requires additional setup with AWS IAM Identity Center or similar.
# =============================================================================
