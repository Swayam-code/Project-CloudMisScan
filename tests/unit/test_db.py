from models.database import SessionLocal, ScanResult, Report
from datetime import datetime
import json

def test_database():
    """Test database operations"""
    db = SessionLocal()
    try:
        # Test creating a scan result
        test_scan = ScanResult(
            service_type="S3",
            resource_id="test-bucket",
            configuration={"bucket_name": "test-bucket"},
            misconfigurations=[{
                "type": "public_access",
                "severity": "HIGH",
                "description": "Bucket is publicly accessible"
            }],
            risk_score=8.0,
            severity="HIGH",
            remediation_steps=["Enable block public access settings"]
        )
        db.add(test_scan)
        
        # Test creating a report
        test_report = Report(
            report_type="JSON",
            content={"scan_id": 1, "findings": ["Test finding"]},
            summary={"total_issues": 1}
        )
        db.add(test_report)
        
        # Commit the changes
        db.commit()
        
        # Verify the data
        scan_result = db.query(ScanResult).first()
        report = db.query(Report).first()
        
        print("\nDatabase Test Results:")
        print("-" * 50)
        
        print("\nScan Result:")
        print(f"ID: {scan_result.id}")
        print(f"Service Type: {scan_result.service_type}")
        print(f"Resource ID: {scan_result.resource_id}")
        print(f"Risk Score: {scan_result.risk_score}")
        print(f"Severity: {scan_result.severity}")
        print(f"Misconfigurations: {json.dumps(scan_result.misconfigurations, indent=2)}")
        
        print("\nReport:")
        print(f"ID: {report.id}")
        print(f"Type: {report.report_type}")
        print(f"Creation Date: {report.creation_date}")
        print(f"Summary: {json.dumps(report.summary, indent=2)}")
        
        return True
        
    except Exception as e:
        print(f"Error testing database: {str(e)}")
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    success = test_database()
    if success:
        print("\nDatabase test completed successfully!")
    else:
        print("\nDatabase test failed!")
