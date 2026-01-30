"""
S3 Data Lake Setup for ML Workflows

This script demonstrates setting up an S3-based data lake optimized for ML workloads.
It covers bucket configuration, security, lifecycle policies, and event notifications.

EXAM TIPS:
- Know storage classes and when to use each
- Understand encryption options (SSE-S3, SSE-KMS)
- Know lifecycle policies for cost optimization
- Understand S3 event triggers for ML automation
"""

import boto3
import json
from datetime import datetime


# Initialize clients
s3 = boto3.client('s3')
s3_resource = boto3.resource('s3')


def create_ml_data_lake(bucket_name: str, region: str = 'us-east-1'):
    """
    Create and configure an S3 bucket optimized for ML data lake.

    EXAM TIP: Know the key configurations:
    - Versioning for model artifact tracking
    - Encryption for compliance
    - Lifecycle policies for cost optimization
    - Block public access for security
    """

    # 1. Create bucket
    if region == 'us-east-1':
        s3.create_bucket(Bucket=bucket_name)
    else:
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': region}
        )

    print(f"Created bucket: {bucket_name}")

    # 2. Enable versioning (IMPORTANT for ML - track model versions)
    s3.put_bucket_versioning(
        Bucket=bucket_name,
        VersioningConfiguration={'Status': 'Enabled'}
    )
    print("Enabled versioning")

    # 3. Block public access (SECURITY BEST PRACTICE)
    s3.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            'BlockPublicAcls': True,
            'IgnorePublicAcls': True,
            'BlockPublicPolicy': True,
            'RestrictPublicBuckets': True
        }
    )
    print("Blocked public access")

    # 4. Enable server-side encryption
    # EXAM TIP: SSE-S3 is simplest, SSE-KMS provides audit trail
    s3.put_bucket_encryption(
        Bucket=bucket_name,
        ServerSideEncryptionConfiguration={
            'Rules': [{
                'ApplyServerSideEncryptionByDefault': {
                    'SSEAlgorithm': 'AES256'  # SSE-S3
                },
                'BucketKeyEnabled': True  # Reduces KMS costs if using SSE-KMS
            }]
        }
    )
    print("Enabled default encryption (SSE-S3)")

    # 5. Add lifecycle policies
    configure_lifecycle_policies(bucket_name)

    # 6. Create folder structure
    create_data_lake_structure(bucket_name)

    return bucket_name


def configure_lifecycle_policies(bucket_name: str):
    """
    Configure lifecycle policies for ML data lake.

    EXAM TIP: Lifecycle policies help with:
    - Cost optimization (move to cheaper storage)
    - Compliance (retain data for required period)
    - Cleanup (delete temporary files)
    """

    lifecycle_policy = {
        'Rules': [
            # Rule 1: Archive old model artifacts
            {
                'ID': 'ArchiveOldModels',
                'Status': 'Enabled',
                'Filter': {'Prefix': 'models/'},
                'Transitions': [
                    {
                        'Days': 30,
                        'StorageClass': 'STANDARD_IA'  # Infrequent Access
                    },
                    {
                        'Days': 90,
                        'StorageClass': 'GLACIER_IR'  # Glacier Instant Retrieval
                    },
                    {
                        'Days': 365,
                        'StorageClass': 'GLACIER'  # Glacier Flexible
                    }
                ]
            },
            # Rule 2: Archive processed data
            {
                'ID': 'ArchiveProcessedData',
                'Status': 'Enabled',
                'Filter': {'Prefix': 'processed/'},
                'Transitions': [
                    {
                        'Days': 60,
                        'StorageClass': 'STANDARD_IA'
                    },
                    {
                        'Days': 180,
                        'StorageClass': 'GLACIER_IR'
                    }
                ]
            },
            # Rule 3: Delete temporary files
            {
                'ID': 'DeleteTempFiles',
                'Status': 'Enabled',
                'Filter': {'Prefix': 'temp/'},
                'Expiration': {'Days': 7}
            },
            # Rule 4: Delete old versions
            {
                'ID': 'DeleteOldVersions',
                'Status': 'Enabled',
                'Filter': {'Prefix': ''},
                'NoncurrentVersionExpiration': {'NoncurrentDays': 90}
            },
            # Rule 5: Abort incomplete multipart uploads
            {
                'ID': 'AbortIncompleteMultipartUploads',
                'Status': 'Enabled',
                'Filter': {'Prefix': ''},
                'AbortIncompleteMultipartUpload': {'DaysAfterInitiation': 7}
            }
        ]
    }

    s3.put_bucket_lifecycle_configuration(
        Bucket=bucket_name,
        LifecycleConfiguration=lifecycle_policy
    )
    print("Configured lifecycle policies")


def create_data_lake_structure(bucket_name: str):
    """
    Create standard folder structure for ML data lake.

    EXAM TIP: Organized structure enables:
    - Better governance
    - Easier access control with S3 Access Points
    - Efficient queries with Athena/Glue
    """

    folders = [
        'raw/',                    # Raw ingested data (Bronze layer)
        'processed/',              # Cleaned/transformed data (Silver layer)
        'features/',               # Feature store exports (Gold layer)
        'models/',                 # Model artifacts
        'models/production/',      # Production models
        'models/staging/',         # Staging models
        'models/archived/',        # Archived models
        'predictions/',            # Batch prediction outputs
        'experiments/',            # Experiment tracking data
        'temp/',                   # Temporary files (auto-deleted)
        'logs/',                   # Processing logs
    ]

    for folder in folders:
        s3.put_object(Bucket=bucket_name, Key=folder)

    print(f"Created {len(folders)} folders")


def configure_event_notifications(bucket_name: str, lambda_arn: str = None):
    """
    Configure S3 event notifications for ML automation.

    EXAM TIP: S3 events can trigger:
    - Lambda functions (processing, validation)
    - SQS queues (decoupled processing)
    - SNS topics (fan-out notifications)
    - EventBridge (complex routing)
    """

    # Example: Notify when new training data is uploaded
    notification_config = {
        'LambdaFunctionConfigurations': [
            {
                'LambdaFunctionArn': lambda_arn or 'arn:aws:lambda:region:account:function:name',
                'Events': ['s3:ObjectCreated:*'],
                'Filter': {
                    'Key': {
                        'FilterRules': [
                            {'Name': 'prefix', 'Value': 'raw/'},
                            {'Name': 'suffix', 'Value': '.csv'}
                        ]
                    }
                }
            }
        ]
    }

    # Uncomment to apply (requires Lambda permission)
    # s3.put_bucket_notification_configuration(
    #     Bucket=bucket_name,
    #     NotificationConfiguration=notification_config
    # )

    print("Event notification configuration prepared")
    return notification_config


def upload_training_data(bucket_name: str, local_path: str, s3_prefix: str):
    """
    Upload training data to S3 with optimized settings.

    EXAM TIP: Use multipart upload for large files (>100MB)
    """

    from boto3.s3.transfer import TransferConfig

    # Configure multipart upload
    config = TransferConfig(
        multipart_threshold=100 * 1024 * 1024,  # 100MB
        max_concurrency=10,
        multipart_chunksize=100 * 1024 * 1024,
        use_threads=True
    )

    s3_key = f"{s3_prefix}/{local_path.split('/')[-1]}"

    s3.upload_file(
        Filename=local_path,
        Bucket=bucket_name,
        Key=s3_key,
        Config=config,
        ExtraArgs={
            'Metadata': {
                'uploaded-at': datetime.utcnow().isoformat(),
                'source': 'training-pipeline'
            }
        }
    )

    print(f"Uploaded {local_path} to s3://{bucket_name}/{s3_key}")
    return f"s3://{bucket_name}/{s3_key}"


def create_s3_access_point(bucket_name: str, access_point_name: str, vpc_id: str = None):
    """
    Create S3 Access Point for simplified access management.

    EXAM TIP: Access Points provide:
    - Simplified permissions for different teams/applications
    - Network controls (VPC-only access)
    - Own DNS name for the access point
    """

    s3control = boto3.client('s3control')
    account_id = boto3.client('sts').get_caller_identity()['Account']

    access_point_config = {
        'AccountId': account_id,
        'Name': access_point_name,
        'Bucket': bucket_name,
        'PublicAccessBlockConfiguration': {
            'BlockPublicAcls': True,
            'IgnorePublicAcls': True,
            'BlockPublicPolicy': True,
            'RestrictPublicBuckets': True
        }
    }

    # Add VPC configuration if provided
    if vpc_id:
        access_point_config['VpcConfiguration'] = {'VpcId': vpc_id}

    # Uncomment to create (requires proper permissions)
    # s3control.create_access_point(**access_point_config)

    print(f"Access point configuration prepared: {access_point_name}")
    return access_point_config


def get_bucket_metrics(bucket_name: str):
    """
    Get storage metrics for the bucket.

    Useful for monitoring data growth and optimizing costs.
    """

    cloudwatch = boto3.client('cloudwatch')

    # Get bucket size metric
    response = cloudwatch.get_metric_statistics(
        Namespace='AWS/S3',
        MetricName='BucketSizeBytes',
        Dimensions=[
            {'Name': 'BucketName', 'Value': bucket_name},
            {'Name': 'StorageType', 'Value': 'StandardStorage'}
        ],
        StartTime=datetime.utcnow().replace(hour=0, minute=0, second=0),
        EndTime=datetime.utcnow(),
        Period=86400,
        Statistics=['Average']
    )

    if response['Datapoints']:
        size_bytes = response['Datapoints'][0]['Average']
        size_gb = size_bytes / (1024 ** 3)
        print(f"Bucket size: {size_gb:.2f} GB")
        return size_gb

    return 0


def generate_presigned_url(bucket_name: str, object_key: str, expiration: int = 3600):
    """
    Generate a presigned URL for temporary access.

    EXAM TIP: Presigned URLs provide:
    - Temporary access without credentials
    - Time-limited access (default 1 hour, max 7 days with IAM user)
    - Useful for sharing data with external parties
    """

    url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket_name, 'Key': object_key},
        ExpiresIn=expiration
    )

    print(f"Generated presigned URL (expires in {expiration}s)")
    return url


# ============================================================================
# IAM Policy Examples
# ============================================================================

def get_sagemaker_s3_policy(bucket_name: str) -> dict:
    """
    Generate IAM policy for SageMaker to access S3.

    EXAM TIP: SageMaker needs:
    - s3:GetObject for reading training data
    - s3:PutObject for saving model artifacts
    - s3:ListBucket for listing objects
    """

    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "S3ReadWriteAccess",
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:DeleteObject"
                ],
                "Resource": [
                    f"arn:aws:s3:::{bucket_name}/*"
                ]
            },
            {
                "Sid": "S3ListAccess",
                "Effect": "Allow",
                "Action": [
                    "s3:ListBucket",
                    "s3:GetBucketLocation"
                ],
                "Resource": [
                    f"arn:aws:s3:::{bucket_name}"
                ]
            }
        ]
    }

    return policy


def get_ml_data_lake_bucket_policy(bucket_name: str, sagemaker_role_arn: str) -> dict:
    """
    Generate bucket policy for ML data lake.

    EXAM TIP: Bucket policies can:
    - Restrict access to specific IAM roles
    - Require encryption
    - Enforce HTTPS only
    """

    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AllowSageMakerAccess",
                "Effect": "Allow",
                "Principal": {
                    "AWS": sagemaker_role_arn
                },
                "Action": [
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:ListBucket"
                ],
                "Resource": [
                    f"arn:aws:s3:::{bucket_name}",
                    f"arn:aws:s3:::{bucket_name}/*"
                ]
            },
            {
                "Sid": "DenyUnencryptedUploads",
                "Effect": "Deny",
                "Principal": "*",
                "Action": "s3:PutObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/*",
                "Condition": {
                    "Null": {
                        "s3:x-amz-server-side-encryption": "true"
                    }
                }
            },
            {
                "Sid": "DenyHTTP",
                "Effect": "Deny",
                "Principal": "*",
                "Action": "s3:*",
                "Resource": [
                    f"arn:aws:s3:::{bucket_name}",
                    f"arn:aws:s3:::{bucket_name}/*"
                ],
                "Condition": {
                    "Bool": {
                        "aws:SecureTransport": "false"
                    }
                }
            }
        ]
    }

    return policy


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("S3 Data Lake Setup for ML")
    print("=" * 50)
    print("\nThis script demonstrates S3 configuration for ML workloads.")
    print("\nKey concepts covered:")
    print("1. Bucket creation with security best practices")
    print("2. Versioning for model artifact tracking")
    print("3. Encryption (SSE-S3, SSE-KMS)")
    print("4. Lifecycle policies for cost optimization")
    print("5. Event notifications for ML automation")
    print("6. Access Points for simplified access control")
    print("7. IAM policies for SageMaker integration")

    # Example usage (uncomment to run):
    # create_ml_data_lake('my-ml-data-lake', 'us-east-1')
