"""
Configuration for the Polls DynamoDB application.

DynamoDB Learning Notes:
------------------------
- DynamoDB is a fully managed NoSQL database
- It uses key-value and document data models
- Primary key can be simple (partition key) or composite (partition + sort key)
- Global Secondary Indexes (GSI) allow querying on non-primary key attributes
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # AWS Settings
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

    # DynamoDB Settings
    DYNAMODB_ENDPOINT = os.getenv("DYNAMODB_ENDPOINT")  # None for real AWS
    TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "polls")

    # Flask Settings
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG = os.getenv("FLASK_DEBUG", "true").lower() == "true"


config = Config()
