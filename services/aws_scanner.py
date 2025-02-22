from typing import Dict, List, Any, Tuple
import boto3
import logging
import os
from datetime import datetime
from .network_scanner import NetworkScanner
from .compliance_checker import ComplianceChecker
from .export_handler import ExportHandler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AWSScanner:
    def __init__(self):
        try:
            self.session = boto3.Session(
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
            )
            self.risk_weights = {
                'public_access': 10.0,
                'encryption_disabled': 8.0,
                'logging_disabled': 6.0,
                'versioning_disabled': 4.0,
                'tags_missing': 2.0
            }
            self.s3_client = None
            self.iam_client = None
            self.securityhub_client = None
            self.ec2_client = None
            self.rds_client = None
            self.network_scanner = NetworkScanner(self.session)
            self.compliance_checker = ComplianceChecker(self.session)
            self.export_handler = ExportHandler()
            self._initialize_clients()
        except Exception as e:
            logging.error(f"Failed to initialize AWS Scanner: {str(e)}")
            raise
    
    def _initialize_clients(self):
        """Initialize AWS clients with proper error handling"""
        try:
            # Test AWS connection first
            sts = self.session.client('sts')
            identity = sts.get_caller_identity()
            logging.info(f"Authenticated as: {identity['Arn']}")
            
            # Initialize service clients
            self.s3_client = self.session.client('s3')
            self.iam_client = self.session.client('iam')
            self.securityhub_client = self.session.client('securityhub')
            self.ec2_client = self.session.client('ec2')
            self.rds_client = self.session.client('rds')
            
            # Test each service
            self.s3_client.list_buckets()
            self.iam_client.list_users()
            self.ec2_client.describe_instances()
            self.rds_client.describe_db_instances()
            
            logging.info("Successfully initialized and tested all AWS clients")
        except Exception as e:
            logging.error(f"Failed to initialize AWS clients: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            raise
    
    def calculate_risk_score(self, misconfigurations: List[Dict[str, Any]]) -> Tuple[float, str]:
        """Calculate risk score based on misconfigurations"""
        if not misconfigurations:
            return 0.0, 'LOW'
            
        total_score = 0.0
        for issue in misconfigurations:
            issue_type = issue['type']
            weight = self.risk_weights.get(issue_type, 1.0)
            total_score += weight
        
        # Normalize score to 0-10 range
        normalized_score = min(10.0, total_score)
        
        # Determine severity
        if normalized_score >= 8.0:
            severity = 'HIGH'
        elif normalized_score >= 5.0:
            severity = 'MEDIUM'
        else:
            severity = 'LOW'
        
        return normalized_score, severity
    
    def scan_s3_buckets(self) -> List[Dict[str, Any]]:
        """Scan S3 buckets for misconfigurations"""
        logging.info("Starting S3 bucket scan...")
        results = []
        
        try:
            buckets = self.s3_client.list_buckets()['Buckets']
            logging.info(f"Found {len(buckets)} S3 buckets")
            
            for bucket in buckets:
                bucket_name = bucket['Name']
                logging.info(f"Scanning bucket: {bucket_name}")
                misconfigurations = []
                
                try:
                    # Check public access
                    public_access = self.s3_client.get_public_access_block(Bucket=bucket_name)
                    if not all(public_access['PublicAccessBlockConfiguration'].values()):
                        misconfigurations.append({
                            'type': 'public_access',
                            'severity': 'HIGH',
                            'description': 'Bucket has public access enabled'
                        })
                except Exception as e:
                    logging.warning(f"Could not check public access for {bucket_name}: {str(e)}")
                
                try:
                    # Check encryption
                    encryption = self.s3_client.get_bucket_encryption(Bucket=bucket_name)
                except self.s3_client.exceptions.ClientError as e:
                    if 'ServerSideEncryptionConfigurationNotFoundError' in str(e):
                        misconfigurations.append({
                            'type': 'encryption_disabled',
                            'severity': 'HIGH',
                            'description': 'Bucket encryption not enabled'
                        })
                except Exception as e:
                    logging.warning(f"Could not check encryption for {bucket_name}: {str(e)}")
                
                try:
                    # Check versioning with proper status check
                    versioning = self.s3_client.get_bucket_versioning(Bucket=bucket_name)
                    versioning_status = versioning.get('Status', '')
                    if versioning_status.lower() != 'enabled':
                        misconfigurations.append({
                            'type': 'versioning_disabled',
                            'severity': 'MEDIUM',
                            'description': 'Bucket versioning not enabled'
                        })
                except Exception as e:
                    logging.warning(f"Could not check versioning for {bucket_name}: {str(e)}")
                
                try:
                    # Check logging with proper configuration check
                    logging_config = self.s3_client.get_bucket_logging(Bucket=bucket_name)
                    if 'LoggingEnabled' not in logging_config or not logging_config['LoggingEnabled']:
                        # Skip logging check for the central logging bucket
                        if not bucket_name.endswith('-logs-841162686805'):
                            misconfigurations.append({
                                'type': 'logging_disabled',
                                'severity': 'MEDIUM',
                                'description': 'Bucket logging not enabled'
                            })
                except Exception as e:
                    logging.warning(f"Could not check logging for {bucket_name}: {str(e)}")
                
                # Calculate risk score
                risk_score, severity = self.calculate_risk_score(misconfigurations)
                
                results.append({
                    'resource_id': bucket_name,
                    'resource_type': 's3',
                    'misconfigurations': misconfigurations,
                    'risk_score': risk_score,
                    'severity': severity,
                    'timestamp': datetime.now().isoformat()
                })
            
            return results
        
        except Exception as e:
            logging.error(f"Error scanning S3 buckets: {str(e)}")
            return []
    
    def scan_ec2_instances(self) -> List[Dict[str, Any]]:
        """Scan EC2 instances for misconfigurations"""
        logging.info("Starting EC2 instance scan...")
        results = []
        
        try:
            # Get all EC2 instances
            response = self.ec2_client.describe_instances()
            
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instance_id = instance['InstanceId']
                    logging.info(f"Scanning EC2 instance: {instance_id}")
                    misconfigurations = []
                    
                    # Check for public IP
                    if instance.get('PublicIpAddress'):
                        misconfigurations.append({
                            'type': 'public_access',
                            'severity': 'HIGH',
                            'description': 'Instance has public IP address'
                        })
                    
                    # Check for missing tags
                    if not instance.get('Tags'):
                        misconfigurations.append({
                            'type': 'tags_missing',
                            'severity': 'LOW',
                            'description': 'Instance has no tags'
                        })
                    
                    # Check security groups
                    security_groups = instance.get('SecurityGroups', [])
                    for sg in security_groups:
                        sg_id = sg['GroupId']
                        sg_rules = self.ec2_client.describe_security_groups(GroupIds=[sg_id])['SecurityGroups'][0]
                        
                        # Check for overly permissive inbound rules
                        for rule in sg_rules['IpPermissions']:
                            for ip_range in rule.get('IpRanges', []):
                                if ip_range.get('CidrIp') == '0.0.0.0/0':
                                    misconfigurations.append({
                                        'type': 'public_access',
                                        'severity': 'HIGH',
                                        'description': f'Security group {sg_id} allows inbound access from anywhere'
                                    })
                    
                    # Calculate risk score
                    risk_score, severity = self.calculate_risk_score(misconfigurations)
                    
                    results.append({
                        'resource_id': instance_id,
                        'service_type': 'EC2',
                        'configuration': {
                            'instance_type': instance['InstanceType'],
                            'state': instance['State']['Name'],
                            'launch_time': instance['LaunchTime'].isoformat(),
                            'vpc_id': instance.get('VpcId', 'N/A'),
                            'subnet_id': instance.get('SubnetId', 'N/A'),
                            'security_groups': [sg['GroupId'] for sg in security_groups]
                        },
                        'misconfigurations': misconfigurations,
                        'risk_score': risk_score,
                        'severity': severity,
                        'scan_date': datetime.utcnow().isoformat()
                    })
            
            logging.info("EC2 instance scan completed")
            return results
            
        except Exception as e:
            logging.error(f"Error scanning EC2 instances: {str(e)}")
            return []

    def scan_iam_users(self) -> List[Dict[str, Any]]:
        """Scan IAM users for misconfigurations"""
        logging.info("Starting IAM user scan...")
        results = []
        
        try:
            users = self.iam_client.list_users()['Users']
            for user in users:
                username = user['UserName']
                logging.info(f"Scanning IAM user: {username}")
                misconfigurations = []
                
                # Check for access keys
                access_keys = self.iam_client.list_access_keys(UserName=username)['AccessKeyMetadata']
                if access_keys:
                    for key in access_keys:
                        if key['Status'] == 'Active':
                            key_age = (datetime.now(key['CreateDate'].tzinfo) - key['CreateDate']).days
                            if key_age > 90:
                                misconfigurations.append({
                                    'type': 'access_key_rotation',
                                    'severity': 'MEDIUM',
                                    'description': f'Access key is {key_age} days old'
                                })
                
                # Check MFA
                try:
                    mfa_devices = self.iam_client.list_mfa_devices(UserName=username)['MFADevices']
                    if not mfa_devices:
                        misconfigurations.append({
                            'type': 'mfa_disabled',
                            'severity': 'HIGH',
                            'description': 'User does not have MFA enabled'
                        })
                except Exception as e:
                    logging.warning(f"Could not check MFA for user {username}: {str(e)}")
                
                # Calculate risk score
                risk_score, severity = self.calculate_risk_score(misconfigurations)
                
                results.append({
                    'resource_id': username,
                    'service_type': 'IAM',
                    'configuration': {
                        'arn': user['Arn'],
                        'create_date': user['CreateDate'].isoformat(),
                        'path': user['Path'],
                        'has_console_access': bool(user.get('PasswordLastUsed')),
                        'access_key_count': len(access_keys)
                    },
                    'misconfigurations': misconfigurations,
                    'risk_score': risk_score,
                    'severity': severity,
                    'scan_date': datetime.utcnow().isoformat()
                })
            
            logging.info("IAM user scan completed")
            return results
            
        except Exception as e:
            logging.error(f"Error scanning IAM users: {str(e)}")
            return []

    def scan_rds_instances(self) -> List[Dict[str, Any]]:
        """Scan RDS instances for misconfigurations"""
        logging.info("Starting RDS instance scan...")
        results = []
        
        try:
            instances = self.rds_client.describe_db_instances()['DBInstances']
            for instance in instances:
                instance_id = instance['DBInstanceIdentifier']
                logging.info(f"Scanning RDS instance: {instance_id}")
                misconfigurations = []
                
                # Check for public accessibility
                if instance.get('PubliclyAccessible'):
                    misconfigurations.append({
                        'type': 'public_access',
                        'severity': 'HIGH',
                        'description': 'Database is publicly accessible'
                    })
                
                # Check encryption
                if not instance.get('StorageEncrypted'):
                    misconfigurations.append({
                        'type': 'encryption_disabled',
                        'severity': 'HIGH',
                        'description': 'Storage encryption is not enabled'
                    })
                
                # Check backup retention
                if instance.get('BackupRetentionPeriod', 0) < 7:
                    misconfigurations.append({
                        'type': 'backup_retention',
                        'severity': 'MEDIUM',
                        'description': 'Backup retention period is less than 7 days'
                    })
                
                # Calculate risk score
                risk_score, severity = self.calculate_risk_score(misconfigurations)
                
                results.append({
                    'resource_id': instance_id,
                    'service_type': 'RDS',
                    'configuration': {
                        'engine': instance['Engine'],
                        'version': instance['EngineVersion'],
                        'size': instance['DBInstanceClass'],
                        'storage': instance['AllocatedStorage'],
                        'multi_az': instance.get('MultiAZ', False),
                        'vpc_id': instance.get('DBSubnetGroup', {}).get('VpcId', 'N/A')
                    },
                    'misconfigurations': misconfigurations,
                    'risk_score': risk_score,
                    'severity': severity,
                    'scan_date': datetime.utcnow().isoformat()
                })
            
            logging.info("RDS instance scan completed")
            return results
            
        except Exception as e:
            logging.error(f"Error scanning RDS instances: {str(e)}")
            return []

    def scan_all(self):
        """Scan all AWS services for misconfigurations"""
        results = {
            's3': self.scan_s3_buckets(),
            'ec2': self.scan_ec2_instances(),
            'iam': self.scan_iam_users(),
            'rds': self.scan_rds_instances(),
            'network': self.network_scanner.scan_network_acls(),
            'compliance': {
                'cis': self.compliance_checker.check_cis_compliance(),
                'nist': self.compliance_checker.check_nist_compliance(),
                'pci': self.compliance_checker.check_pci_compliance()
            }
        }
        return results

    def scan_and_export(self, export_formats: List[str] = None) -> Dict[str, str]:
        """
        Scan AWS services and export results in specified formats
        
        Args:
            export_formats: List of formats to export ('json', 'csv', 'pdf')
        
        Returns:
            Dictionary mapping format to exported file path
        """
        # Perform scan
        results = self.scan_all()
        
        # Default to all formats if none specified
        if export_formats is None:
            export_formats = ['json', 'csv', 'pdf']
        
        # Export results
        exported_files = {}
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for format in export_formats:
            if format == 'json':
                filepath = self.export_handler.export_json(results, f"scan_results_{timestamp}.json")
                exported_files['json'] = filepath
            elif format == 'csv':
                filepath = self.export_handler.export_csv(results, f"scan_results_{timestamp}.csv")
                exported_files['csv'] = filepath
            elif format == 'pdf':
                filepath = self.export_handler.export_pdf(results, f"scan_results_{timestamp}.pdf")
                exported_files['pdf'] = filepath
            else:
                logging.warning(f"Unsupported export format: {format}")
        
        return exported_files

    def test_aws_connection(self):
        """Test AWS connection and credentials"""
        try:
            # Try to list S3 buckets as a simple test
            s3 = self.session.client('s3')
            s3.list_buckets()
            return True
        except Exception as e:
            logging.error(f"AWS Connection Test Failed: {str(e)}")
            return False

    def scan_service(self, service_type: str) -> List[Dict[str, Any]]:
        """
        Scan a specific AWS service for misconfigurations.
        
        Args:
            service_type: The type of AWS service to scan (e.g., 'ec2', 's3', 'iam', 'rds')
            
        Returns:
            List of scan results containing misconfigurations
            
        Raises:
            ValueError: If service_type is not supported
        """
        service_type = service_type.lower()
        logging.info(f"Starting scan for service: {service_type}")
        
        scan_methods = {
            's3': self.scan_s3_buckets,
            'ec2': self.scan_ec2_instances,
            'iam': self.scan_iam_users,
            'rds': self.scan_rds_instances
        }
        
        if service_type not in scan_methods:
            raise ValueError(f"Unsupported service type: {service_type}. Supported types: {list(scan_methods.keys())}")
        
        try:
            results = scan_methods[service_type]()
            if not isinstance(results, list):
                results = [results]
            
            # Add service_type to each result if not present
            for result in results:
                if 'service_type' not in result:
                    result['service_type'] = service_type
            
            logging.info(f"Completed scan for service: {service_type}")
            return results
        except Exception as e:
            logging.error(f"Error scanning {service_type}: {str(e)}")
            raise

    def scan_all_services(self) -> Dict[str, Any]:
        """Scan all AWS services for misconfigurations"""
        try:
            logging.info("Starting AWS services scan...")
            
            # Log AWS credentials status
            logging.info("AWS Configuration:")
            logging.info(f"Access Key ID exists: {bool(os.getenv('AWS_ACCESS_KEY_ID'))}")
            logging.info(f"Secret Access Key exists: {bool(os.getenv('AWS_SECRET_ACCESS_KEY'))}")
            logging.info(f"Region: {os.getenv('AWS_DEFAULT_REGION', 'not set')}")
            
            if not self.test_aws_connection():
                raise Exception("Failed to connect to AWS. Please check your credentials and permissions.")
            
            results = {}
            
            # S3 scan
            try:
                logging.info("Scanning S3 buckets...")
                results['s3'] = self.scan_s3_buckets()
                logging.info(f"Found {len(results['s3'])} S3 buckets")
            except Exception as e:
                logging.error(f"Error scanning S3: {str(e)}")
                results['s3'] = []
            
            # IAM scan
            try:
                logging.info("Scanning IAM users...")
                results['iam'] = self.scan_iam_users()
                logging.info(f"Found {len(results['iam'])} IAM users")
            except Exception as e:
                logging.error(f"Error scanning IAM: {str(e)}")
                results['iam'] = []
            
            # EC2 scan
            try:
                logging.info("Scanning EC2 instances...")
                results['ec2'] = self.scan_ec2_instances()
                logging.info(f"Found {len(results['ec2'])} EC2 instances")
            except Exception as e:
                logging.error(f"Error scanning EC2: {str(e)}")
                results['ec2'] = []
            
            # RDS scan
            try:
                logging.info("Scanning RDS instances...")
                results['rds'] = self.scan_rds_instances()
                logging.info(f"Found {len(results['rds'])} RDS instances")
            except Exception as e:
                logging.error(f"Error scanning RDS: {str(e)}")
                results['rds'] = []
            
            # Network scan
            try:
                logging.info("Scanning network configurations...")
                results['network'] = self.network_scanner.scan_network_acls()
                logging.info(f"Found {len(results['network'])} network resources")
            except Exception as e:
                logging.error(f"Error scanning network: {str(e)}")
                results['network'] = []
            
            # Compliance checks
            try:
                logging.info("Running compliance checks...")
                results['compliance'] = {
                    'cis': self.compliance_checker.check_cis_compliance(),
                    'nist': self.compliance_checker.check_nist_compliance(),
                    'pci': self.compliance_checker.check_pci_compliance()
                }
                logging.info("Compliance checks completed")
            except Exception as e:
                logging.error(f"Error running compliance checks: {str(e)}")
                results['compliance'] = {
                    'cis': {'score': 0, 'controls': []},
                    'nist': {'score': 0, 'controls': []},
                    'pci': {'score': 0, 'controls': []}
                }
            
            logging.info("AWS services scan completed successfully")
            return results
            
        except Exception as e:
            logging.error(f"Error in scan_all_services: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            raise
