import jwt
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

def test_jwt_secret():
    """Test that the JWT secret key is properly configured and can generate valid tokens."""
    # Load environment variables
    load_dotenv()
    
    # Get JWT secret key
    secret_key = os.getenv("JWT_SECRET_KEY")
    if not secret_key:
        print("❌ TEST FAILED: JWT_SECRET_KEY is not set in .env file")
        return False
        
    # Check that the secret key is not empty
    if len(secret_key) < 32:
        print(f"❌ TEST FAILED: JWT_SECRET_KEY is too short ({len(secret_key)} chars). Should be at least 32 chars.")
        return False
        
    # Test JWT token generation
    try:
        expires_delta = timedelta(minutes=15)
        expire = datetime.utcnow() + expires_delta
        
        # Create a test payload
        test_data = {"sub": "test_user", "exp": expire}
        
        # Generate token
        token = jwt.encode(test_data, secret_key, algorithm="HS256")
        
        # Verify token
        decoded = jwt.decode(token, secret_key, algorithms=["HS256"])
        
        if decoded["sub"] == "test_user":
            print("✅ TEST PASSED: JWT token generation and verification worked correctly")
            return True
        else:
            print(f"❌ TEST FAILED: JWT token decoded incorrectly. Expected 'test_user', got '{decoded['sub']}'")
            return False
            
    except Exception as e:
        print(f"❌ TEST FAILED: Error during JWT operations: {str(e)}")
        return False
        
if __name__ == "__main__":
    print("Testing JWT configuration...")
    success = test_jwt_secret()
    
    if success:
        print("All JWT tests passed!")
    else:
        print("JWT tests failed. Please check your configuration.") 