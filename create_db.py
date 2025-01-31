from sqlalchemy import create_engine, text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_database():
    try:
        # Connect to default postgres database first
        engine = create_engine('postgresql://postgres:swayampk@908@localhost:5432/postgres')
        
        # Create a connection
        with engine.connect() as conn:
            # Disconnect all users from the database if it exists
            conn.execute(text("""
                SELECT pg_terminate_backend(pid) 
                FROM pg_stat_activity 
                WHERE datname = 'cloud_scan'
            """))
            conn.execute(text("commit"))
            
            # Drop database if exists
            conn.execute(text("DROP DATABASE IF EXISTS cloud_scan"))
            conn.execute(text("commit"))
            
            # Create database
            conn.execute(text("CREATE DATABASE cloud_scan"))
            conn.execute(text("commit"))
            
        logger.info("Successfully created database 'cloud_scan'")
        
        # Test connection to new database
        new_engine = create_engine('postgresql://postgres:swayampk@908@localhost:5432/cloud_scan')
        with new_engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            logger.info("Successfully connected to new database!")
        
        return True
    except Exception as e:
        logger.error(f"Error creating database: {str(e)}")
        return False

if __name__ == "__main__":
    password = input("Enter your PostgreSQL password: ")
    
    # Replace password in the script
    with open(__file__, 'r') as file:
        content = file.read()
    
    updated_content = content.replace('swayampk@908', password)
    
    with open(__file__, 'w') as file:
        file.write(updated_content)
    
    logger.info("Starting database creation...")
    if create_database():
        logger.info("""
Database setup completed successfully!
You can now update your .env file with:
DATABASE_URL=postgresql://postgres:{}@localhost:5432/cloud_scan
""".format(password))
    else:
        logger.error("Database creation failed!")
