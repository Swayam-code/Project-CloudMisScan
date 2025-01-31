import requests
import json
from datetime import datetime
import sys

def check_monitoring_status():
    """Check the current monitoring status"""
    try:
        # Set a timeout to avoid hanging
        response = requests.get('http://localhost:8000/api/v1/monitor/status', timeout=5)
        if response.status_code != 200:
            print(f"\nError: Server returned status code {response.status_code}")
            print(response.text)
            return False
            
        data = response.json()
        
        print(f"\nMonitoring Status at {datetime.now().isoformat()}:")
        print(json.dumps(data, indent=2))
        
        # Print a more user-friendly summary
        print("\nSummary:")
        print(f"- Monitoring Active: {data.get('is_running', False)}")
        print(f"- Active Connections: {data.get('active_connections', 0)}")
        print(f"- Scan Interval: {data.get('scan_interval', 'N/A')} seconds")
        if data.get('last_scan'):
            print(f"- Last Scan: {data.get('last_scan')}")
        else:
            print("- Last Scan: Never")
            
        return True
        
    except requests.exceptions.Timeout:
        print("\nError: Request timed out while trying to connect to the monitoring server.")
        print("The server might be busy or not responding.")
        return False
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to the monitoring server.")
        print("Make sure the server is running (python -m uvicorn main:app --reload)")
        return False
    except Exception as e:
        print(f"\nError checking status: {str(e)}")
        return False

if __name__ == "__main__":
    success = check_monitoring_status()
    if not success:
        sys.exit(1)
