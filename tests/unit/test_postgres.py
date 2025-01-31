from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import ScanResult, Report
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_postgres_connection():
    """Test PostgreSQL connection and queries"""
    try:
        # Get database URL from environment
        from dotenv import load_dotenv
        import os
        load_dotenv()
        
        DATABASE_URL = os.getenv("DATABASE_URL")
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Test queries
        logger.info("\nTesting PostgreSQL Connection:")
        logger.info("-" * 50)
        
        # Count records
        scan_count = session.query(ScanResult).count()
        report_count = session.query(Report).count()
        
        logger.info(f"\nTotal Records:")
        logger.info(f"Scan Results: {scan_count}")
        logger.info(f"Reports: {report_count}")
        
        # Get latest scan
        latest_scan = session.query(ScanResult).order_by(ScanResult.scan_date.desc()).first()
        if latest_scan:
            logger.info(f"\nLatest Scan:")
            logger.info(f"ID: {latest_scan.id}")
            logger.info(f"Date: {latest_scan.scan_date}")
            logger.info(f"Service: {latest_scan.service_type}")
            logger.info(f"Resource: {latest_scan.resource_id}")
        
        logger.info("\nPostgreSQL connection test completed successfully!")
        return True
    
    except Exception as e:
        logger.error(f"Error testing PostgreSQL connection: {str(e)}")
        return False
    
    finally:
        session.close()

if __name__ == "__main__":
    test_postgres_connection()
