from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from services.aws_scanner import AWSScanner
from services.trend_analyzer import TrendAnalyzer
from services.export_handler import ExportHandler
from services.notification_service import NotificationService
from datetime import datetime, timedelta
import json
import logging
import os
import traceback
from dotenv import load_dotenv

# Configure logging with more detail
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Debug AWS credentials
logger.info("AWS Configuration:")
logger.info(f"Access Key ID exists: {bool(os.getenv('AWS_ACCESS_KEY_ID'))}")
logger.info(f"Secret Access Key exists: {bool(os.getenv('AWS_SECRET_ACCESS_KEY'))}")
logger.info(f"Region: {os.getenv('AWS_DEFAULT_REGION', 'not set')}")

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://localhost:3001"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

try:
    aws_scanner = AWSScanner()
    trend_analyzer = TrendAnalyzer()
    export_handler = ExportHandler()
    notification_service = NotificationService()
    logger.info("Successfully initialized all services")
except Exception as e:
    logger.error(f"Failed to initialize services: {str(e)}\n{traceback.format_exc()}")
    raise

@app.route('/')
def index():
    return jsonify({
        'status': 'ok',
        'message': 'CloudMisScan API is running',
        'endpoints': [
            '/api/dashboard',
            '/api/export',
            '/api/notify'
        ]
    })

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_data():
    try:
        days = int(request.args.get('days', 30))
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        logger.info(f"Fetching dashboard data for last {days} days")

        # Get latest scan results
        try:
            logger.info("Starting AWS service scan...")
            scan_results = aws_scanner.scan_all_services()
            logger.info("Successfully completed AWS service scan")
        except Exception as e:
            logger.error(f"Failed to scan AWS services: {str(e)}\n{traceback.format_exc()}")
            return jsonify({'error': 'Failed to scan AWS services. Please check your AWS credentials.'}), 500
        
        # Store scan results
        try:
            logger.info("Storing scan results...")
            trend_analyzer.store_scan_results(scan_results)
            logger.info("Successfully stored scan results")
        except Exception as e:
            logger.error(f"Failed to store scan results: {str(e)}\n{traceback.format_exc()}")
            # Continue even if storage fails
        
        # Get historical trends
        try:
            logger.info(f"Retrieving historical trends for last {days} days...")
            trends = trend_analyzer.get_historical_trends(days)
            logger.info(f"Successfully retrieved trends with {len(trends.get('overall', []))} data points")
        except Exception as e:
            logger.error(f"Failed to get historical trends: {str(e)}\n{traceback.format_exc()}")
            trends = {
                'overall': [],
                'services': {
                    'ec2': [], 'rds': [], 's3': [], 'iam': [], 'network': []
                }
            }
        
        # Get compliance data
        try:
            logger.info("Fetching compliance data...")
            compliance_data = aws_scanner.compliance_checker.get_compliance_data()
            logger.info("Successfully retrieved compliance data")
        except Exception as e:
            logger.error(f"Failed to get compliance data: {str(e)}\n{traceback.format_exc()}")
            compliance_data = {'error': 'Failed to fetch compliance data'}

        # Get service-specific data
        services_data = {
            service: resources
            for service, resources in scan_results.items()
            if service in ['s3', 'ec2', 'iam', 'rds', 'network']
        }

        response_data = {
            'compliance': compliance_data,
            'trends': trends,
            'services': services_data
        }
        
        logger.info("Successfully prepared dashboard response")
        return jsonify(response_data)

    except Exception as e:
        logger.error(f"Dashboard endpoint error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'An unexpected error occurred while fetching dashboard data'}), 500

@app.route('/api/export', methods=['GET'])
def export_data():
    try:
        export_format = request.args.get('format', 'json')
        if export_format not in ['json', 'csv', 'pdf']:
            return jsonify({'error': 'Invalid export format'}), 400

        # Get latest scan results
        scan_results = aws_scanner.scan_all_services()
        
        if export_format == 'json':
            return jsonify(scan_results)
        elif export_format == 'csv':
            csv_file = export_handler.export_to_csv(scan_results)
            return send_file(csv_file, mimetype='text/csv', as_attachment=True, download_name='scan_results.csv')
        else:  # pdf
            pdf_file = export_handler.export_to_pdf(scan_results)
            return send_file(pdf_file, mimetype='application/pdf', as_attachment=True, download_name='scan_results.pdf')

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notify', methods=['POST'])
def send_notification():
    try:
        platform = request.json.get('platform')
        if platform not in ['slack', 'teams']:
            return jsonify({'error': 'Invalid platform'}), 400

        # Get latest scan results
        scan_results = aws_scanner.scan_all_services()
        
        # Get recent changes
        changes = trend_analyzer.get_recent_changes()

        # Send notification
        if platform == 'slack':
            success = notification_service.notify_scan_results(scan_results, 'slack')
            if changes:
                notification_service.notify_changes(changes, 'slack')
        else:  # teams
            success = notification_service.notify_scan_results(scan_results, 'teams')
            if changes:
                notification_service.notify_changes(changes, 'teams')

        if success:
            return jsonify({'message': f'Notification sent to {platform}'})
        else:
            return jsonify({'error': f'Failed to send notification to {platform}'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
