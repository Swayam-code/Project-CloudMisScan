from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List, Any
import json
import csv
from io import StringIO, BytesIO
from datetime import datetime
from fastapi.responses import FileResponse, StreamingResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from models.database import get_db, ScanResult, Report

router = APIRouter()

def generate_pdf_report(results: List[ScanResult]) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    )
    elements.append(Paragraph("Cloud Security Scan Report", title_style))
    elements.append(Spacer(1, 12))

    # Summary Section
    elements.append(Paragraph("Executive Summary", styles['Heading2']))
    elements.append(Spacer(1, 12))

    total_resources = len(results)
    total_misconfigs = sum(len(r.misconfigurations) for r in results)
    high_severity = sum(1 for r in results if r.severity == "HIGH")
    medium_severity = sum(1 for r in results if r.severity == "MEDIUM")
    low_severity = sum(1 for r in results if r.severity == "LOW")

    summary_data = [
        ["Total Resources Scanned", str(total_resources)],
        ["Total Misconfigurations", str(total_misconfigs)],
        ["High Severity Issues", str(high_severity)],
        ["Medium Severity Issues", str(medium_severity)],
        ["Low Severity Issues", str(low_severity)]
    ]

    summary_table = Table(summary_data, colWidths=[4*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 20))

    # Detailed Findings
    elements.append(Paragraph("Detailed Findings", styles['Heading2']))
    elements.append(Spacer(1, 12))

    for result in results:
        if result.misconfigurations:
            # Resource Header
            resource_header = f"{result.service_type} - {result.resource_id}"
            elements.append(Paragraph(resource_header, styles['Heading3']))
            elements.append(Spacer(1, 6))

            # Misconfigurations Table
            misconfig_data = [["Issue Type", "Severity", "Description"]]
            for misc in result.misconfigurations:
                misconfig_data.append([
                    misc['type'],
                    misc['severity'],
                    misc['description']
                ])

            misconfig_table = Table(misconfig_data, colWidths=[2*inch, 1.5*inch, 4*inch])
            misconfig_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))
            elements.append(misconfig_table)
            elements.append(Spacer(1, 12))

    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

def generate_json_report(results: List[ScanResult]) -> Dict:
    return {
        "scan_date": datetime.utcnow().isoformat(),
        "summary": {
            "total_resources": len(results),
            "total_misconfigurations": sum(len(r.misconfigurations) for r in results),
            "risk_levels": {
                "high": sum(1 for r in results if r.severity == "HIGH"),
                "medium": sum(1 for r in results if r.severity == "MEDIUM"),
                "low": sum(1 for r in results if r.severity == "LOW")
            }
        },
        "results": [
            {
                "service_type": r.service_type,
                "resource_id": r.resource_id,
                "misconfigurations": r.misconfigurations,
                "risk_score": r.risk_score,
                "severity": r.severity,
                "remediation_steps": r.remediation_steps
            }
            for r in results
        ]
    }

def generate_csv_report(results: List[ScanResult]) -> str:
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        "Service Type",
        "Resource ID",
        "Issue Type",
        "Severity",
        "Description",
        "Risk Score"
    ])
    
    # Write data
    for result in results:
        for misc in result.misconfigurations:
            writer.writerow([
                result.service_type,
                result.resource_id,
                misc['type'],
                misc['severity'],
                misc['description'],
                result.risk_score
            ])
    
    return output.getvalue()

@router.get("/export/{format}")
async def export_report(format: str, db: Session = Depends(get_db)):
    """Export scan results in specified format (pdf, json, csv)"""
    results = db.query(ScanResult).all()
    if not results:
        raise HTTPException(status_code=404, detail="No scan results found")

    try:
        if format.lower() == 'pdf':
            pdf_content = generate_pdf_report(results)
            return StreamingResponse(
                iter([pdf_content]),
                media_type="application/pdf",
                headers={"Content-Disposition": "attachment; filename=cloud_scan_report.pdf"}
            )
        
        elif format.lower() == 'json':
            json_content = generate_json_report(results)
            return StreamingResponse(
                iter([json.dumps(json_content, indent=2).encode()]),
                media_type="application/json",
                headers={"Content-Disposition": "attachment; filename=cloud_scan_report.json"}
            )
        
        elif format.lower() == 'csv':
            csv_content = generate_csv_report(results)
            return StreamingResponse(
                iter([csv_content.encode()]),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=cloud_scan_report.csv"}
            )
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported format. Use 'pdf', 'json', or 'csv'")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")

@router.get("/summary")
async def get_summary(db: Session = Depends(get_db)):
    """Get a summary of all scan results"""
    results = db.query(ScanResult).all()
    if not results:
        raise HTTPException(status_code=404, detail="No scan results found")

    return {
        "last_scan": max(r.scan_date for r in results),
        "total_resources": len(results),
        "services": {
            service: len([r for r in results if r.service_type == service])
            for service in set(r.service_type for r in results)
        },
        "severity_distribution": {
            "high": len([r for r in results if r.severity == "HIGH"]),
            "medium": len([r for r in results if r.severity == "MEDIUM"]),
            "low": len([r for r in results if r.severity == "LOW"])
        },
        "top_issues": [
            {
                "type": misc["type"],
                "count": sum(1 for r in results for m in r.misconfigurations if m["type"] == misc["type"]),
                "severity": misc["severity"]
            }
            for misc in sorted(
                {m for r in results for m in r.misconfigurations},
                key=lambda x: sum(1 for r in results for m in r.misconfigurations if m["type"] == x["type"]),
                reverse=True
            )[:5]
        ]
    }
