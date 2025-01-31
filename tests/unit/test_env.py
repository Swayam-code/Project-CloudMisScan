from dotenv import load_dotenv
import os

load_dotenv()

def test_env_vars():
    # Test database URL
    print("\nDatabase URL:", os.getenv("DATABASE_URL", "Not set"))
    
    # Test AWS Region (safe to show)
    print("AWS Region:", os.getenv("AWS_DEFAULT_REGION", "Not set"))
    
    # Test if AWS credentials are set (without showing them)
    aws_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY")
    print("\nAWS Credentials:")
    print("AWS_ACCESS_KEY_ID:", "Set" if aws_key else "Not set")
    print("AWS_SECRET_ACCESS_KEY:", "Set" if aws_secret else "Not set")
    
    # Test if JWT secret is set (without showing it)
    jwt_secret = os.getenv("JWT_SECRET_KEY")
    print("\nJWT Configuration:")
    print("JWT_SECRET_KEY:", "Set" if jwt_secret else "Not set")
    print("JWT_ALGORITHM:", os.getenv("JWT_ALGORITHM", "Not set"))
    
    # Test API configuration
    print("\nAPI Configuration:")
    print("API_HOST:", os.getenv("API_HOST", "Not set"))
    print("API_PORT:", os.getenv("API_PORT", "Not set"))

if __name__ == "__main__":
    test_env_vars()
