import boto3
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def verify_security_changes():
    try:
        session = boto3.Session(
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        )
        
        iam = session.client('iam')
        s3 = session.client('s3')
        ec2 = session.client('ec2')
        
        # Check IAM Password Policy
        logger.info("Checking IAM Password Policy...")
        try:
            password_policy = iam.get_account_password_policy()
            policy = password_policy['PasswordPolicy']
            logger.info(f"✅ Password Policy verified:")
            logger.info(f"  - Minimum length: {policy.get('MinimumPasswordLength', 'N/A')}")
            logger.info(f"  - Requires symbols: {policy.get('RequireSymbols', 'N/A')}")
            logger.info(f"  - Requires numbers: {policy.get('RequireNumbers', 'N/A')}")
            logger.info(f"  - Expires in days: {policy.get('MaxPasswordAge', 'N/A')}")
        except Exception as e:
            logger.error(f"❌ Failed to verify password policy: {str(e)}")

        # Check S3 Bucket Security
        logger.info("\nChecking S3 Bucket Security...")
        try:
            buckets = s3.list_buckets()['Buckets']
            for bucket in buckets:
                bucket_name = bucket['Name']
                logger.info(f"\nBucket: {bucket_name}")
                
                # Check logging
                try:
                    logging_config = s3.get_bucket_logging(Bucket=bucket_name)
                    has_logging = 'LoggingEnabled' in logging_config
                    logger.info(f"  ✅ Logging: {'Enabled' if has_logging else 'Disabled'}")
                except Exception as e:
                    logger.error(f"  ❌ Failed to check logging: {str(e)}")
                
                # Check versioning
                try:
                    versioning = s3.get_bucket_versioning(Bucket=bucket_name)
                    status = versioning.get('Status', 'Disabled')
                    logger.info(f"  ✅ Versioning: {status}")
                except Exception as e:
                    logger.error(f"  ❌ Failed to check versioning: {str(e)}")
                
                # Check bucket policy
                try:
                    s3.get_bucket_policy(Bucket=bucket_name)
                    logger.info("  ✅ Bucket policy: Present")
                except s3.exceptions.NoSuchBucketPolicy:
                    logger.warning("  ⚠️ Bucket policy: Not configured")
                except Exception as e:
                    logger.error(f"  ❌ Failed to check bucket policy: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to check S3 buckets: {str(e)}")

        # Check Network ACL Rules
        logger.info("\nChecking Network ACL Rules...")
        try:
            nacls = ec2.describe_network_acls()['NetworkAcls']
            for nacl in nacls:
                nacl_id = nacl['NetworkAclId']
                logger.info(f"\nNetwork ACL: {nacl_id}")
                
                # Check inbound rules
                inbound_rules = [rule for rule in nacl['Entries'] if not rule['Egress']]
                logger.info("Inbound Rules:")
                for rule in inbound_rules:
                    logger.info(f"  - Rule {rule['RuleNumber']}: {rule['Protocol']} " + 
                              f"Port {rule.get('PortRange', {}).get('From', 'ALL')}-{rule.get('PortRange', {}).get('To', 'ALL')} " +
                              f"Action: {rule['RuleAction']}")
                
                # Verify specific ports (80, 443, 22)
                allowed_ports = {80, 443, 22}
                configured_ports = {rule.get('PortRange', {}).get('From') for rule in inbound_rules 
                                 if rule.get('PortRange')}
                missing_ports = allowed_ports - configured_ports
                if missing_ports:
                    logger.warning(f"  ⚠️ Missing rules for ports: {missing_ports}")
                else:
                    logger.info("  ✅ All required ports (80, 443, 22) are configured")
        except Exception as e:
            logger.error(f"Failed to check Network ACLs: {str(e)}")

    except Exception as e:
        logger.error(f"Failed to verify security changes: {str(e)}")

if __name__ == '__main__':
    verify_security_changes()
