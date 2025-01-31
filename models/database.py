from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, DateTime, JSON, Float, ForeignKey
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./cloud_scan.db"  # For development, replace with PostgreSQL in production

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class ScanResult(Base):
    __tablename__ = "scan_results"

    id = Column(Integer, primary_key=True, index=True)
    scan_date = Column(DateTime, default=datetime.utcnow)
    service_type = Column(String)  # e.g., 'S3', 'EC2', 'IAM'
    resource_id = Column(String, index=True)
    configuration = Column(JSON)
    misconfigurations = Column(JSON)
    risk_score = Column(Float)
    severity = Column(String)  # 'Low', 'Medium', 'High'
    remediation_steps = Column(JSON)

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    creation_date = Column(DateTime, default=datetime.utcnow)
    report_type = Column(String)  # 'PDF', 'JSON', 'CSV'
    content = Column(JSON)
    summary = Column(JSON)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
