import boto3
import json
import logging
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_account_id():
    """Get AWS account ID"""
    sts = boto3.client('sts')
    return sts.get_caller_identity()['Account']

def apply_bucket_policy(bucket_name):
    """Apply security policy to S3 bucket"""
    try:
        s3 = boto3.client('s3')
        
        # Read policy template
        with open('bucket-policy.json', 'r') as f:
            policy = json.load(f)
        
        # Replace placeholder with actual bucket name
        policy_str = json.dumps(policy).replace('[BUCKET_NAME]', bucket_name)
        
        # Apply policy
        s3.put_bucket_policy(
            Bucket=bucket_name,
            Policy=policy_str
        )
        logger.info(f"Applied security policy to bucket: {bucket_name}")
        return True
    except ClientError as e:
        logger.error(f"Failed to apply policy to bucket {bucket_name}: {str(e)}")
        return False

def enable_bucket_logging(bucket_name):
    """Enable logging for S3 bucket"""
    try:
        s3 = boto3.client('s3')
        
        # Read logging config
        with open('logging.json', 'r') as f:
            logging_config = json.load(f)
        
        # Apply logging configuration
        s3.put_bucket_logging(
            Bucket=bucket_name,
            BucketLoggingStatus=logging_config
        )
        logger.info(f"Enabled logging for bucket: {bucket_name}")
        return True
    except ClientError as e:
        logger.error(f"Failed to enable logging for bucket {bucket_name}: {str(e)}")
        return False

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

def update_network_acl(acl_id):
    """Update Network ACL with secure rules"""
    try:
        ec2 = boto3.client('ec2')
        
        # Remove existing rules
        acl = ec2.describe_network_acls(NetworkAclIds=[acl_id])['NetworkAcls'][0]
        for entry in acl['Entries']:
            if not entry.get('RuleNumber') == 32767:  # Don't remove default deny rule
                ec2.delete_network_acl_entry(
                    NetworkAclId=acl_id,
                    RuleNumber=entry['RuleNumber'],
                    Egress=entry['Egress']
                )
        
        # Add secure inbound rules
        rules = [
            # Allow HTTP(S)
            {'port': 80, 'rule_num': 100},
            {'port': 443, 'rule_num': 110},
            # Allow SSH from specific range (replace with your IP)
            {'port': 22, 'rule_num': 120, 'cidr': '0.0.0.0/0'}  # Replace with specific IP
        ]
        
        for rule in rules:
            ec2.create_network_acl_entry(
                NetworkAclId=acl_id,
                RuleNumber=rule['rule_num'],
                Protocol='6',  # TCP
                RuleAction='allow',
                Egress=False,
                CidrBlock=rule.get('cidr', '0.0.0.0/0'),
                PortRange={
                    'From': rule['port'],
                    'To': rule['port']
                }
            )
        
        # Add tags
        ec2.create_tags(
            Resources=[acl_id],
            Tags=[
                {'Key': 'Name', 'Value': 'SecurityManagedACL'},
                {'Key': 'Environment', 'Value': 'Production'},
                {'Key': 'SecurityManaged', 'Value': 'True'}
            ]
        )
        
        logger.info(f"Updated Network ACL: {acl_id}")
        return True
    except ClientError as e:
        logger.error(f"Failed to update Network ACL {acl_id}: {str(e)}")
        return False

def main():
    """Apply all security fixes"""
    try:
        s3 = boto3.client('s3')
        
        # Get all S3 buckets
        buckets = s3.list_buckets()['Buckets']
        
        # Apply fixes to each bucket
        for bucket in buckets:
            bucket_name = bucket['Name']
            if bucket_name.startswith('cloudmisscan-test-'):
                logger.info(f"\nApplying fixes to bucket: {bucket_name}")
                enable_bucket_logging(bucket_name)
                enable_bucket_versioning(bucket_name)
                apply_bucket_policy(bucket_name)
        
        # Update Network ACL
        update_network_acl('acl-05de50acf02c27ab6')
        
        logger.info("\nSecurity fixes applied successfully!")
        
    except Exception as e:
        logger.error(f"Failed to apply security fixes: {str(e)}")

if __name__ == '__main__':
    main()
