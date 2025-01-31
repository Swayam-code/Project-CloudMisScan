import boto3
import json
import logging
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_logging_bucket(s3_client, account_id, region):
    """Create a logging bucket in the same region"""
    try:
        logging_bucket = f'cloudmisscan-logs-{account_id}'
        
        # Create the logging bucket
        if region == 'eu-north-1':
            s3_client.create_bucket(
                Bucket=logging_bucket,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        else:
            # For us-east-1, don't specify LocationConstraint
            s3_client.create_bucket(Bucket=logging_bucket)
        
        # Add bucket policy for logging
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "S3ServerAccessLogsPolicy",
                    "Effect": "Allow",
                    "Principal": {"Service": "logging.s3.amazonaws.com"},
                    "Action": [
                        "s3:PutObject"
                    ],
                    "Resource": f"arn:aws:s3:::{logging_bucket}/*"
                }
            ]
        }
        
        s3_client.put_bucket_policy(
            Bucket=logging_bucket,
            Policy=json.dumps(policy)
        )
        
        # Enable versioning
        s3_client.put_bucket_versioning(
            Bucket=logging_bucket,
            VersioningConfiguration={'Status': 'Enabled'}
        )
        
        logger.info(f"Created logging bucket: {logging_bucket}")
        return logging_bucket
    except ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyExists':
            logger.info(f"Logging bucket already exists: {logging_bucket}")
            return logging_bucket
        else:
            logger.error(f"Failed to create logging bucket: {str(e)}")
            raise

def enable_bucket_logging(s3_client, bucket_name, logging_bucket):
    """Enable logging for a bucket"""
    try:
        s3_client.put_bucket_logging(
            Bucket=bucket_name,
            BucketLoggingStatus={
                'LoggingEnabled': {
                    'TargetBucket': logging_bucket,
                    'TargetPrefix': f'logs/{bucket_name}/'
                }
            }
        )
        logger.info(f"Enabled logging for bucket: {bucket_name}")
        return True
    except ClientError as e:
        logger.error(f"Failed to enable logging for bucket {bucket_name}: {str(e)}")
        return False

def main():
    """Set up S3 logging"""
    try:
        session = boto3.Session()
        s3_client = session.client('s3')
        sts_client = session.client('sts')
        
        # Get account ID and region
        account_id = sts_client.get_caller_identity()['Account']
        region = session.region_name or 'eu-north-1'  # Default to eu-north-1 if not set
        
        # Create logging bucket
        logging_bucket = create_logging_bucket(s3_client, account_id, region)
        
        # Get all test buckets
        buckets = s3_client.list_buckets()['Buckets']
        for bucket in buckets:
            if bucket['Name'].startswith('cloudmisscan-test-'):
                enable_bucket_logging(s3_client, bucket['Name'], logging_bucket)
        
        logger.info("S3 logging setup completed!")
        
    except Exception as e:
        logger.error(f"Failed to set up S3 logging: {str(e)}")

if __name__ == '__main__':
    main()
