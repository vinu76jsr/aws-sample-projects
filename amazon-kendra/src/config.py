"""
Configuration Module for Amazon Kendra Sample Project
======================================================

WHAT THIS MODULE DOES:
This module handles loading configuration from environment variables.
It uses the python-dotenv library to read values from a .env file.

WHY USE ENVIRONMENT VARIABLES?
------------------------------
1. Security: Sensitive data (API keys, credentials) should NEVER be hardcoded
   in source code. If you commit credentials to Git, they become public!

2. Flexibility: Different environments (dev, staging, production) need
   different configurations. Environment variables let you change settings
   without modifying code.

3. Best Practice: The "12-Factor App" methodology recommends storing config
   in environment variables for cloud-native applications.

HOW python-dotenv WORKS:
------------------------
1. Create a .env file in your project root (never commit this to Git!)
2. Add key-value pairs: AWS_REGION=us-east-1
3. Call load_dotenv() to read .env and set environment variables
4. Use os.getenv() to retrieve values

LEARNING TIP:
Always provide a .env.example file (committed to Git) showing required
variables WITHOUT actual values, so other developers know what to configure.
"""

import os
from dotenv import load_dotenv

# load_dotenv() reads the .env file and loads its contents into os.environ
# This must be called BEFORE accessing any environment variables
# It searches for .env in the current directory and parent directories
load_dotenv()


class Config:
    """
    Configuration class containing all application settings.

    WHY USE A CLASS?
    ----------------
    Using a class (instead of module-level variables) provides:
    - Namespace: All config is accessed as Config.SETTING_NAME
    - Organization: Related settings are grouped together
    - IDE Support: Better autocomplete and type hints
    - Testing: Easy to mock or replace for unit tests

    PATTERN: This is a "Settings" or "Config" class pattern common in Python.
    """

    # ==========================================================================
    # AWS REGION CONFIGURATION
    # ==========================================================================
    # os.getenv(name, default) retrieves an environment variable
    # If not found, it returns the default value (second argument)
    #
    # us-east-1 is the default because:
    # 1. It's often the most feature-complete AWS region
    # 2. Many AWS tutorials and docs use it as the example
    # 3. Kendra was first launched in us-east-1
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

    # ==========================================================================
    # KENDRA INDEX ID
    # ==========================================================================
    # A Kendra Index is like a search database. Each index:
    # - Has a unique ID (UUID format like "abc123-def4-5678-...")
    # - Stores documents that can be searched
    # - Has its own settings, data sources, and query capacity
    #
    # You get this ID when you create an index via AWS Console or API
    # No default value - this MUST be provided for search to work
    KENDRA_INDEX_ID = os.getenv("KENDRA_INDEX_ID")

    # ==========================================================================
    # IAM ROLE ARN FOR KENDRA
    # ==========================================================================
    # ARN = Amazon Resource Name - a unique identifier for any AWS resource
    # Format: arn:aws:service:region:account:resource
    # Example: arn:aws:iam::123456789012:role/KendraRole
    #
    # WHY DOES KENDRA NEED A ROLE?
    # ----------------------------
    # Kendra needs permissions to:
    # 1. Access CloudWatch Logs (for logging and monitoring)
    # 2. Read from S3 buckets (if using S3 as a data source)
    # 3. Access other data sources (SharePoint, databases, etc.)
    #
    # The IAM role grants these permissions using AWS's security model.
    # This is called "AssumeRole" - Kendra assumes this role's permissions.
    #
    # Required for: Creating indexes and data sources
    KENDRA_ROLE_ARN = os.getenv("KENDRA_ROLE_ARN")

    # ==========================================================================
    # S3 BUCKET NAME (OPTIONAL)
    # ==========================================================================
    # Amazon S3 (Simple Storage Service) stores files in "buckets"
    # A bucket is like a top-level folder with a globally unique name
    #
    # Bucket naming rules:
    # - 3-63 characters long
    # - Only lowercase letters, numbers, and hyphens
    # - Must be globally unique across ALL AWS accounts
    # - Cannot start with "xn--" or end with "-s3alias"
    #
    # This is optional because you can add documents to Kendra directly
    # via the BatchPutDocument API without using S3.
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")


# =============================================================================
# LEARNING EXERCISE:
# =============================================================================
# Try these commands in Python to understand how config loading works:
#
# >>> from src.config import Config
# >>> print(Config.AWS_REGION)       # Should print "us-east-1" or your value
# >>> print(Config.KENDRA_INDEX_ID)  # None if not set, or your index ID
#
# >>> import os
# >>> print(os.environ.get("PATH"))  # See other environment variables
# =============================================================================
