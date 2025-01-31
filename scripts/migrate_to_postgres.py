import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import Base, ScanResult, Report
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLite configuration
SQLITE_URL = "sqlite:///./cloud_scan.db"
sqlite_engine = create_engine(SQLITE_URL)
SQLiteSession = sessionmaker(bind=sqlite_engine)

# PostgreSQL configuration
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "your_password"  # Change this
POSTGRES_HOST = "localhost"
POSTGRES_PORT = "5432"
POSTGRES_DB = "cloud_scan"

POSTGRES_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

def create_postgres_db():
    """Create PostgreSQL database if it doesn't exist"""
    temp_engine = create_engine(f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/postgres")
    conn = temp_engine.connect()
    conn.execute("commit")
    
    # Check if database exists
    result = conn.execute(f"SELECT 1 FROM pg_database WHERE datname = '{POSTGRES_DB}'")
    if not result.scalar():
        conn.execute(f"CREATE DATABASE {POSTGRES_DB}")
        logger.info(f"Created database {POSTGRES_DB}")
    
    conn.close()
    temp_engine.dispose()

def migrate_data():
    """Migrate data from SQLite to PostgreSQL"""
    try:
        # Create PostgreSQL database
        create_postgres_db()
        
        # Create PostgreSQL engine and tables
        postgres_engine = create_engine(POSTGRES_URL)
        Base.metadata.create_all(postgres_engine)
        PostgresSession = sessionmaker(bind=postgres_engine)
        
        # Create sessions
        sqlite_session = SQLiteSession()
        postgres_session = PostgresSession()
        
        # Migrate scan results
        logger.info("Migrating scan results...")
        scan_results = sqlite_session.query(ScanResult).all()
        for result in scan_results:
            new_result = ScanResult(
                scan_date=result.scan_date,
                service_type=result.service_type,
                resource_id=result.resource_id,
                configuration=result.configuration,
                misconfigurations=result.misconfigurations,
                risk_score=result.risk_score,
                severity=result.severity,
                remediation_steps=result.remediation_steps
            )
            postgres_session.add(new_result)
        
        # Migrate reports
        logger.info("Migrating reports...")
        reports = sqlite_session.query(Report).all()
        for report in reports:
            new_report = Report(
                creation_date=report.creation_date,
                report_type=report.report_type,
                content=report.content,
                summary=report.summary
            )
            postgres_session.add(new_report)
        
        # Commit changes
        postgres_session.commit()
        logger.info("Migration completed successfully!")
        
        # Update .env file
        update_env_file(POSTGRES_URL)
        
        return True
    
    except Exception as e:
        logger.error(f"Error during migration: {str(e)}")
        return False
    
    finally:
        sqlite_session.close()
        postgres_session.close()

def update_env_file(new_url):
    """Update DATABASE_URL in .env file"""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    
    with open(env_path, 'r') as file:
        lines = file.readlines()
    
    with open(env_path, 'w') as file:
        for line in lines:
            if line.startswith('DATABASE_URL='):
                file.write(f'DATABASE_URL={new_url}\n')
            else:
                file.write(line)
    
    logger.info("Updated DATABASE_URL in .env file")

def verify_migration():
    """Verify the migration was successful"""
    postgres_engine = create_engine(POSTGRES_URL)
    PostgresSession = sessionmaker(bind=postgres_engine)
    postgres_session = PostgresSession()
    
    try:
        # Check scan results
        scan_count = postgres_session.query(ScanResult).count()
        report_count = postgres_session.query(Report).count()
        
        logger.info("\nMigration Verification:")
        logger.info(f"Scan Results: {scan_count}")
        logger.info(f"Reports: {report_count}")
        
        # Test querying
        latest_scan = postgres_session.query(ScanResult).order_by(ScanResult.scan_date.desc()).first()
        if latest_scan:
            logger.info("\nLatest Scan Result:")
            logger.info(f"ID: {latest_scan.id}")
            logger.info(f"Service Type: {latest_scan.service_type}")
            logger.info(f"Resource ID: {latest_scan.resource_id}")
            logger.info(f"Severity: {latest_scan.severity}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error verifying migration: {str(e)}")
        return False
    
    finally:
        postgres_session.close()

if __name__ == "__main__":
    logger.info("Starting migration to PostgreSQL...")
    if migrate_data():
        verify_migration()
    else:
        logger.error("Migration failed!")
