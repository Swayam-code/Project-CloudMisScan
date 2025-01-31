from datetime import datetime, timedelta
from jose import JWTError, jwt
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY environment variable is not set")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    """Create a new JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

if __name__ == "__main__":
    # Create a test token
    test_data = {
        "sub": "test_user",
        "scopes": ["monitor"]
    }
    token = create_access_token(test_data)
    print("\nGenerated JWT Token:")
    print(token)
    print("\nUse this token in your WebSocket connection:")
