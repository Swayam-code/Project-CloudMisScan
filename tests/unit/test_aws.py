import boto3
import logging
import os
from dotenv import load_dotenv
from services.aws_scanner import AWSScanner
from services.compliance_checker import ComplianceChecker
from services.trend_analyzer import TrendAnalyzer
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

def test_aws_credentials():
    """Test if AWS credentials are properly configured"""
    logger.info("\n=== Testing AWS Credentials ===")
    load_dotenv()
    
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
    
    logger.info(f"Access Key exists: {bool(access_key)}")
    logger.info(f"Secret Key exists: {bool(secret_key)}")
    logger.info(f"Region: {region}")
    
    try:
        session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        sts = session.client('sts')
        identity = sts.get_caller_identity()
        logger.info(f"Successfully authenticated as: {identity['Arn']}")
        return session
    except Exception as e:
        logger.error(f"Failed to authenticate with AWS: {str(e)}")
        return None

def test_s3_access(session):
    """Test S3 bucket access"""
    logger.info("\n=== Testing S3 Access ===")
    try:
        s3 = session.client('s3')
        buckets = s3.list_buckets()['Buckets']
        logger.info(f"Successfully listed {len(buckets)} S3 buckets:")
        for bucket in buckets:
            logger.info(f"- {bucket['Name']}")
        return True
    except Exception as e:
        logger.error(f"Failed to access S3: {str(e)}")
        return False

def test_iam_access(session):
    """Test IAM access"""
    logger.info("\n=== Testing IAM Access ===")
    try:
        iam = session.client('iam')
        users = iam.list_users()['Users']
        logger.info(f"Successfully listed {len(users)} IAM users:")
        for user in users:
            logger.info(f"- {user['UserName']}")
        return True
    except Exception as e:
        logger.error(f"Failed to access IAM: {str(e)}")
        return False

def test_ec2_access(session):
    """Test EC2 access"""
    logger.info("\n=== Testing EC2 Access ===")
    try:
        ec2 = session.client('ec2')
        instances = ec2.describe_instances()['Reservations']
        total_instances = sum(len(r['Instances']) for r in instances)
        logger.info(f"Successfully listed {total_instances} EC2 instances")
        return True
    except Exception as e:
        logger.error(f"Failed to access EC2: {str(e)}")
        return False

def test_security_hub_access(session):
    """Test Security Hub access"""
    logger.info("\n=== Testing Security Hub Access ===")
    try:
        securityhub = session.client('securityhub')
        enabled = securityhub.get_enabled_standards()
        logger.info(f"Successfully accessed Security Hub")
        logger.info(f"Enabled standards: {json.dumps(enabled.get('StandardsSubscriptions', []), indent=2)}")
        return True
    except Exception as e:
        logger.error(f"Failed to access Security Hub: {str(e)}")
        return False

def test_scanner_components():
    """Test AWS Scanner components"""
    logger.info("\n=== Testing AWS Scanner Components ===")
    try:
        scanner = AWSScanner()
        logger.info("Successfully created AWSScanner")
        
        # Test compliance checker
        logger.info("\nTesting Compliance Checker:")
        compliance_data = scanner.compliance_checker.get_compliance_data()
        logger.info(f"CIS Score: {compliance_data['cis']['score']}%")
        logger.info(f"NIST Score: {compliance_data['nist']['score']}%")
        logger.info(f"PCI Score: {compliance_data['pci']['score']}%")
        
        # Test service scanning
        logger.info("\nTesting Service Scanning:")
        scan_results = scanner.scan_all_services()
        for service, results in scan_results.items():
            if isinstance(results, list):
                issues = sum(len(r.get('misconfigurations', [])) for r in results)
                logger.info(f"{service}: {len(results)} resources, {issues} issues")
        
        return True
    except Exception as e:
        logger.error(f"Scanner component test failed: {str(e)}")
        return False

def main():
    """Run all AWS tests"""
    logger.info("Starting AWS integration tests...")
    
    # Test AWS credentials
    session = test_aws_credentials()
    if not session:
        logger.error("Failed to authenticate with AWS. Please check your credentials.")
        return False
    
    # Test individual services
    services_ok = all([
        test_s3_access(session),
        test_iam_access(session),
        test_ec2_access(session),
        test_security_hub_access(session)
    ])
    
    if not services_ok:
        logger.error("One or more AWS services failed to respond. Please check permissions.")
        return False
    
    # Test scanner components
    if not test_scanner_components():
        logger.error("Scanner components test failed. Please check the logs.")
        return False
    
    logger.info("\n=== All tests completed successfully ===")
    return True

if __name__ == '__main__':
    main()
