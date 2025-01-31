import boto3
import unittest
from unittest.mock import MagicMock, patch
from services.network_scanner import NetworkScanner
from datetime import datetime

class TestNetworkScanner(unittest.TestCase):
    @patch('boto3.Session')
    def setUp(self, mock_session):
        self.mock_ec2_client = MagicMock()
        mock_session.return_value.client.return_value = self.mock_ec2_client
        self.session = mock_session
        self.network_scanner = NetworkScanner(self.session.return_value)

    @patch('boto3.Session.client')
    def test_scan_network_acls(self, mock_client):
        # Mock EC2 client response
        mock_ec2 = MagicMock()
        mock_client.return_value = mock_ec2
        
        # Sample Network ACL response
        mock_ec2.describe_network_acls.return_value = {
            'NetworkAcls': [
                {
                    'NetworkAclId': 'acl-12345',
                    'VpcId': 'vpc-67890',
                    'IsDefault': True,
                    'Entries': [
                        {
                            'RuleNumber': 100,
                            'Protocol': '-1',
                            'RuleAction': 'allow',
                            'Egress': False,
                            'CidrBlock': '0.0.0.0/0'
                        }
                    ],
                    'Tags': []
                }
            ]
        }

        results = self.network_scanner.scan_network_acls()

        # Verify results
        self.assertEqual(len(results), 1)
        result = results[0]
        
        # Check resource identification
        self.assertEqual(result['resource_id'], 'acl-12345')
        self.assertEqual(result['service_type'], 'NetworkACL')
        self.assertEqual(result['vpc_id'], 'vpc-67890')

        # Check misconfigurations
        misconfigs = result['misconfigurations']
        self.assertTrue(any(m['type'] == 'unrestricted_access' for m in misconfigs))
        self.assertTrue(any(m['type'] == 'insecure_protocol' for m in misconfigs))
        self.assertTrue(any(m['type'] == 'no_tags' for m in misconfigs))

        # Check risk score and severity
        self.assertGreater(result['risk_score'], 0)
        self.assertIn(result['severity'], ['LOW', 'MEDIUM', 'HIGH'])

    def test_calculate_risk_score(self):
        misconfigurations = [
            {'type': 'unrestricted_access', 'severity': 'HIGH'},
            {'type': 'no_tags', 'severity': 'LOW'}
        ]
        score = self.network_scanner._calculate_risk_score(misconfigurations)
        self.assertGreater(score, 0)
        self.assertLessEqual(score, 10.0)

    def test_determine_severity(self):
        self.assertEqual(self.network_scanner._determine_severity(8.0), 'HIGH')
        self.assertEqual(self.network_scanner._determine_severity(5.0), 'MEDIUM')
        self.assertEqual(self.network_scanner._determine_severity(2.0), 'LOW')

if __name__ == '__main__':
    unittest.main()
