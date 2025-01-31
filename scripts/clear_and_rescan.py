import os
import shutil
import logging
from services.aws_scanner import AWSScanner
from services.trend_analyzer import TrendAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_and_rescan():
    # Clear cached data
    data_dir = "data/history"
    if os.path.exists(data_dir):
        logger.info(f"Clearing cached data from {data_dir}")
        shutil.rmtree(data_dir)
        os.makedirs(data_dir)
    
    # Initialize services
    scanner = AWSScanner()
    trend_analyzer = TrendAnalyzer()
    
    # Run fresh scan
    logger.info("Running fresh AWS scan...")
    scan_results = scanner.scan_all_services()
    
    # Store new results
    logger.info("Storing new scan results...")
    trend_analyzer.store_scan_results(scan_results)
    
    logger.info("Scan complete. Please refresh the dashboard to see updated results.")

if __name__ == '__main__':
    clear_and_rescan()
