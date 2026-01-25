"""
Index Manager Module - CRUD Operations for Kendra Indexes
==========================================================

WHAT THIS MODULE DOES:
This module provides functions to create, read, update, and delete (CRUD)
Amazon Kendra indexes. An index is the core component of Kendra - it's
where your searchable content lives.

WHAT IS A KENDRA INDEX?
-----------------------
Think of a Kendra index like a highly intelligent search database:

Traditional Database Search:
  User types: "vacation policy"
  Result: Documents containing the exact words "vacation" and "policy"

Kendra Index (ML-powered):
  User types: "How many days off do I get?"
  Result: "Full-time employees receive 15 vacation days per year." (from HR handbook)

A Kendra index stores:
- Document content (text extracted from PDFs, Word docs, HTML, etc.)
- Document metadata (title, author, date, custom attributes)
- ML models for understanding natural language
- Inverted indexes for fast retrieval

INDEX EDITIONS:
---------------
Kendra offers two editions:

1. DEVELOPER_EDITION:
   - Good for testing and small workloads
   - Limited to ~10,000 documents
   - Lower cost (but still not free!)
   - Up to 4,000 queries per day
   - Single availability zone (less redundant)

2. ENTERPRISE_EDITION:
   - Production workloads
   - Up to 100,000+ documents
   - Higher query capacity
   - Multi-AZ for high availability
   - Better SLA guarantees

COST WARNING:
Amazon Kendra is NOT cheap! As of 2024:
- Developer Edition: ~$810/month base + $0.40 per document/month
- Enterprise Edition: ~$1,008/hour + additional costs

Always delete indexes when not in use during learning!

INDEX LIFECYCLE:
----------------
1. CREATING: Index is being provisioned (can take 15-30+ minutes!)
2. ACTIVE: Index is ready to use
3. UPDATING: Index settings are being modified
4. DELETING: Index is being removed
5. FAILED: Something went wrong

You can only add documents and run queries when status is ACTIVE.
"""

from .kendra_client import get_kendra_client
from .config import Config


def create_index(name: str, description: str = "") -> dict:
    """
    Create a new Kendra index.

    WHAT THIS FUNCTION DOES:
    ------------------------
    Creates a new search index in Amazon Kendra. This is like setting up
    a new search engine for your documents.

    IMPORTANT TIMING NOTE:
    Creating an index is NOT instant! It typically takes 15-30 minutes
    because AWS needs to:
    1. Provision compute resources
    2. Set up machine learning models
    3. Initialize storage systems
    4. Configure networking

    The function returns immediately with an Index ID, but the index
    won't be usable until its status becomes "ACTIVE".

    Args:
        name (str): Human-readable name for the index.
                   Example: "HR-Knowledge-Base", "Product-Documentation"
                   This appears in the AWS Console for identification.

        description (str): Optional description explaining what this index
                          contains or its purpose.
                          Example: "Contains all HR policies and procedures"

    Returns:
        dict: Response from AWS containing:
            {
                'Id': 'abc123-def4-5678-...',  # Unique index identifier
                'ResponseMetadata': {...}      # AWS request metadata
            }

    EXAMPLE USAGE:
    --------------
    >>> response = create_index(
    ...     name="My-First-Index",
    ...     description="Learning Kendra with sample documents"
    ... )
    >>> index_id = response['Id']
    >>> print(f"Index created! ID: {index_id}")
    >>> # Now wait for status to become ACTIVE before adding documents
    """
    # Get a fresh Kendra client for this operation
    client = get_kendra_client()

    # Call the create_index API
    # Documentation: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/kendra.html#Kendra.Client.create_index
    response = client.create_index(
        # Name is required - used in AWS Console to identify this index
        Name=name,

        # Description is optional but helpful for documentation
        Description=description,

        # Edition determines capacity and cost
        # DEVELOPER_EDITION: For testing/development (cheaper but limited)
        # ENTERPRISE_EDITION: For production workloads (expensive but scalable)
        Edition="DEVELOPER_EDITION",  # Change to ENTERPRISE_EDITION for production

        # RoleArn: IAM role that Kendra assumes to access resources
        # This role needs permissions for CloudWatch Logs at minimum
        # If using S3 data sources, it also needs S3 read permissions
        RoleArn=Config.KENDRA_ROLE_ARN,
    )

    # Print confirmation - note that the index is NOT ready yet!
    print(f"Index creation initiated. Index ID: {response['Id']}")
    print("Note: Index creation takes 15-30 minutes. Check status with describe_index().")
    return response


def describe_index(index_id: str = None) -> dict:
    """
    Get detailed information about a Kendra index.

    WHAT THIS FUNCTION DOES:
    ------------------------
    Retrieves comprehensive information about an index, including:
    - Current status (CREATING, ACTIVE, UPDATING, etc.)
    - Configuration settings
    - Capacity information
    - Error messages (if any)

    This is essential for:
    1. Checking if a newly created index is ready
    2. Monitoring index health
    3. Getting configuration details
    4. Debugging issues

    Args:
        index_id (str, optional): The unique identifier of the index.
                                 If not provided, uses KENDRA_INDEX_ID from config.
                                 Format: UUID like "abc123-def4-5678-ghij-9012klmnopqr"

    Returns:
        dict: Comprehensive index information including:
            {
                'Id': 'abc123-...',
                'Name': 'My-Index',
                'Description': '...',
                'Status': 'ACTIVE',           # Current lifecycle state
                'Edition': 'DEVELOPER_EDITION',
                'RoleArn': 'arn:aws:iam::...',
                'CreatedAt': datetime(...),   # When created
                'UpdatedAt': datetime(...),   # Last modified
                'DocumentMetadataConfigurations': [...],  # Custom attributes
                'IndexStatistics': {
                    'FaqStatistics': {'IndexedQuestionAnswersCount': 0},
                    'TextDocumentStatistics': {'IndexedTextDocumentsCount': 5}
                },
                'ErrorMessage': '',           # Empty if no errors
                'CapacityUnits': {...},       # Provisioned capacity
                ...
            }

    EXAMPLE USAGE:
    --------------
    >>> # Check if index is ready
    >>> info = describe_index("abc123-def4-5678...")
    >>> if info['Status'] == 'ACTIVE':
    ...     print("Index is ready!")
    ... else:
    ...     print(f"Index status: {info['Status']}")

    POLLING FOR READINESS:
    ----------------------
    Here's a pattern to wait for an index to become active:

    >>> import time
    >>> while True:
    ...     info = describe_index(index_id)
    ...     if info['Status'] == 'ACTIVE':
    ...         break
    ...     elif info['Status'] == 'FAILED':
    ...         raise Exception(f"Index failed: {info['ErrorMessage']}")
    ...     print(f"Status: {info['Status']}, waiting...")
    ...     time.sleep(60)  # Check every minute
    """
    client = get_kendra_client()

    # Use provided index_id or fall back to config
    # The "or" operator returns the first truthy value
    # If index_id is None or empty string, it uses Config.KENDRA_INDEX_ID
    index_id = index_id or Config.KENDRA_INDEX_ID

    # Call the describe_index API
    response = client.describe_index(Id=index_id)
    return response


def list_indexes() -> list:
    """
    List all Kendra indexes in your AWS account.

    WHAT THIS FUNCTION DOES:
    ------------------------
    Returns a summary of all Kendra indexes in your account for the
    configured region. Useful for:
    - Discovering existing indexes
    - Getting index IDs
    - Quick status overview

    Note: This lists indexes in the configured region only.
    Indexes in other regions won't appear.

    Returns:
        list: List of index summary dictionaries, each containing:
            [
                {
                    'Name': 'My-Index',
                    'Id': 'abc123-...',
                    'Edition': 'DEVELOPER_EDITION',
                    'CreatedAt': datetime(...),
                    'UpdatedAt': datetime(...),
                    'Status': 'ACTIVE'
                },
                {...},
                ...
            ]

    Returns an empty list if no indexes exist.

    PAGINATION NOTE:
    ----------------
    The list_indices API is paginated. This simple implementation
    returns only the first page (up to 100 indexes). For accounts
    with many indexes, you'd need to handle pagination:

    >>> # Full pagination example:
    >>> all_indexes = []
    >>> next_token = None
    >>> while True:
    ...     if next_token:
    ...         response = client.list_indices(NextToken=next_token)
    ...     else:
    ...         response = client.list_indices()
    ...     all_indexes.extend(response['IndexConfigurationSummaryItems'])
    ...     next_token = response.get('NextToken')
    ...     if not next_token:
    ...         break

    EXAMPLE USAGE:
    --------------
    >>> indexes = list_indexes()
    >>> for idx in indexes:
    ...     print(f"{idx['Name']}: {idx['Status']}")
    """
    client = get_kendra_client()

    # Call the list_indices API (note: AWS API uses "indices" plural)
    response = client.list_indices()

    # Extract the list of indexes from the response
    # .get() with default [] handles case where key doesn't exist
    return response.get("IndexConfigurationSummaryItems", [])


def delete_index(index_id: str) -> dict:
    """
    Delete a Kendra index.

    WHAT THIS FUNCTION DOES:
    ------------------------
    Permanently removes a Kendra index and ALL its contents:
    - All indexed documents
    - All data source configurations
    - All FAQ content
    - Index settings and configurations

    THIS OPERATION IS IRREVERSIBLE!

    WHY DELETE INDEXES?
    -------------------
    1. Cost savings - Kendra charges whether you use it or not
    2. Clean up after testing/learning
    3. Recreate with different settings
    4. Remove unused resources

    DELETION PROCESS:
    -----------------
    Like creation, deletion is asynchronous:
    1. Function returns immediately
    2. Status changes to "DELETING"
    3. AWS removes all resources (can take several minutes)
    4. Index disappears from list_indexes()

    Args:
        index_id (str): The unique identifier of the index to delete.
                       This is REQUIRED - no default value for safety!
                       You must explicitly specify which index to delete.

    Returns:
        dict: AWS response metadata (mostly empty for delete operations):
            {
                'ResponseMetadata': {
                    'RequestId': '...',
                    'HTTPStatusCode': 200,
                    ...
                }
            }

    Raises:
        ClientError: If index doesn't exist or you lack permission

    SAFETY TIP:
    -----------
    Consider implementing a confirmation step in production:

    >>> def safe_delete_index(index_id):
    ...     info = describe_index(index_id)
    ...     print(f"About to delete: {info['Name']}")
    ...     confirm = input("Type 'DELETE' to confirm: ")
    ...     if confirm == 'DELETE':
    ...         return delete_index(index_id)
    ...     else:
    ...         print("Deletion cancelled")

    EXAMPLE USAGE:
    --------------
    >>> # Delete a specific index
    >>> delete_index("abc123-def4-5678-...")
    Index abc123-def4-5678-... deletion initiated

    >>> # Verify it's being deleted
    >>> info = describe_index("abc123-...")
    >>> print(info['Status'])  # Should be "DELETING"
    """
    client = get_kendra_client()

    # Call the delete_index API
    # Note: No confirmation dialog - this deletes immediately
    response = client.delete_index(Id=index_id)

    print(f"Index {index_id} deletion initiated")
    print("Note: Deletion takes several minutes to complete.")
    return response


# =============================================================================
# LEARNING EXERCISES:
# =============================================================================
#
# EXERCISE 1: Create and delete an index (watch the costs!)
# ---------------------------------------------------------
# >>> from src.index_manager import create_index, describe_index, delete_index
# >>> import time
# >>>
# >>> # Create an index
# >>> response = create_index("Test-Index", "My first Kendra index")
# >>> index_id = response['Id']
# >>>
# >>> # Poll until ready (this takes 15-30 minutes!)
# >>> while True:
# ...     info = describe_index(index_id)
# ...     print(f"Status: {info['Status']}")
# ...     if info['Status'] == 'ACTIVE':
# ...         break
# ...     time.sleep(60)
# >>>
# >>> # Don't forget to clean up!
# >>> delete_index(index_id)
#
#
# EXERCISE 2: Explore index details
# ---------------------------------
# >>> info = describe_index()
# >>> print(f"Name: {info['Name']}")
# >>> print(f"Status: {info['Status']}")
# >>> print(f"Documents indexed: {info['IndexStatistics']['TextDocumentStatistics']['IndexedTextDocumentsCount']}")
#
#
# COMMON ERRORS AND SOLUTIONS:
# ----------------------------
#
# ResourceNotFoundException:
#   - Index ID doesn't exist
#   - Check for typos or that the index wasn't deleted
#
# ValidationException:
#   - Invalid parameters (e.g., bad RoleArn format)
#   - Check ARN format: arn:aws:iam::ACCOUNT:role/ROLENAME
#
# AccessDeniedException:
#   - IAM permissions issue
#   - Ensure your credentials have kendra:* permissions
#
# ServiceQuotaExceededException:
#   - You've hit the limit on number of indexes
#   - Delete unused indexes or request a quota increase
#
# =============================================================================
