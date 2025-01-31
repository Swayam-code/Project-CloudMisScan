from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.monitor import CloudMonitor
import json
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()
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
                command = json.loads(data)
                if command.get('action') == 'force_scan':
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
