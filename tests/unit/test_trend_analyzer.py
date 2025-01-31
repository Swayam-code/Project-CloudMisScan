import unittest
import os
import sqlite3
from datetime import datetime, timezone, timedelta
import time
from services.trend_analyzer import TrendAnalyzer

class TestTrendAnalyzer(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.test_db = "test_data/test_scan_history.db"
        
        # Ensure test directory exists
        os.makedirs(os.path.dirname(self.test_db), exist_ok=True)
        
        # Remove existing test database if it exists
        if os.path.exists(self.test_db):
            try:
                os.remove(self.test_db)
            except PermissionError:
                print(f"Warning: Could not delete {self.test_db}, file is in use.")
        
        self.trend_analyzer = TrendAnalyzer(self.test_db)
        
        # Sample scan results
        self.sample_scan = {
            "s3": [
                {
                    "resource_id": "test-bucket",
                    "misconfigurations": [
                        {
                            "type": "public_access",
                            "severity": "HIGH",
                            "description": "Bucket allows public access"
                        }
                    ]
                }
            ],
            "compliance": {
                "cis": {
                    "framework": "CIS",
                    "version": "1.4.0",
                    "controls": [
                        {
                            "control_id": "CIS 1.1",
                            "resource": "test-bucket",
                            "status": "PASS",
                            "description": "S3 bucket is properly configured"
                        },
                        {
                            "control_id": "CIS 1.2",
                            "resource": "test-bucket",
                            "status": "FAIL",
                            "description": "S3 bucket is misconfigured"
                        }
                    ]
                }
            }
        }

    def tearDown(self):
        """Clean up test environment"""
        # Close the database connection
        if hasattr(self.trend_analyzer, 'conn') and self.trend_analyzer.conn:
            self.trend_analyzer.conn.close()
            self.trend_analyzer.conn = None
        
        # Remove test database
        if os.path.exists(self.test_db):
            try:
                os.remove(self.test_db)
            except PermissionError:
                print(f"Warning: Could not delete {self.test_db}, file is in use.")
        
        # Remove test directory if empty
        try:
            os.rmdir(os.path.dirname(self.test_db))
        except (OSError, PermissionError):
            pass

    def test_store_scan_results(self):
        """Test storing scan results"""
        self.trend_analyzer.store_scan_results(self.sample_scan)
        
        # Get trends to verify storage
        trends = self.trend_analyzer.get_historical_trends(days=1)
        
        self.assertEqual(len(trends['overall']), 1)
        self.assertEqual(trends['overall'][0]['total_issues'], 1)
        self.assertGreater(trends['overall'][0]['risk_score'], 0)
        
        self.assertIn('s3', trends['services'])
        self.assertEqual(len(trends['services']['s3']), 1)
        self.assertEqual(trends['services']['s3'][0]['issue_type'], 'public_access')

    def test_historical_trends(self):
        """Test retrieving historical trends"""
        # Store multiple scan results with delays
        for i in range(3):
            self.trend_analyzer.store_scan_results(self.sample_scan)
            time.sleep(0.1)  # Small delay to ensure different timestamps
        
        trends = self.trend_analyzer.get_historical_trends(days=7)
        
        self.assertEqual(len(trends['overall']), 3)
        self.assertTrue(all(t['total_issues'] > 0 for t in trends['overall']))
        self.assertTrue(all(t['risk_score'] > 0 for t in trends['overall']))

    def test_compliance_trends(self):
        """Test retrieving compliance trends"""
        # Store multiple scan results with delays
        for i in range(3):
            self.trend_analyzer.store_scan_results(self.sample_scan)
            time.sleep(0.1)  # Small delay to ensure different timestamps
        
        trends = self.trend_analyzer.get_compliance_trends(days=7)
        
        self.assertIn('cis', trends)
        self.assertEqual(len(trends['cis']), 3)
        self.assertTrue(all(t['compliance_score'] == 50.0 for t in trends['cis']))  # 1 PASS, 1 FAIL = 50%

    def test_recent_changes(self):
        """Test detecting recent changes"""
        # Store initial scan
        self.trend_analyzer.store_scan_results(self.sample_scan)
        time.sleep(0.1)  # Small delay to ensure different timestamps
        
        # Create modified scan with new issue
        modified_scan = {
            "s3": [
                {
                    "resource_id": "test-bucket",
                    "misconfigurations": [
                        {
                            "type": "public_access",
                            "severity": "HIGH",
                            "description": "Bucket allows public access"
                        },
                        {
                            "type": "encryption_disabled",
                            "severity": "MEDIUM",
                            "description": "Bucket encryption is disabled"
                        }
                    ]
                }
            ],
            "compliance": self.sample_scan['compliance']
        }
        
        # Store modified scan
        self.trend_analyzer.store_scan_results(modified_scan)
        
        changes = self.trend_analyzer.get_recent_changes(days=1)
        
        # Verify that new issues were detected
        self.assertTrue(
            any(c['type'] == 'new_issues' and c['service'] == 's3' and c['issues'] == 1 for c in changes),
            "Expected to find new issues in changes"
        )

if __name__ == '__main__':
    unittest.main()
