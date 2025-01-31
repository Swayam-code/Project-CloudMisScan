from dotenv import load_dotenv
import boto3
import os
from services.network_scanner import NetworkScanner
from services.aws_scanner import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION
from pprint import pprint

def verify_aws_credentials():
    """Verify AWS credentials are working"""
    print("\nAWS Credentials:")
    print(f"Access Key ID: {AWS_ACCESS_KEY_ID[:4]}...")
    print(f"Secret Key: {AWS_SECRET_ACCESS_KEY[:4]}...")
    print(f"Region: {AWS_DEFAULT_REGION}")
    
    try:
        # Initialize AWS session
        session = boto3.Session(
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_DEFAULT_REGION
        )
        
        # Test S3 access
        s3 = session.client('s3')
        buckets = s3.list_buckets()
        print("\nS3 buckets:")
        for bucket in buckets['Buckets']:
            print(f"- {bucket['Name']}")
        
        # Test EC2/VPC access
        print("\nChecking VPC configuration...")
        ec2_client = session.client('ec2')
        vpcs = ec2_client.describe_vpcs()
        print("\nVPCs found:")
        for vpc in vpcs['Vpcs']:
            print(f"- VPC ID: {vpc['VpcId']}")
            print(f"  CIDR: {vpc['CidrBlock']}")
            print(f"  Is Default: {vpc.get('IsDefault', False)}")
            
            # Get Network ACLs for this VPC
            nacls = ec2_client.describe_network_acls(
                Filters=[{'Name': 'vpc-id', 'Values': [vpc['VpcId']]}]
            )
            print(f"  Network ACLs:")
            for nacl in nacls['NetworkAcls']:
                print(f"    - NACL ID: {nacl['NetworkAclId']}")
                print(f"      Is Default: {nacl.get('IsDefault', False)}")
                print(f"      Number of Rules: {len(nacl['Entries'])}")
        
        # Test Network Scanner
        print("\nTesting Network Scanner...")
        network_scanner = NetworkScanner(session)
        results = network_scanner.scan_network_acls()
        
        print("\nNetwork ACL Scan Results:")
        for result in results:
            print(f"\nResource ID: {result['resource_id']}")
            print(f"VPC ID: {result['vpc_id']}")
            print(f"Severity: {result['severity']}")
            print(f"Risk Score: {result['risk_score']}")
            print("\nMisconfigurations:")
            for issue in result['misconfigurations']:
                print(f"- {issue['type']}: {issue['description']}")
            
        print("\nAWS credentials and Network Scanner are working correctly!")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_aws_credentials()
