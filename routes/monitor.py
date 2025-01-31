from fastapi import APIRouter, WebSocket, WebSocketDisconnect, BackgroundTasks, HTTPException, status
from services.monitor import CloudMonitor
from typing import Dict, Any
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()  # Remove prefix, it's handled in main.py
monitor = CloudMonitor()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time monitoring updates"""
    logger.debug(f"WebSocket connection request received at {websocket.url.path}")
    
    try:
        logger.debug("Accepting WebSocket connection...")
        await websocket.accept()
        logger.info("WebSocket connection accepted")
        
        await monitor.connect(websocket)
        logger.info("WebSocket connection registered with monitor")
        
        # Start monitoring if not already running
        if not monitor.is_running:
            logger.info("Starting monitoring via WebSocket connection")
            await monitor.start_monitoring()
        
        # Keep the connection alive and handle any client messages
        while True:
            try:
                data = await websocket.receive_text()
                logger.debug(f"Received message: {data}")
                
                # Handle any client commands here
                if data == "force_scan":
                    logger.info("Received force_scan command")
                    changes = await monitor.scan_and_compare()
                    if changes:
                        await websocket.send_json(changes)
                        
            except WebSocketDisconnect:
                logger.info("WebSocket disconnected")
                monitor.disconnect(websocket)
                break
                
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {str(e)}")
                try:
                    await websocket.send_json({
                        'error': str(e)
                    })
                except:
                    break
                    
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        monitor.disconnect(websocket)
        logger.info("WebSocket connection closed")

@router.post("/start")
async def start_monitoring(background_tasks: BackgroundTasks):
    """Start the monitoring process"""
    if not monitor.is_running:
        background_tasks.add_task(monitor.start_monitoring)
        return {"message": "Monitoring started"}
    return {"message": "Monitoring is already running"}

@router.post("/stop")
async def stop_monitoring():
    """Stop the monitoring process"""
    monitor.stop_monitoring()
    return {"message": "Monitoring stopped"}

@router.get("/status")
async def get_monitoring_status():
    """Get the current monitoring status"""
    return {
        "is_running": monitor.is_running,
        "active_connections": len(monitor.active_connections),
        "scan_interval": monitor.scan_interval,
        "last_scan": monitor.last_scan_results.get("timestamp") if monitor.last_scan_results else None
    }

@router.post("/scan")
async def trigger_scan():
    """Trigger an immediate scan"""
    if not monitor.is_running:
        return {"error": "Monitoring is not running"}
    
    changes = await monitor.scan_and_compare()
    return {
        "message": "Scan completed",
        "changes": changes,
        "timestamp": datetime.now().isoformat()
    }
