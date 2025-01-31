import os
from pathlib import Path
from dotenv import load_dotenv
import secrets

# Load environment variables
load_dotenv()

def update_env_file():
    env_path = Path('.env')
    
    # Read existing content
    if env_path.exists():
        with open(env_path, 'r') as f:
            lines = f.readlines()
    else:
        lines = []
    
    # Remove existing SECRET_KEY if present
    lines = [line for line in lines if not line.startswith('SECRET_KEY=')]
    
    # Generate a secure random key if not present
    secret_key = os.getenv("JWT_SECRET_KEY")
    if not secret_key:
        secret_key = secrets.token_urlsafe(32)
    lines.append(f'SECRET_KEY={secret_key}\n')
    
    # Write back to file
    with open(env_path, 'w') as f:
        f.writelines(lines)
    
    print("SECRET_KEY has been added to .env file")

if __name__ == '__main__':
    update_env_file()
