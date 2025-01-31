from typing import Dict, List, Any
import boto3
import logging
from datetime import datetime

class NetworkScanner:
    def __init__(self, session: boto3.Session):
        self.session = session
        self.ec2_client = session.client('ec2')
        self.risk_weights = {
            'open_ports': 10.0,
            'unrestricted_access': 8.0,
            'insecure_protocol': 6.0,
            'no_egress_rules': 4.0,
            'no_tags': 2.0
        }

    def scan_network_acls(self) -> List[Dict[str, Any]]:
        """Scan Network ACLs for security misconfigurations"""
        try:
            response = self.ec2_client.describe_network_acls()
            results = []

            for nacl in response['NetworkAcls']:
                misconfigurations = []
                nacl_id = nacl['NetworkAclId']
                vpc_id = nacl['VpcId']

                # Check for unrestricted inbound access
                for entry in nacl['Entries']:
                    if entry['Egress'] is False:  # Inbound rule
                        if (entry['CidrBlock'] == '0.0.0.0/0' and 
                            entry['RuleAction'] == 'allow' and 
                            entry['Protocol'] == '-1'):  # All traffic
                            misconfigurations.append({
                                'type': 'unrestricted_access',
                                'severity': 'HIGH',
                                'description': f'Network ACL {nacl_id} allows unrestricted inbound access'
                            })

                # Check for missing egress rules
                has_egress_rules = any(entry['Egress'] for entry in nacl['Entries'])
                if not has_egress_rules:
                    misconfigurations.append({
                        'type': 'no_egress_rules',
                        'severity': 'MEDIUM',
                        'description': f'Network ACL {nacl_id} has no egress rules defined'
                    })

                # Check for insecure protocols (e.g., allowing all ports)
                for entry in nacl['Entries']:
                    if (entry['Protocol'] == '-1' and 
                        entry['RuleAction'] == 'allow'):
                        misconfigurations.append({
                            'type': 'insecure_protocol',
                            'severity': 'MEDIUM',
                            'description': f'Network ACL {nacl_id} allows all protocols'
                        })

                # Check for tags
                if 'Tags' not in nacl or not nacl['Tags']:
                    misconfigurations.append({
                        'type': 'no_tags',
                        'severity': 'LOW',
                        'description': f'Network ACL {nacl_id} has no tags'
                    })

                # Calculate risk score
                risk_score = self._calculate_risk_score(misconfigurations)
                severity = self._determine_severity(risk_score)

                results.append({
                    'resource_id': nacl_id,
                    'service_type': 'NetworkACL',
                    'vpc_id': vpc_id,
                    'configuration': {
                        'entries': nacl['Entries'],
                        'is_default': nacl.get('IsDefault', False),
                        'associations': nacl.get('Associations', []),
                        'tags': nacl.get('Tags', [])
                    },
                    'misconfigurations': misconfigurations,
                    'risk_score': risk_score,
                    'severity': severity,
                    'scan_date': datetime.utcnow().isoformat()
                })

            return results

        except Exception as e:
            logging.error(f"Error scanning Network ACLs: {str(e)}")
            raise

    def _calculate_risk_score(self, misconfigurations: List[Dict[str, Any]]) -> float:
        """Calculate risk score based on misconfigurations"""
        if not misconfigurations:
            return 0.0
            
        total_score = 0.0
        for issue in misconfigurations:
            issue_type = issue['type']
            weight = self.risk_weights.get(issue_type, 1.0)
            total_score += weight
        
        return min(total_score, 10.0)  # Cap at 10.0

    def _determine_severity(self, risk_score: float) -> str:
        """Determine severity level based on risk score"""
        if risk_score >= 7.0:
            return 'HIGH'
        elif risk_score >= 4.0:
            return 'MEDIUM'
        return 'LOW'
