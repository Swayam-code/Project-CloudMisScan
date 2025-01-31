from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import Base
import logging
from dotenv import load_dotenv
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_database():
    """Set up PostgreSQL database"""
    try:
        # Get database URL from environment or use default
        load_dotenv()
        
        # Construct PostgreSQL URL
        DB_USER = "postgres"  # default PostgreSQL user
        DB_PASSWORD = input("Enter your PostgreSQL password: ")  # the password you set during installation
        DB_HOST = "localhost"
        DB_PORT = "5432"
        DB_NAME = "cloud_scan"
        
        DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Test connection
        try:
            connection = engine.connect()
            connection.close()
            logger.info("Successfully connected to PostgreSQL!")
        except Exception as e:
            logger.error(f"Error connecting to PostgreSQL: {str(e)}")
            return False
        
        # Create tables
        Base.metadata.create_all(engine)
        logger.info("Successfully created database tables!")
        
        # Update .env file
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        with open(env_path, 'r') as file:
            lines = file.readlines()
        
        with open(env_path, 'w') as file:
            for line in lines:
                if line.startswith('DATABASE_URL='):
                    file.write(f'DATABASE_URL={DATABASE_URL}\n')
                else:
                    file.write(line)
        
        logger.info("Updated DATABASE_URL in .env file")
        
        # Create a test session
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        # Test the session
        try:
            # Try a simple query
            result = session.execute("SELECT 1").scalar()
            logger.info("Database session test successful!")
        except Exception as e:
            logger.error(f"Error testing database session: {str(e)}")
            return False
        finally:
            session.close()
        
        return True
    
    except Exception as e:
        logger.error(f"Error setting up database: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Starting database setup...")
    if setup_database():
        logger.info("Database setup completed successfully!")
    else:
        logger.error("Database setup failed!")
