from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List, Any
from datetime import datetime
import logging

from models.database import get_db, ScanResult
from services.aws_scanner import AWSScanner

router = APIRouter()
scanner = AWSScanner()

@router.post("/start")
async def start_scan(service_type: str = None, db: Session = Depends(get_db)):
    """
    Start a new AWS configuration scan.
    If service_type is provided, only scan that specific service.
    Otherwise, scan all services.
    """
    try:
        if service_type:
            scan_results = scanner.scan_service(service_type)
            # Convert single service results to the same format as scan_all
            results = {service_type: scan_results}
        else:
            results = scanner.scan_all()
        
        # Store results in database
        for service, service_results in results.items():
            if not isinstance(service_results, list):
                service_results = [service_results]
                
            for result in service_results:
                risk_score = result.get('risk_score', 0)
                db_result = ScanResult(
                    service_type=service,
                    resource_id=result.get('resource_id', ''),
                    configuration=result.get('configuration', {}),
                    misconfigurations=result.get('misconfigurations', []),
                    risk_score=risk_score,
                    severity='HIGH' if risk_score >= 7 else 'MEDIUM' if risk_score >= 4 else 'LOW',
                    scan_date=datetime.utcnow()
                )
                db.add(db_result)
        
        db.commit()
        return {"status": "success", "results": results}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"Scan failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/results")
async def get_scan_results(db: Session = Depends(get_db)):
    """Get all scan results"""
    results = db.query(ScanResult).order_by(ScanResult.scan_date.desc()).all()
    return results

@router.get("/results/{service_type}")
async def get_service_results(service_type: str, db: Session = Depends(get_db)):
    """Get scan results for a specific service"""
    results = db.query(ScanResult).filter(
        ScanResult.service_type.ilike(service_type)
    ).order_by(ScanResult.scan_date.desc()).all()
    
    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"No results found for service {service_type}"
        )
    return results

@router.get("/results/resource/{resource_id}")
async def get_resource_results(resource_id: str, db: Session = Depends(get_db)):
    """Get scan results for a specific resource"""
    results = db.query(ScanResult).filter(
        ScanResult.resource_id.ilike(resource_id)
    ).order_by(ScanResult.scan_date.desc()).all()
    
    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"No results found for resource {resource_id}"
        )
    return results

@router.get("/security-hub/status")
async def check_security_hub_status():
    """Check if AWS Security Hub is enabled in the current region"""
    try:
        securityhub = scanner.session.client('securityhub')
        try:
            response = securityhub.get_enabled_standards()
            return {
                "status": "enabled",
                "standards": response.get('StandardsSubscriptions', [])
            }
        except securityhub.exceptions.InvalidAccessException:
            return {"status": "disabled"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check Security Hub status: {str(e)}"
        )
