import asyncio
import websockets
import boto3
import json
import time
from datetime import datetime
from dotenv import load_dotenv
import os
import requests
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True
)
logger = logging.getLogger('TestMonitoring')

# Add console handler for immediate output
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(message)s')
console.setFormatter(formatter)
logger.addHandler(console)

async def connect_websocket():
    """Connect to the monitoring WebSocket endpoint"""
    uri = "ws://localhost:8000/api/v1/monitor/ws"
    max_retries = 5
    retry_delay = 3

    # Get JWT token
    from generate_token import create_access_token
    token = create_access_token({"sub": "test_user", "scopes": ["monitor"]})

    for attempt in range(max_retries):
        try:
            print(f"\nAttempting WebSocket connection (attempt {attempt + 1}/{max_retries})...")
            headers = {"Authorization": f"Bearer {token}"}
            
            async with websockets.connect(uri, extra_headers=headers) as websocket:
                print("Connected to WebSocket")
                logger.info("Connected to WebSocket")
                
                # Send initial message
                await websocket.send(json.dumps({"action": "start_monitoring"}))
                
                while True:
                    try:
                        message = await websocket.recv()
                        data = json.loads(message)
                        logger.info(f"Received: {data}")
                        
                        # Pretty print the received data
                        print("\nReceived update:")
                        message_type = data.get('type', 'unknown')
                        
                        if message_type == 'service_scan_complete':
                            service = data.get('service', 'unknown')
                            scan_data = data.get('data', [])
                            print(f"Service scan completed: {service}")
                            print(f"Found {len(scan_data)} resources")
                            
                            # Print misconfigurations if any
                            for resource in scan_data:
                                if resource.get('misconfigurations'):
                                    print(f"Misconfigurations found in {resource['resource_id']}:")
                                    for issue in resource['misconfigurations']:
                                        print(f"- {issue['type']}: {issue['description']}")
                        
                        elif message_type == 'changes_detected':
                            changes = data.get('changes', {})
                            scan_duration = data.get('scan_duration', 0)
                            print(f"Changes detected (scan took {scan_duration:.2f} seconds):")
                            
                            for service, service_changes in changes.items():
                                print(f"\n{service} changes:")
                                if service_changes.get('new_issues'):
                                    print(f"New issues: {len(service_changes['new_issues'])}")
                                if service_changes.get('resolved_issues'):
                                    print(f"Resolved issues: {len(service_changes['resolved_issues'])}")
                                if service_changes.get('changed_issues'):
                                    print(f"Changed issues: {len(service_changes['changed_issues'])}")
                        
                        else:
                            print(f"Message type: {message_type}")
                            print(json.dumps(data, indent=2))
                        
                        if "error" in data:
                            logger.error(f"Error from server: {data['error']}")
                            break
                            
                    except websockets.exceptions.ConnectionClosed:
                        logger.warning("WebSocket connection closed")
                        break
                        
        except Exception as e:
            logger.error(f"Connection attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                logger.error("Failed to connect after all retries")
                raise

async def cleanup_resources(bucket_name: str):
    """Clean up test resources"""
    if not bucket_name:
        return
        
    print("\nCleaning up resources...")
    try:
        s3 = boto3.client('s3')
        
        # Delete all objects
        try:
            objects = s3.list_objects_v2(Bucket=bucket_name).get('Contents', [])
            if objects:
                s3.delete_objects(
                    Bucket=bucket_name,
                    Delete={'Objects': [{'Key': obj['Key']} for obj in objects]}
                )
        except Exception as e:
            print(f"Error deleting objects: {str(e)}")
            logger.error(f"Error deleting objects: {str(e)}")
        
        # Delete bucket
        try:
            s3.delete_bucket(Bucket=bucket_name)
            print(f"Cleaned up test bucket: {bucket_name}")
        except Exception as e:
            print(f"Error deleting bucket: {str(e)}")
            logger.error(f"Error deleting bucket: {str(e)}")
            
    except Exception as e:
        print(f"Error during cleanup: {str(e)}")
        logger.error(f"Error during cleanup: {str(e)}")

async def main():
    try:
        # Start monitoring
        print("\nStarting monitoring...")
        response = requests.post('http://localhost:8000/api/v1/monitor/start')
        print(f"Started monitoring: {response.json()}")
    except Exception as e:
        print(f"Error starting monitoring: {str(e)}")
        logger.error(f"Error starting monitoring: {str(e)}")
    
    # Start WebSocket connection
    websocket_task = asyncio.create_task(connect_websocket())
    
    # Create test resources
    bucket_name = create_test_resources()
    
    if bucket_name:
        print(f"\nTest bucket created: {bucket_name}")
        print("Monitoring for changes... (Press Ctrl+C to exit)")
        
        try:
            # Keep the script running to receive updates
            await asyncio.sleep(60)  # Monitor for 1 minute
        except KeyboardInterrupt:
            print("\nStopping test...")
        finally:
            # Clean up
            await cleanup_resources(bucket_name)
    
    # Cancel WebSocket task
    websocket_task.cancel()
    try:
        await websocket_task
    except asyncio.CancelledError:
        pass

def create_test_resources():
    """Create test AWS resources with various configurations"""
    print("\nCreating test resources...")
    s3 = boto3.client('s3')
    bucket_name = f"cloudmisscan-test-{int(time.time())}"
    
    try:
        # Create bucket
        print(f"\nCreating bucket: {bucket_name}")
        s3.create_bucket(Bucket=bucket_name)
        print("Bucket created successfully")
        
        # Wait for bucket to be available
        time.sleep(5)
        
        # Make some configuration changes
        print("\nMaking configuration changes...")
        
        try:
            # 1. Enable versioning
            s3.put_bucket_versioning(
                Bucket=bucket_name,
                VersioningConfiguration={'Status': 'Enabled'}
            )
            print("Enabled versioning")
        except Exception as e:
            print(f"Error enabling versioning: {str(e)}")
        
        time.sleep(5)
        
        try:
            # 2. Enable encryption
            s3.put_bucket_encryption(
                Bucket=bucket_name,
                ServerSideEncryptionConfiguration={
                    'Rules': [{
                        'ApplyServerSideEncryptionByDefault': {
                            'SSEAlgorithm': 'AES256'
                        }
                    }]
                }
            )
            print("Enabled encryption")
        except Exception as e:
            print(f"Error enabling encryption: {str(e)}")
        
        time.sleep(5)
        
        # We'll skip logging configuration as it requires a valid target bucket
        print("Skipping logging configuration (requires existing target bucket)")
        
        return bucket_name
        
    except Exception as e:
        print(f"Error creating test resources: {str(e)}")
        return None

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Test stopped by user")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        logger.error(f"Unexpected error: {str(e)}")
