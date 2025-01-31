import boto3
import unittest
from services.compliance_checker import ComplianceChecker
from services.aws_scanner import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION

class TestComplianceChecker(unittest.TestCase):
    def setUp(self):
        self.session = boto3.Session(
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_DEFAULT_REGION
        )
        self.compliance_checker = ComplianceChecker(self.session)

    def test_cis_compliance(self):
        """Test CIS compliance checks"""
        results = self.compliance_checker.check_cis_compliance()
        
        # Verify structure
        self.assertEqual(results['framework'], 'CIS')
        self.assertEqual(results['version'], '1.4.0')
        self.assertIsInstance(results['controls'], list)
        
        # Verify controls
        for control in results['controls']:
            self.assertIn('control_id', control)
            self.assertIn('resource', control)
            self.assertIn('status', control)
            self.assertIn('description', control)
            self.assertIn(control['status'], ['PASS', 'FAIL', 'ERROR'])

    def test_nist_compliance(self):
        """Test NIST compliance checks"""
        results = self.compliance_checker.check_nist_compliance()
        
        # Verify structure
        self.assertEqual(results['framework'], 'NIST')
        self.assertEqual(results['version'], '800-53 Rev. 5')
        self.assertIsInstance(results['controls'], list)
        
        # Verify controls
        for control in results['controls']:
            self.assertIn('control_id', control)
            self.assertIn('resource', control)
            self.assertIn('status', control)
            self.assertIn('description', control)
            self.assertIn(control['status'], ['PASS', 'FAIL', 'ERROR'])

    def test_pci_compliance(self):
        """Test PCI DSS compliance checks"""
        results = self.compliance_checker.check_pci_compliance()
        
        # Verify structure
        self.assertEqual(results['framework'], 'PCI DSS')
        self.assertEqual(results['version'], '3.2.1')
        self.assertIsInstance(results['controls'], list)
        
        # Verify controls
        for control in results['controls']:
            self.assertIn('control_id', control)
            self.assertIn('resource', control)
            self.assertIn('status', control)
            self.assertIn('description', control)
            self.assertIn(control['status'], ['PASS', 'FAIL', 'ERROR'])

if __name__ == '__main__':
    unittest.main()
