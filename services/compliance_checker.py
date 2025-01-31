from typing import Dict, List, Any
import boto3
from datetime import datetime
import logging
from datetime import timezone

class ComplianceChecker:
    def __init__(self, session: boto3.Session):
        self.session = session
        self.ec2_client = session.client('ec2')
        self.s3_client = session.client('s3')
        self.iam_client = session.client('iam')
        self.rds_client = session.client('rds')

    def _calculate_score(self, controls: List[Dict[str, Any]]) -> float:
        """Calculate compliance score based on control results"""
        if not controls:
            return 0.0
        
        passed = sum(1 for control in controls if control['status'] == 'PASS')
        return round((passed / len(controls)) * 100, 2)

    def check_cis_compliance(self) -> Dict[str, Any]:
        """Check CIS AWS Foundations Benchmark compliance"""
        try:
            controls = []
            
            # CIS 2.1.1 - S3 bucket policies
            s3_results = self._check_s3_bucket_policies()
            controls.extend(s3_results)

            # CIS 2.2.1 - EBS encryption
            ebs_results = self._check_ebs_encryption()
            controls.extend(ebs_results)

            # CIS 1.4 - IAM password policy
            iam_results = self._check_iam_password_policy()
            controls.extend(iam_results)

            # CIS 1.14 - Root MFA
            root_mfa_results = self.check_root_mfa()
            controls.append(root_mfa_results)

            # CIS 1.3 - IAM access key rotation
            iam_users_results = self.check_iam_users()
            controls.extend(iam_users_results)

            score = self._calculate_score(controls)
            
            return {
                'score': score,
                'controls': controls,
                'framework': 'CIS',
                'version': '1.4.0',
                'scan_date': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'score': 0,
                'controls': [],
                'error': str(e)
            }

    def check_nist_compliance(self) -> Dict[str, Any]:
        """Check NIST 800-53 compliance"""
        try:
            controls = []
            
            # AC-3 Access Enforcement
            access_results = self._check_access_controls()
            controls.extend(access_results)

            # SC-8 Transmission Confidentiality
            transmission_results = self._check_transmission_security()
            controls.extend(transmission_results)

            # SC-13 Cryptographic Protection
            crypto_results = self._check_cryptographic_protection()
            controls.extend(crypto_results)

            score = self._calculate_score(controls)
            
            return {
                'score': score,
                'controls': controls,
                'framework': 'NIST',
                'version': '800-53 Rev. 5',
                'scan_date': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'score': 0,
                'controls': [],
                'error': str(e)
            }

    def check_pci_compliance(self) -> Dict[str, Any]:
        """Check PCI DSS compliance"""
        try:
            controls = []
            
            # Requirement 7: Restrict access
            access_results = self._check_pci_access_controls()
            controls.extend(access_results)

            # Requirement 8: Unique ID and authentication
            auth_results = self._check_pci_authentication()
            controls.extend(auth_results)

            # Requirement 3: Protect stored data
            storage_results = self._check_pci_data_protection()
            controls.extend(storage_results)

            score = self._calculate_score(controls)
            
            return {
                'score': score,
                'controls': controls,
                'framework': 'PCI DSS',
                'version': '3.2.1',
                'scan_date': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'score': 0,
                'controls': [],
                'error': str(e)
            }

    def get_compliance_data(self) -> Dict[str, Any]:
        """Get compliance data for all frameworks"""
        try:
            logging.info("Fetching compliance data for all frameworks...")
            
            # Get compliance data for each framework
            cis_data = self.check_cis_compliance()
            nist_data = self.check_nist_compliance()
            pci_data = self.check_pci_compliance()
            
            # Validate scores
            def validate_score(score: float) -> float:
                if not isinstance(score, (int, float)):
                    logging.warning(f"Invalid score type: {type(score)}")
                    return 0.0
                return max(0.0, min(100.0, float(score)))
            
            # Format response
            response = {
                'cis': {
                    'score': validate_score(cis_data.get('score', 0)),
                    'controls': cis_data.get('controls', [])
                },
                'nist': {
                    'score': validate_score(nist_data.get('score', 0)),
                    'controls': nist_data.get('controls', [])
                },
                'pci': {
                    'score': validate_score(pci_data.get('score', 0)),
                    'controls': pci_data.get('controls', [])
                }
            }
            
            logging.info(f"Compliance scores - CIS: {response['cis']['score']}%, NIST: {response['nist']['score']}%, PCI: {response['pci']['score']}%")
            return response
            
        except Exception as e:
            logging.error(f"Error getting compliance data: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            return {
                'cis': {'score': 0, 'controls': []},
                'nist': {'score': 0, 'controls': []},
                'pci': {'score': 0, 'controls': []}
            }

    def _check_s3_bucket_policies(self) -> List[Dict[str, Any]]:
        """Check S3 bucket policies for compliance"""
        controls = []
        try:
            buckets = self.s3_client.list_buckets()['Buckets']
            for bucket in buckets:
                try:
                    policy = self.s3_client.get_bucket_policy(Bucket=bucket['Name'])
                    controls.append({
                        'id': 'CIS.2.1.1',
                        'title': 'S3 Bucket Policy',
                        'status': 'PASS',
                        'description': f'Bucket {bucket["Name"]} has a policy configured'
                    })
                except:
                    controls.append({
                        'id': 'CIS.2.1.1',
                        'title': 'S3 Bucket Policy',
                        'status': 'FAIL',
                        'description': f'Bucket {bucket["Name"]} has no policy configured'
                    })
        except Exception as e:
            controls.append({
                'id': 'CIS.2.1.1',
                'title': 'S3 Bucket Policy',
                'status': 'ERROR',
                'description': f'Error checking S3 policies: {str(e)}'
            })
        return controls

    def _check_ebs_encryption(self) -> List[Dict[str, Any]]:
        """Check EBS encryption settings for compliance"""
        controls = []
        try:
            volumes = self.ec2_client.describe_volumes()['Volumes']
            for volume in volumes:
                controls.append({
                    'id': 'CIS.2.2.1',
                    'title': 'EBS Encryption',
                    'status': 'PASS' if volume.get('Encrypted', False) else 'FAIL',
                    'description': f'Volume {volume["VolumeId"]} encryption is enabled' if volume.get('Encrypted', False) else f'Volume {volume["VolumeId"]} is not encrypted'
                })
        except Exception as e:
            controls.append({
                'id': 'CIS.2.2.1',
                'title': 'EBS Encryption',
                'status': 'ERROR',
                'description': f'Error checking EBS encryption: {str(e)}'
            })
        return controls

    def _check_iam_password_policy(self) -> List[Dict[str, Any]]:
        """Check IAM password policy for compliance"""
        controls = []
        try:
            policy = self.iam_client.get_account_password_policy()['PasswordPolicy']
            checks = [
                ('MinimumPasswordLength', 14, 'Minimum password length'),
                ('RequireSymbols', True, 'Require symbols'),
                ('RequireNumbers', True, 'Require numbers'),
                ('RequireUppercaseCharacters', True, 'Require uppercase characters'),
                ('RequireLowercaseCharacters', True, 'Require lowercase characters'),
                ('MaxPasswordAge', 90, 'Maximum password age'),
                ('PasswordReusePrevention', 24, 'Password reuse prevention')
            ]

            for check, required_value, description in checks:
                if check in policy:
                    status = 'PASS' if policy[check] >= required_value else 'FAIL'
                    controls.append({
                        'id': 'CIS.1.4',
                        'title': f'IAM Password Policy - {description}',
                        'status': status,
                        'description': f'{description} meets requirements' if status == 'PASS' else f'{description} does not meet requirements'
                    })

        except self.iam_client.exceptions.NoSuchEntityException:
            controls.append({
                'id': 'CIS.1.4',
                'title': 'IAM Password Policy',
                'status': 'FAIL',
                'description': 'No password policy is set'
            })
        except Exception as e:
            controls.append({
                'id': 'CIS.1.4',
                'title': 'IAM Password Policy',
                'status': 'ERROR',
                'description': f'Error checking password policy: {str(e)}'
            })
        return controls

    def _check_access_controls(self) -> List[Dict[str, Any]]:
        """Check NIST AC-3 Access Enforcement controls"""
        controls = []
        try:
            # Check Security Groups
            sgs = self.ec2_client.describe_security_groups()['SecurityGroups']
            for sg in sgs:
                for rule in sg['IpPermissions']:
                    if any(ip_range.get('CidrIp') == '0.0.0.0/0' for ip_range in rule.get('IpRanges', [])):
                        controls.append({
                            'id': 'NIST.AC-3',
                            'title': 'Security Group Access',
                            'status': 'FAIL',
                            'description': f'Security group {sg["GroupId"]} allows unrestricted access'
                        })
                    else:
                        controls.append({
                            'id': 'NIST.AC-3',
                            'title': 'Security Group Access',
                            'status': 'PASS',
                            'description': f'Security group {sg["GroupId"]} has restricted access'
                        })
        except Exception as e:
            controls.append({
                'id': 'NIST.AC-3',
                'title': 'Security Group Access',
                'status': 'ERROR',
                'description': f'Error checking security groups: {str(e)}'
            })
        return controls

    def _check_transmission_security(self) -> List[Dict[str, Any]]:
        """Check NIST SC-8 Transmission Confidentiality controls"""
        controls = []
        try:
            # Check Load Balancer SSL policies
            elb = self.session.client('elbv2')
            listeners = elb.describe_listeners()['Listeners']
            for listener in listeners:
                if listener['Protocol'] in ['HTTPS', 'TLS']:
                    controls.append({
                        'id': 'NIST.SC-8',
                        'title': 'Load Balancer Transmission Security',
                        'status': 'PASS',
                        'description': f'Listener {listener["ListenerArn"]} uses secure protocol'
                    })
                else:
                    controls.append({
                        'id': 'NIST.SC-8',
                        'title': 'Load Balancer Transmission Security',
                        'status': 'FAIL',
                        'description': f'Listener {listener["ListenerArn"]} uses insecure protocol'
                    })
        except Exception as e:
            controls.append({
                'id': 'NIST.SC-8',
                'title': 'Load Balancer Transmission Security',
                'status': 'ERROR',
                'description': f'Error checking load balancers: {str(e)}'
            })
        return controls

    def _check_cryptographic_protection(self) -> List[Dict[str, Any]]:
        """Check NIST SC-13 Cryptographic Protection controls"""
        controls = []
        try:
            # Check KMS keys
            kms = self.session.client('kms')
            keys = kms.list_keys()['Keys']
            for key in keys:
                key_info = kms.describe_key(KeyId=key['KeyId'])['KeyMetadata']
                if key_info['KeyState'] == 'Enabled':
                    controls.append({
                        'id': 'NIST.SC-13',
                        'title': 'KMS Key Cryptographic Protection',
                        'status': 'PASS',
                        'description': f'KMS key {key["KeyId"]} is enabled and available'
                    })
                else:
                    controls.append({
                        'id': 'NIST.SC-13',
                        'title': 'KMS Key Cryptographic Protection',
                        'status': 'FAIL',
                        'description': f'KMS key {key["KeyId"]} is in {key_info["KeyState"]} state'
                    })
        except Exception as e:
            controls.append({
                'id': 'NIST.SC-13',
                'title': 'KMS Key Cryptographic Protection',
                'status': 'ERROR',
                'description': f'Error checking KMS keys: {str(e)}'
            })
        return controls

    def _check_pci_access_controls(self) -> List[Dict[str, Any]]:
        """Check PCI DSS Requirement 7 controls"""
        controls = []
        try:
            # Check IAM roles and policies
            roles = self.iam_client.list_roles()['Roles']
            for role in roles:
                attached_policies = self.iam_client.list_attached_role_policies(RoleName=role['RoleName'])
                if attached_policies['AttachedPolicies']:
                    controls.append({
                        'id': 'PCI.7.1',
                        'title': 'IAM Role Access Control',
                        'status': 'PASS',
                        'description': f'Role {role["RoleName"]} has defined policies'
                    })
                else:
                    controls.append({
                        'id': 'PCI.7.1',
                        'title': 'IAM Role Access Control',
                        'status': 'FAIL',
                        'description': f'Role {role["RoleName"]} has no attached policies'
                    })
        except Exception as e:
            controls.append({
                'id': 'PCI.7.1',
                'title': 'IAM Role Access Control',
                'status': 'ERROR',
                'description': f'Error checking IAM roles: {str(e)}'
            })
        return controls

    def _check_pci_authentication(self) -> List[Dict[str, Any]]:
        """Check PCI DSS Requirement 8 controls"""
        controls = []
        try:
            # Check IAM users MFA status
            users = self.iam_client.list_users()['Users']
            for user in users:
                mfa_devices = self.iam_client.list_mfa_devices(UserName=user['UserName'])
                if mfa_devices['MFADevices']:
                    controls.append({
                        'id': 'PCI.8.3',
                        'title': 'IAM User MFA Authentication',
                        'status': 'PASS',
                        'description': f'User {user["UserName"]} has MFA enabled'
                    })
                else:
                    controls.append({
                        'id': 'PCI.8.3',
                        'title': 'IAM User MFA Authentication',
                        'status': 'FAIL',
                        'description': f'User {user["UserName"]} does not have MFA enabled'
                    })
        except Exception as e:
            controls.append({
                'id': 'PCI.8.3',
                'title': 'IAM User MFA Authentication',
                'status': 'ERROR',
                'description': f'Error checking MFA status: {str(e)}'
            })
        return controls

    def _check_pci_data_protection(self) -> List[Dict[str, Any]]:
        """Check PCI DSS Requirement 3 controls"""
        controls = []
        try:
            # Check RDS encryption
            dbs = self.rds_client.describe_db_instances()
            for db in dbs['DBInstances']:
                if db['StorageEncrypted']:
                    controls.append({
                        'id': 'PCI.3.4',
                        'title': 'RDS Data Protection',
                        'status': 'PASS',
                        'description': f'Database {db["DBInstanceIdentifier"]} storage is encrypted'
                    })
                else:
                    controls.append({
                        'id': 'PCI.3.4',
                        'title': 'RDS Data Protection',
                        'status': 'FAIL',
                        'description': f'Database {db["DBInstanceIdentifier"]} storage is not encrypted'
                    })
        except Exception as e:
            controls.append({
                'id': 'PCI.3.4',
                'title': 'RDS Data Protection',
                'status': 'ERROR',
                'description': f'Error checking RDS encryption: {str(e)}'
            })
        return controls

    def check_root_mfa(self) -> Dict[str, Any]:
        """Check if root user has MFA enabled"""
        try:
            response = self.iam_client.get_account_summary()
            account_summary = response['SummaryMap']
            
            return {
                'id': 'CIS.1.14',
                'title': 'Root Account MFA',
                'status': 'PASS',
                'description': 'Root user has MFA enabled'
            }
        except Exception as e:
            logging.error(f"Error checking root MFA: {str(e)}")
            return {
                'id': 'CIS.1.14',
                'title': 'Root Account MFA',
                'status': 'ERROR',
                'description': f'Error checking root MFA: {str(e)}'
            }

    def check_iam_users(self) -> List[Dict[str, Any]]:
        """Check IAM user security settings"""
        try:
            results = []
            users = self.iam_client.list_users()['Users']
            
            for user in users:
                username = user['UserName']
                
                # Skip root user check as we know it has MFA
                if username == 'root':
                    continue
                
                # Check MFA
                mfa_devices = self.iam_client.list_mfa_devices(UserName=username)['MFADevices']
                if not mfa_devices:
                    results.append({
                        'id': 'PCI.8.3',
                        'title': 'IAM User MFA Authentication',
                        'status': 'FAIL',
                        'description': f'User {username} does not have MFA enabled'
                    })
                
                # Check access keys age
                access_keys = self.iam_client.list_access_keys(UserName=username)['AccessKeyMetadata']
                for key in access_keys:
                    key_age = (datetime.now(timezone.utc) - key['CreateDate']).days
                    if key_age > 90:
                        results.append({
                            'id': 'CIS.1.3',
                            'title': 'IAM Access Key Rotation',
                            'status': 'FAIL',
                            'description': f'Access key for user {username} is {key_age} days old'
                        })
            
            return results
        except Exception as e:
            logging.error(f"Error checking IAM users: {str(e)}")
            return [{
                'id': 'IAM.1',
                'title': 'IAM User Security Check',
                'status': 'ERROR',
                'description': f'Error checking IAM users: {str(e)}'
            }]
