import json
import csv
from typing import Dict, Any, List
from datetime import datetime
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

class ExportHandler:
    def __init__(self, output_dir: str = "reports"):
        """Initialize ExportHandler with output directory"""
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def export_json(self, data: Dict[str, Any], filename: str = None) -> str:
        """Export data to JSON format"""
        if filename is None:
            filename = f"scan_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        return filepath

    def export_csv(self, data: Dict[str, Any], filename: str = None) -> str:
        """Export data to CSV format"""
        if filename is None:
            filename = f"scan_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Flatten the data structure
        flattened_data = self._flatten_data(data)
        
        if not flattened_data:
            # Create empty file with headers if no data
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Service', 'Resource ID', 'Issue Type', 'Severity', 'Description',
                               'Framework', 'Control ID', 'Status'])
            return filepath
        
        # Get all possible keys from flattened data
        fieldnames = set()
        for item in flattened_data:
            fieldnames.update(item.keys())
        fieldnames = sorted(list(fieldnames))
        
        # Write to CSV
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in flattened_data:
                # Ensure all fields exist in each row
                for field in fieldnames:
                    if field not in row:
                        row[field] = ''
                writer.writerow(row)
        
        return filepath

    def export_pdf(self, data: Dict[str, Any], filename: str = None) -> str:
        """Export data to PDF format"""
        if filename is None:
            filename = f"scan_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        )
        elements.append(Paragraph("Cloud Misconfiguration Scan Report", title_style))
        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
        elements.append(Spacer(1, 20))

        # Add compliance summary
        if 'compliance' in data:
            elements.append(Paragraph("Compliance Summary", styles['Heading2']))
            elements.append(Spacer(1, 10))
            
            for framework, results in data['compliance'].items():
                elements.append(Paragraph(f"{framework.upper()} Compliance", styles['Heading3']))
                
                # Calculate compliance statistics
                total_controls = len(results['controls'])
                passed = len([c for c in results['controls'] if c['status'] == 'PASS'])
                failed = len([c for c in results['controls'] if c['status'] == 'FAIL'])
                
                # Create summary table
                summary_data = [
                    ['Total Controls', 'Passed', 'Failed', 'Compliance Score'],
                    [
                        str(total_controls),
                        str(passed),
                        str(failed),
                        f"{(passed/total_controls*100):.1f}%" if total_controls > 0 else "N/A"
                    ]
                ]
                
                summary_table = Table(summary_data)
                summary_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(summary_table)
                elements.append(Spacer(1, 20))

        # Add misconfigurations
        if any(key in data for key in ['s3', 'ec2', 'iam', 'rds', 'network']):
            elements.append(Paragraph("Misconfiguration Details", styles['Heading2']))
            elements.append(Spacer(1, 10))
            
            for service in ['s3', 'ec2', 'iam', 'rds', 'network']:
                if service in data:
                    elements.append(Paragraph(f"{service.upper()} Misconfigurations", styles['Heading3']))
                    
                    misconfigs = data[service]
                    if misconfigs:
                        table_data = [['Resource', 'Issue', 'Severity']]
                        for item in misconfigs:
                            for issue in item.get('misconfigurations', []):
                                table_data.append([
                                    item.get('resource_id', 'N/A'),
                                    issue.get('description', 'N/A'),
                                    issue.get('severity', 'N/A')
                                ])
                        
                        if len(table_data) > 1:  # Only create table if there are issues
                            table = Table(table_data)
                            table.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                ('FONTSIZE', (0, 0), (-1, 0), 12),
                                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                                ('FONTSIZE', (0, 1), (-1, -1), 10),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black)
                            ]))
                            elements.append(table)
                            elements.append(Spacer(1, 20))
                        else:
                            elements.append(Paragraph("No issues found", styles["Normal"]))
                            elements.append(Spacer(1, 10))

        # Build PDF
        doc.build(elements)
        return filepath

    def _flatten_data(self, data: Dict[str, Any], prefix: str = '') -> List[Dict[str, Any]]:
        """Flatten nested dictionary structure for CSV export"""
        flattened = []
        
        # Handle compliance data
        if 'compliance' in data:
            for framework, results in data['compliance'].items():
                for control in results['controls']:
                    row = {
                        'Framework': framework.upper(),
                        'Control ID': control['control_id'],
                        'Resource': control['resource'],
                        'Status': control['status'],
                        'Description': control['description']
                    }
                    flattened.append(row)

        # Handle misconfiguration data
        for service in ['s3', 'ec2', 'iam', 'rds', 'network']:
            if service in data:
                for item in data[service]:
                    for issue in item.get('misconfigurations', []):
                        row = {
                            'Service': service.upper(),
                            'Resource ID': item.get('resource_id', 'N/A'),
                            'Issue Type': issue.get('type', 'N/A'),
                            'Severity': issue.get('severity', 'N/A'),
                            'Description': issue.get('description', 'N/A')
                        }
                        flattened.append(row)

        return flattened
