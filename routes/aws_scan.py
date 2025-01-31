from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List, Any
from datetime import datetime

from models.database import get_db, ScanResult
from services.aws_scanner import AWSScanner

router = APIRouter()
scanner = AWSScanner()

@router.post("/start")
async def start_scan(db: Session = Depends(get_db)):
    """Start a new AWS configuration scan"""
    try:
        scan_results = scanner.scan_all()
        
        # Store results in database
        for service, results in scan_results.items():
            for result in results:
                db_result = ScanResult(
                    service_type=result['service_type'],
                    resource_id=result['resource_id'],
                    configuration=result['configuration'],
                    misconfigurations=result['misconfigurations'],
                    risk_score=result['risk_score'],
                    severity='HIGH' if result['risk_score'] >= 7 else 'MEDIUM' if result['risk_score'] >= 4 else 'LOW'
                )
                db.add(db_result)
        
        db.commit()
        return {"status": "success", "results": scan_results}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/results")
async def get_scan_results(db: Session = Depends(get_db)):
    """Get all scan results"""
    results = db.query(ScanResult).all()
    return results

@router.get("/results/{service_type}")
async def get_service_results(service_type: str, db: Session = Depends(get_db)):
    """Get scan results for a specific service"""
    results = db.query(ScanResult).filter(ScanResult.service_type == service_type).all()
    if not results:
        raise HTTPException(status_code=404, detail=f"No results found for service {service_type}")
    return results

@router.get("/results/resource/{resource_id}")
async def get_resource_results(resource_id: str, db: Session = Depends(get_db)):
    """Get scan results for a specific resource"""
    results = db.query(ScanResult).filter(ScanResult.resource_id == resource_id).all()
    if not results:
        raise HTTPException(status_code=404, detail=f"No results found for resource {resource_id}")
    return results

@router.get("/security-hub/status")
async def check_security_hub_status():
    """
    Check if AWS Security Hub is enabled in the current region
    """
    scanner = AWSScanner()
    return scanner.check_security_hub_status()
