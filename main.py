from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import os
import logging
from jose import JWTError, jwt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from models.database import engine, Base
from routes import aws_scan, reports, auth, monitor
from services.monitor import CloudMonitor

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Database Configuration
DATABASE_URL = "sqlite:///./cloud_scan.db"

# AWS Configuration
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')

# JWT Configuration
SECRET_KEY = os.getenv('JWT_SECRET_KEY')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = 8000
API_DEBUG = True

# Security Configuration
CORS_ORIGINS = ["http://localhost:3000"]
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# Scan Configuration
SCAN_INTERVAL_MINUTES = 60
MAX_CONCURRENT_SCANS = 3

# Report Configuration
REPORT_RETENTION_DAYS = 30
PDF_REPORT_TEMPLATE = "default"

# Create database tables
Base.metadata.create_all(bind=engine)

# Create monitor instance
monitor_instance = CloudMonitor()

app = FastAPI(
    title="Cloud Misconfiguration Scanner",
    description="AWS Cloud Configuration Monitoring Tool",
    version="1.0.0"
)

# Get CORS origins from environment variable
cors_origins = json.loads(os.getenv("CORS_ORIGINS", json.dumps(CORS_ORIGINS)))

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_token_from_header(websocket: WebSocket) -> Optional[str]:
    """Extract JWT token from WebSocket headers"""
    auth_header = websocket.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    return auth_header.split(" ")[1]

async def verify_token(websocket: WebSocket) -> bool:
    """Verify JWT token from WebSocket connection"""
    token = await get_token_from_header(websocket)
    if not token:
        logger.error("No token found in WebSocket headers")
        return False
        
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            logger.error("No username found in token")
            return False
            
        # Verify scopes if needed
        scopes = payload.get("scopes", [])
        if "monitor" not in scopes:
            logger.error("Token does not have monitor scope")
            return False
            
        return True
        
    except JWTError as e:
        logger.error(f"JWT verification failed: {str(e)}")
        return False

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time monitoring updates"""
    logger.debug(f"WebSocket connection request received at {websocket.url.path}")
    
    # Verify JWT token
    if not await verify_token(websocket):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    try:
        logger.debug("Accepting WebSocket connection...")
        await websocket.accept()
        logger.info("WebSocket connection accepted")
        
        await monitor_instance.connect(websocket)
        logger.info("WebSocket connection registered with monitor")
        
        # Start monitoring if not already running
        if not monitor_instance.is_running:
            logger.info("Starting monitoring via WebSocket connection")
            await monitor_instance.start_monitoring()
        
        # Keep the connection alive and handle any client messages
        while True:
            try:
                data = await websocket.receive_text()
                logger.debug(f"Received message: {data}")
                
                # Handle any client commands here
                command = json.loads(data)
                if command.get('action') == 'force_scan':
                    logger.info("Received force_scan command")
                    changes = await monitor_instance.scan_and_compare()
                    if changes:
                        await websocket.send_json(changes)
                        
            except WebSocketDisconnect:
                logger.info("WebSocket disconnected")
                monitor_instance.disconnect(websocket)
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
        monitor_instance.disconnect(websocket)
        logger.info("WebSocket connection closed")

# Print all registered routes
@app.on_event("startup")
async def startup_event():
    logger.debug("Available routes:")
    for route in app.routes:
        if hasattr(route, 'methods'):
            logger.debug(f"Route: {route.path} [{','.join(route.methods)}]")
        else:
            logger.debug(f"WebSocket Route: {route.path}")

# Include routers - WebSocket route must be registered first
logger.debug("Registering routes...")
app.include_router(monitor.router, prefix="/api/v1/monitor", tags=["Real-time Monitoring"])
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(aws_scan.router, prefix="/api/v1/scan", tags=["AWS Scanning"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])

@app.get("/")
async def root():
    return {"message": "Cloud Misconfiguration Scanner API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
