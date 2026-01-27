"""
DynamoDB Connection and Table Setup.

DynamoDB Learning Notes:
------------------------
1. Table Design: We use a SINGLE-TABLE DESIGN pattern
   - This is a DynamoDB best practice for related entities
   - All data lives in one table with different item types
   - Partition Key (PK) and Sort Key (SK) are overloaded

2. Access Patterns:
   - Get all polls: Query where PK = "POLLS"
   - Get single poll: Query where PK = "POLL#<id>"
   - Get choices for poll: Query where PK = "POLL#<id>" and SK begins_with "CHOICE#"
   - Get poll metadata: Query where PK = "POLL#<id>" and SK = "METADATA"

3. Item Types:
   - Poll Index: PK="POLLS", SK="POLL#<id>" (for listing all polls)
   - Poll Metadata: PK="POLL#<id>", SK="METADATA"
   - Choice: PK="POLL#<id>", SK="CHOICE#<choice_id>"
"""

import boto3
from botocore.exceptions import ClientError
from config import config


def get_dynamodb_resource():
    """
    Get DynamoDB resource.

    Learning Note:
    - boto3.resource() provides a higher-level, object-oriented interface
    - boto3.client() provides a lower-level, service-oriented interface
    - Resource is easier for common operations, client gives more control
    """
    kwargs = {
        "region_name": config.AWS_REGION,
    }

    if config.DYNAMODB_ENDPOINT:
        kwargs["endpoint_url"] = config.DYNAMODB_ENDPOINT

    if config.AWS_ACCESS_KEY_ID:
        kwargs["aws_access_key_id"] = config.AWS_ACCESS_KEY_ID
        kwargs["aws_secret_access_key"] = config.AWS_SECRET_ACCESS_KEY

    return boto3.resource("dynamodb", **kwargs)


def get_dynamodb_client():
    """Get DynamoDB client for lower-level operations."""
    kwargs = {
        "region_name": config.AWS_REGION,
    }

    if config.DYNAMODB_ENDPOINT:
        kwargs["endpoint_url"] = config.DYNAMODB_ENDPOINT

    if config.AWS_ACCESS_KEY_ID:
        kwargs["aws_access_key_id"] = config.AWS_ACCESS_KEY_ID
        kwargs["aws_secret_access_key"] = config.AWS_SECRET_ACCESS_KEY

    return boto3.client("dynamodb", **kwargs)


def get_table():
    """Get the polls table."""
    dynamodb = get_dynamodb_resource()
    return dynamodb.Table(config.TABLE_NAME)


def create_table():
    """
    Create the polls table with single-table design.

    Learning Notes:
    ---------------
    1. KeySchema: Defines the primary key
       - HASH = Partition Key (required)
       - RANGE = Sort Key (optional, but we use it)

    2. AttributeDefinitions: Defines attribute types
       - S = String, N = Number, B = Binary
       - Only define attributes used in keys/indexes

    3. BillingMode:
       - PAY_PER_REQUEST: Pay for what you use (good for variable workloads)
       - PROVISIONED: Set read/write capacity units (good for predictable workloads)

    4. GlobalSecondaryIndex (GSI):
       - Allows querying on different attributes
       - Has its own partition and optional sort key
       - Eventually consistent by default
    """
    dynamodb = get_dynamodb_resource()

    try:
        table = dynamodb.create_table(
            TableName=config.TABLE_NAME,
            KeySchema=[
                {
                    "AttributeName": "PK",  # Partition Key
                    "KeyType": "HASH"
                },
                {
                    "AttributeName": "SK",  # Sort Key
                    "KeyType": "RANGE"
                }
            ],
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "SK", "AttributeType": "S"},
                {"AttributeName": "GSI1PK", "AttributeType": "S"},
                {"AttributeName": "GSI1SK", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    # GSI for listing all polls sorted by date
                    "IndexName": "GSI1",
                    "KeySchema": [
                        {"AttributeName": "GSI1PK", "KeyType": "HASH"},
                        {"AttributeName": "GSI1SK", "KeyType": "RANGE"},
                    ],
                    "Projection": {
                        "ProjectionType": "ALL"  # Include all attributes
                    },
                }
            ],
            BillingMode="PAY_PER_REQUEST",  # On-demand pricing
        )

        # Wait for table to be created
        table.meta.client.get_waiter("table_exists").wait(TableName=config.TABLE_NAME)
        print(f"Table '{config.TABLE_NAME}' created successfully!")
        return table

    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceInUseException":
            print(f"Table '{config.TABLE_NAME}' already exists.")
            return get_table()
        raise


def delete_table():
    """Delete the polls table."""
    dynamodb = get_dynamodb_resource()
    table = dynamodb.Table(config.TABLE_NAME)

    try:
        table.delete()
        table.meta.client.get_waiter("table_not_exists").wait(TableName=config.TABLE_NAME)
        print(f"Table '{config.TABLE_NAME}' deleted successfully!")
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            print(f"Table '{config.TABLE_NAME}' does not exist.")
        else:
            raise


def table_exists():
    """Check if table exists."""
    client = get_dynamodb_client()
    try:
        client.describe_table(TableName=config.TABLE_NAME)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            return False
        raise
