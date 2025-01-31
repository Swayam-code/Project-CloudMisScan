from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime, timedelta
import json
from fastapi import WebSocket
from .aws_scanner import AWSScanner
import boto3
import logging

class CloudMonitor:
    def __init__(self, scan_interval: int = 300):  # Default 5 minutes
        self.scanner = AWSScanner()
        self.scan_interval = scan_interval
        self.active_connections: List[WebSocket] = []
        self.last_scan_results: Dict[str, Any] = {}
        self.is_running = False
        self.current_scan_task = None
        self._initialize_logging()
    
    def _initialize_logging(self):
        """Initialize logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('CloudMonitor')
    
    async def connect(self, websocket: WebSocket):
        """Handle new WebSocket connection"""
        # Note: websocket.accept() should be called by the route handler
        self.active_connections.append(websocket)
        self.logger.info(f"New WebSocket connection established. Total connections: {len(self.active_connections)}")
        
        # Send initial scan results if available
        if self.last_scan_results:
            await websocket.send_json({
                'type': 'initial_state',
                'data': self.last_scan_results
            })
    
    def disconnect(self, websocket: WebSocket):
        """Handle WebSocket disconnection"""
        self.active_connections.remove(websocket)
        self.logger.info(f"WebSocket connection closed. Remaining connections: {len(self.active_connections)}")
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        self.logger.debug(f"Broadcasting message: {message.get('type', 'unknown')}")
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                self.logger.error(f"Error broadcasting to client: {str(e)}")
                self.active_connections.remove(connection)
    
    async def scan_and_compare(self) -> Optional[Dict[str, Any]]:
        """Perform a scan and compare with previous results"""
        scan_start = datetime.utcnow()
        self.logger.info("Starting new scan...")
        
        try:
            # Scan each service independently to improve performance
            services_to_scan = ['s3', 'ec2', 'iam', 'rds']
            current_scan = {}
            
            for service in services_to_scan:
                try:
                    self.logger.info(f"Scanning {service}...")
                    scan_method = getattr(self.scanner, f'scan_{service}')
                    current_scan[service] = scan_method()
                    
                    # Broadcast service-specific results immediately
                    await self.broadcast({
                        'type': 'service_scan_complete',
                        'service': service,
                        'data': current_scan[service],
                        'timestamp': datetime.utcnow().isoformat()
                    })
                    
                except Exception as e:
                    self.logger.error(f"Error scanning {service}: {str(e)}")
                    current_scan[service] = []
            
            # Compare with previous results
            changes = self._compare_scans(current_scan)
            
            # Update last scan results
            self.last_scan_results = current_scan
            
            # Calculate scan duration
            scan_duration = (datetime.utcnow() - scan_start).total_seconds()
            self.logger.info(f"Scan completed in {scan_duration:.2f} seconds")
            
            if changes:
                change_summary = {
                    'type': 'changes_detected',
                    'timestamp': datetime.utcnow().isoformat(),
                    'scan_duration': scan_duration,
                    'changes': changes
                }
                await self.broadcast(change_summary)
                return change_summary
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error during scan and compare: {str(e)}")
            raise
    
    def _compare_scans(self, current_scan: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Compare current scan with previous results"""
        if not self.last_scan_results:
            return {}
            
        changes = {}
        for service, results in current_scan.items():
            previous_results = self.last_scan_results.get(service, [])
            
            # Compare current and previous results
            new_issues = []
            resolved_issues = []
            changed_issues = []
            
            current_resources = {r['resource_id']: r for r in results}
            previous_resources = {r['resource_id']: r for r in previous_results}
            
            # Find new and changed issues
            for resource_id, current in current_resources.items():
                if resource_id not in previous_resources:
                    new_issues.append(current)
                else:
                    prev = previous_resources[resource_id]
                    if current != prev:
                        changed_issues.append({
                            'resource_id': resource_id,
                            'previous': prev,
                            'current': current
                        })
            
            # Find resolved issues
            for resource_id, prev in previous_resources.items():
                if resource_id not in current_resources:
                    resolved_issues.append(prev)
            
            if new_issues or resolved_issues or changed_issues:
                changes[service] = {
                    'new_issues': new_issues,
                    'resolved_issues': resolved_issues,
                    'changed_issues': changed_issues
                }
        
        return changes
    
    async def start_monitoring(self):
        """Start the continuous monitoring process"""
        if self.is_running:
            return
        
        self.logger.info("Starting monitoring process...")
        self.is_running = True
        
        # Perform initial scan
        try:
            initial_scan = await self.scan_and_compare()
            if initial_scan:
                self.logger.info("Initial scan completed with changes detected")
            else:
                self.logger.info("Initial scan completed - no changes detected")
        except Exception as e:
            self.logger.error(f"Error during initial scan: {str(e)}")
        
        while self.is_running:
            try:
                self.current_scan_task = asyncio.create_task(self.scan_and_compare())
                await self.current_scan_task
                self.logger.info(f"Waiting {self.scan_interval} seconds until next scan")
                await asyncio.sleep(self.scan_interval)
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {str(e)}")
                await asyncio.sleep(10)  # Wait before retrying
    
    def stop_monitoring(self):
        """Stop the continuous monitoring process"""
        self.logger.info("Stopping monitoring process...")
        self.is_running = False
        if self.current_scan_task:
            self.current_scan_task.cancel()
        self.logger.info("Monitoring process stopped")
