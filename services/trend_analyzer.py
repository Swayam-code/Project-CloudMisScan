from typing import Dict, List, Any
import boto3
from datetime import datetime, timedelta
import json
import logging
import os

class TrendAnalyzer:
    def __init__(self):
        self.data_dir = "data/history"
        os.makedirs(self.data_dir, exist_ok=True)
        self.scan_results = self._load_historical_data()

    def _load_historical_data(self) -> List[Dict[str, Any]]:
        """Load historical scan data from files"""
        try:
            results = []
            for filename in os.listdir(self.data_dir):
                if filename.endswith('.json'):
                    with open(os.path.join(self.data_dir, filename), 'r') as f:
                        results.append(json.load(f))
            logging.info(f"Loaded {len(results)} historical scan results")
            return results
        except Exception as e:
            logging.error(f"Error loading historical data: {str(e)}")
            return []

    def store_scan_results(self, results: Dict[str, Any]):
        """Store scan results with timestamp"""
        try:
            # Convert any datetime objects to ISO format strings
            def convert_dates(obj):
                if isinstance(obj, dict):
                    return {k: convert_dates(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_dates(item) for item in obj]
                elif isinstance(obj, datetime):
                    return obj.isoformat()
                return obj

            processed_results = convert_dates(results)
            timestamp = datetime.utcnow().isoformat()
            
            # Store in memory
            self.scan_results.append({
                'timestamp': timestamp,
                'results': processed_results
            })
            
            # Store on disk
            filename = f"scan_{timestamp.replace(':', '-')}.json"
            with open(os.path.join(self.data_dir, filename), 'w') as f:
                json.dump({
                    'timestamp': timestamp,
                    'results': processed_results
                }, f, indent=2)
            
            logging.info(f"Successfully stored scan results: {filename}")
            
            # Clean up old files (keep last 90 days)
            self._cleanup_old_files()
            
        except Exception as e:
            logging.error(f"Error storing scan results: {str(e)}")

    def _cleanup_old_files(self):
        """Remove scan files older than 90 days"""
        try:
            cutoff = datetime.utcnow() - timedelta(days=90)
            for filename in os.listdir(self.data_dir):
                if not filename.endswith('.json'):
                    continue
                    
                filepath = os.path.join(self.data_dir, filename)
                file_time = datetime.fromtimestamp(os.path.getctime(filepath))
                
                if file_time < cutoff:
                    os.remove(filepath)
                    logging.info(f"Removed old scan file: {filename}")
        except Exception as e:
            logging.error(f"Error cleaning up old files: {str(e)}")

    def get_historical_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get historical trends for the specified number of days"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            logging.info(f"Getting trends from {start_date} to {end_date}")
            logging.info(f"Current scan results: {len(self.scan_results)} entries")
            
            # Create initial data point if no history exists
            if not self.scan_results:
                current_scan = {
                    'date': end_date.date().isoformat(),
                    'value': 100  # Start with perfect score
                }
                return {
                    'overall': [current_scan],
                    'services': {
                        'ec2': [current_scan],
                        'rds': [current_scan],
                        's3': [current_scan],
                        'iam': [current_scan],
                        'network': [current_scan]
                    }
                }
            
            # Filter results within the date range
            filtered_results = [
                result for result in self.scan_results
                if start_date <= datetime.fromisoformat(result['timestamp']) <= end_date
            ]
            
            # Calculate scores for each service
            service_scores = {}
            overall_scores = []
            
            for result in filtered_results:
                date = datetime.fromisoformat(result['timestamp']).date().isoformat()
                
                # Count issues per service
                service_issues = {}
                total_issues = 0
                
                for service, resources in result['results'].items():
                    if service == 'compliance' or not isinstance(resources, list):
                        continue
                    
                    issues = sum(len(resource.get('misconfigurations', [])) for resource in resources)
                    service_issues[service] = issues
                    total_issues += issues
                
                # Calculate scores (100 - deductions)
                overall_score = max(0, 100 - (total_issues * 2))
                overall_scores.append({
                    'date': date,
                    'value': overall_score
                })
                
                for service in ['ec2', 'rds', 's3', 'iam', 'network']:
                    if service not in service_scores:
                        service_scores[service] = []
                    
                    score = max(0, 100 - (service_issues.get(service, 0) * 5))
                    service_scores[service].append({
                        'date': date,
                        'value': score
                    })
            
            # Sort all scores by date
            overall_scores.sort(key=lambda x: x['date'])
            for service in service_scores:
                service_scores[service].sort(key=lambda x: x['date'])
            
            logging.info(f"Generated trends: overall={len(overall_scores)} points")
            for service, scores in service_scores.items():
                logging.info(f"{service}={len(scores)} points")
            
            return {
                'overall': overall_scores,
                'services': service_scores
            }
            
        except Exception as e:
            logging.error(f"Error getting historical trends: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            return {
                'overall': [],
                'services': {
                    'ec2': [], 'rds': [], 's3': [], 'iam': [], 'network': []
                }
            }
