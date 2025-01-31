# CloudMisScan

CloudMisScan is a comprehensive cloud security scanning tool designed to identify and monitor misconfigurations in AWS cloud infrastructure. It provides real-time monitoring, detailed reports, and security recommendations to help maintain a secure cloud environment.

## Features

- **Real-time Cloud Monitoring**: Continuously monitor AWS resources for security misconfigurations
- **Comprehensive Scanning**: Analyze multiple AWS services including:
  - S3 Buckets
  - IAM Policies
  - Security Groups
  - Network Configuration
- **Interactive Dashboard**: Modern Next.js frontend with real-time updates
- **Detailed Reporting**: Generate detailed reports of security findings
- **Security Recommendations**: Get actionable recommendations to fix identified issues
- **Authentication & Authorization**: Secure JWT-based authentication system
- **API Documentation**: Auto-generated FastAPI documentation

## Tech Stack

### Backend
- FastAPI (Python web framework)
- SQLAlchemy (ORM)
- JWT Authentication
- WebSocket for real-time updates
- AWS SDK (Boto3)

### Frontend
- Next.js
- TypeScript
- Tailwind CSS
- Real-time WebSocket client

## Prerequisites

- Python 3.8+
- Node.js 14+
- AWS Account with appropriate permissions
- Git

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Swayam-code/Project-CloudMisScan.git
   cd Project-CloudMisScan
   ```

2. **Set up Python virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   ```

4. **Configure environment variables**
   ```bash
   cp env.example .env
   ```
   Edit `.env` file with your AWS credentials and other configuration:
   - AWS_ACCESS_KEY_ID
   - AWS_SECRET_ACCESS_KEY
   - AWS_DEFAULT_REGION
   - JWT_SECRET_KEY
   - Other configuration variables

## Running the Application

1. **Start the backend server**
   ```bash
   uvicorn main:app --reload
   ```

2. **Start the frontend development server**
   ```bash
   cd frontend
   npm run dev
   ```

3. Access the application:
   - Frontend: http://localhost:3000
   - API Documentation: http://localhost:8000/docs
   - Alternative API Documentation: http://localhost:8000/redoc

## Project Structure

```
CloudMisScan/
├── frontend/                # Next.js frontend application
├── routes/                  # API route handlers
├── services/               # Core business logic and AWS interactions
├── models/                 # Database models
├── scripts/               # Utility scripts
├── tests/                 # Test suite
├── config/               # Configuration files
└── main.py              # FastAPI application entry point
```

## API Endpoints

- `/api/v1/auth/*` - Authentication endpoints
- `/api/v1/scan/*` - AWS scanning endpoints
- `/api/v1/reports/*` - Report generation endpoints
- `/api/v1/monitor/*` - Real-time monitoring endpoints

## Testing

Run the test suite:
```bash
pytest tests/
```

## Security

- All sensitive information is stored in environment variables
- JWT-based authentication
- CORS protection
- Input validation
- Secure WebSocket connections

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.
