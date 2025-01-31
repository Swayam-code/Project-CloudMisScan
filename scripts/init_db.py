from models.database import Base, engine
from sqlalchemy_utils import database_exists, create_database
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize the database"""
    try:
        # Create database if it doesn't exist
        if not database_exists(engine.url):
            create_database(engine.url)
            logger.info(f"Created database at {engine.url}")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Successfully created all database tables")
        
        return True
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Starting database initialization...")
    success = init_database()
    if success:
        logger.info("Database initialization completed successfully!")
    else:
        logger.error("Database initialization failed!")
