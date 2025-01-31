import boto3
from botocore.exceptions import ClientError

def test_aws_connection():
    try:
        # Test S3 connection
        s3 = boto3.client('s3')
        s3.list_buckets()
        print("✅ Successfully connected to AWS S3")
        
        # Test EC2 connection
        ec2 = boto3.client('ec2')
        ec2.describe_instances()
        print("✅ Successfully connected to AWS EC2")
        
        # Test IAM connection
        iam = boto3.client('iam')
        iam.list_users()
        print("✅ Successfully connected to AWS IAM")
        
        # Test RDS connection
        rds = boto3.client('rds')
        rds.describe_db_instances()
        print("✅ Successfully connected to AWS RDS")
        
        print("\nAWS connection test completed successfully! ✨")
        return True
        
    except ClientError as e:
        print(f"\n❌ AWS Connection Error: {str(e)}")
        print("\nPlease check:")
        print("1. Your AWS credentials are correctly set")
        print("2. The IAM user has the required permissions")
        print("3. Your AWS region is correctly configured")
        return False

if __name__ == "__main__":
    test_aws_connection()
