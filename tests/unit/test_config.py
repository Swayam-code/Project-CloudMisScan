from pydantic_settings import BaseSettings
import os

class TestSettings(BaseSettings):
    def test_aws_credentials(self):
        """Test if AWS credentials are properly configured"""
        aws_vars = {
            'AWS_ACCESS_KEY_ID': os.getenv('AWS_ACCESS_KEY_ID'),
            'AWS_SECRET_ACCESS_KEY': os.getenv('AWS_SECRET_ACCESS_KEY'),
            'AWS_REGION': os.getenv('AWS_REGION', 'us-east-1')
        }
        missing = [k for k, v in aws_vars.items() if not v]
        return {
            'configured': len(missing) == 0,
            'missing': missing
        }
    
    def test_database_connection(self):
        """Test database connection string"""
        db_url = os.getenv('DATABASE_URL', 'sqlite:///./cloud_scan.db')
        return {
            'configured': bool(db_url),
            'url': db_url
        }
    
    def test_jwt_settings(self):
        """Test JWT configuration"""
        jwt_vars = {
            'SECRET_KEY': os.getenv('SECRET_KEY'),
            'ALGORITHM': os.getenv('ALGORITHM', 'HS256'),
            'ACCESS_TOKEN_EXPIRE_MINUTES': os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30')
        }
        missing = [k for k, v in jwt_vars.items() if not v]
        return {
            'configured': len(missing) == 0,
            'missing': missing
        }
    
    def test_monitoring_settings(self):
        """Test monitoring configuration"""
        scan_interval = os.getenv('SCAN_INTERVAL', '300')
        return {
            'configured': bool(scan_interval),
            'scan_interval': scan_interval
        }
    
    def run_all_tests(self):
        """Run all configuration tests"""
        return {
            'aws': self.test_aws_credentials(),
            'database': self.test_database_connection(),
            'jwt': self.test_jwt_settings(),
            'monitoring': self.test_monitoring_settings()
        }

if __name__ == '__main__':
    settings = TestSettings()
    results = settings.run_all_tests()
    print("\nConfiguration Test Results:")
    print("-" * 50)
    
    for category, result in results.items():
        print(f"\n{category.upper()} Configuration:")
        if result.get('configured'):
            print("✓ Properly configured")
        else:
            print("✗ Missing configuration:")
            if 'missing' in result:
                for item in result['missing']:
                    print(f"  - {item}")
            elif 'url' in result:
                print(f"  Using default: {result['url']}")
