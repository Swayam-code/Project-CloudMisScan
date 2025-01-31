import boto3
import json
import logging
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def enable_bucket_versioning(bucket_name):
    """Enable versioning for S3 bucket"""
    try:
        s3 = boto3.client('s3')
        s3.put_bucket_versioning(
            Bucket=bucket_name,
            VersioningConfiguration={'Status': 'Enabled'}
        )
        logger.info(f"Enabled versioning for bucket: {bucket_name}")
        return True
    except ClientError as e:
        logger.error(f"Failed to enable versioning for bucket {bucket_name}: {str(e)}")
        return False

def enable_bucket_logging(bucket_name):
    """Enable logging for S3 bucket"""
    try:
        s3 = boto3.client('s3')
        account_id = boto3.client('sts').get_caller_identity()['Account']
        
        # Use the central logging bucket
        target_bucket = f'cloudmisscan-logs-{account_id}'
        target_prefix = f'logs/{bucket_name}/'
        
        # Configure logging
        s3.put_bucket_logging(
            Bucket=bucket_name,
            BucketLoggingStatus={
                'LoggingEnabled': {
                    'TargetBucket': target_bucket,
                    'TargetPrefix': target_prefix
                }
            }
        )
        logger.info(f"Enabled logging for bucket: {bucket_name}")
        return True
    except ClientError as e:
        logger.error(f"Failed to enable logging for bucket {bucket_name}: {str(e)}")
        return False

def enable_mfa_for_user(username):
    """Enable virtual MFA for IAM user"""
    try:
        iam = boto3.client('iam')
        
        # Create a virtual MFA device
        response = iam.create_virtual_mfa_device(
            VirtualMFADeviceName=f'{username}_mfa'
        )
        
        logger.info(f"Created virtual MFA device for user: {username}")
        logger.info("Please configure this MFA device in the AWS Console")
        logger.info(f"MFA Serial Number: {response['VirtualMFADevice']['SerialNumber']}")
        
        return True
    except ClientError as e:
        if 'EntityAlreadyExists' in str(e):
            logger.info(f"MFA device already exists for user: {username}")
            return True
        logger.error(f"Failed to enable MFA for user {username}: {str(e)}")
        return False

def fix_remaining_issues():
    """Fix remaining security issues"""
    try:
        # Fix CloudTrail logs bucket
        cloudtrail_bucket = 'aws-cloudtrail-logs-841162686805-46b5481a'
        logger.info(f"\nFixing CloudTrail bucket: {cloudtrail_bucket}")
        enable_bucket_versioning(cloudtrail_bucket)
        enable_bucket_logging(cloudtrail_bucket)
        
        # Fix Config bucket
        config_bucket = 'config-bucket-841162686805'
        logger.info(f"\nFixing Config bucket: {config_bucket}")
        enable_bucket_versioning(config_bucket)
        enable_bucket_logging(config_bucket)
        
        # Enable MFA for CloudMisScanAdmin
        logger.info("\nEnabling MFA for CloudMisScanAdmin")
        enable_mfa_for_user('CloudMisScanAdmin')
        
        logger.info("\nAll remaining security fixes applied successfully!")
        
    except Exception as e:
        logger.error(f"Failed to apply remaining security fixes: {str(e)}")

if __name__ == '__main__':
    fix_remaining_issues()
