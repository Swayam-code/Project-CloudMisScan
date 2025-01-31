import unittest
import os
import json
import csv
from services.export_handler import ExportHandler
from datetime import datetime

class TestExportHandler(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_reports"
        self.export_handler = ExportHandler(self.test_dir)
        self.sample_data = {
            "compliance": {
                "cis": {
                    "framework": "CIS",
                    "version": "1.4.0",
                    "scan_date": datetime.utcnow().isoformat(),
                    "controls": [
                        {
                            "control_id": "CIS 1.1",
                            "resource": "test-bucket",
                            "status": "PASS",
                            "description": "S3 bucket is properly configured"
                        }
                    ]
                }
            },
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
            ]
        }

    def tearDown(self):
        # Clean up test files
        if os.path.exists(self.test_dir):
            for file in os.listdir(self.test_dir):
                os.remove(os.path.join(self.test_dir, file))
            os.rmdir(self.test_dir)

    def test_json_export(self):
        """Test JSON export functionality"""
        # Export to JSON
        json_file = self.export_handler.export_json(self.sample_data, "test_export.json")
        
        # Verify file exists
        self.assertTrue(os.path.exists(json_file))
        
        # Verify content
        with open(json_file, 'r') as f:
            exported_data = json.load(f)
        
        self.assertEqual(exported_data['compliance']['cis']['framework'], 'CIS')
        self.assertEqual(len(exported_data['s3']), 1)
        self.assertEqual(exported_data['s3'][0]['resource_id'], 'test-bucket')

    def test_csv_export(self):
        """Test CSV export functionality"""
        # Export to CSV
        csv_file = self.export_handler.export_csv(self.sample_data, "test_export.csv")
        
        # Verify file exists
        self.assertTrue(os.path.exists(csv_file))
        
        # Verify content
        with open(csv_file, 'r', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
        # Should have both compliance and misconfiguration entries
        self.assertEqual(len(rows), 2)  # One compliance control and one misconfiguration
        
        # Verify compliance entry
        compliance_row = next(row for row in rows if 'Framework' in row and row['Framework'] == 'CIS')
        self.assertEqual(compliance_row['Control ID'], 'CIS 1.1')
        self.assertEqual(compliance_row['Status'], 'PASS')
        
        # Verify misconfiguration entry
        misconfig_row = next(row for row in rows if 'Service' in row and row['Service'] == 'S3')
        self.assertEqual(misconfig_row['Resource ID'], 'test-bucket')
        self.assertEqual(misconfig_row['Severity'], 'HIGH')

    def test_pdf_export(self):
        """Test PDF export functionality"""
        # Export to PDF
        pdf_file = self.export_handler.export_pdf(self.sample_data, "test_export.pdf")
        
        # Verify file exists
        self.assertTrue(os.path.exists(pdf_file))
        
        # Verify file size (should be non-zero)
        self.assertGreater(os.path.getsize(pdf_file), 0)

if __name__ == '__main__':
    unittest.main()
