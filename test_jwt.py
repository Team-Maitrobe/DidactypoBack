import jwt
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

def test_jwt_secret():
    """
    Test that the JWT secret key is properly configured and can generate valid tokens.
    
    This test verifies:
    1. JWT_SECRET_KEY exists in the .env file
    2. The secret key is long enough to be secure
    3. JWT tokens can be properly generated and verified
    4. Token payload data is correctly preserved
    """
    print("\n" + "=" * 70)
    print("JWT SECRET CONFIGURATION TEST".center(70))
    print("=" * 70)
    
    # Load environment variables
    load_dotenv()
    print("\n📋 Step 1: Checking environment variables...")
    
    # Get JWT secret key
    secret_key = os.getenv("JWT_SECRET_KEY")
    if not secret_key:
        print("❌ TEST FAILED: JWT_SECRET_KEY is not set in .env file")
        print("   Make sure you have created a .env file with JWT_SECRET_KEY defined")
        return False
    else:
        print(f"✅ JWT_SECRET_KEY found in environment: {secret_key[:5]}...{secret_key[-5:]} (first/last 5 chars)")
        
    # Check that the secret key is not empty and long enough
    if len(secret_key) < 32:
        print(f"❌ TEST FAILED: JWT_SECRET_KEY is too short ({len(secret_key)} chars). Should be at least 32 chars.")
        print("   Generate a new key using: python -c \"import secrets; print(secrets.token_hex(32))\"")
        return False
    else:
        print(f"✅ JWT_SECRET_KEY length is good: {len(secret_key)} characters (min required: 32)")
        
    # Test JWT token generation
    print("\n📋 Step 2: Testing JWT token generation and verification...")
    try:
        # Create token payload with expiration
        expires_delta = timedelta(minutes=15)
        expire = datetime.utcnow() + expires_delta
        
        # Create a test payload
        test_data = {
            "sub": "test_user",
            "exp": expire,
            "roles": ["user"],
            "iat": datetime.utcnow()
        }
        
        print(f"\n📊 Test payload data:")
        print(json.dumps(test_data, default=str, indent=2))
        
        # Generate token
        print("\n📋 Step 3: Generating JWT token...")
        token = jwt.encode(test_data, secret_key, algorithm="HS256")
        print(f"✅ Token generated successfully: {token[:20]}... (first 20 chars)")
        
        # Verify token
        print("\n📋 Step 4: Verifying JWT token...")
        decoded = jwt.decode(token, secret_key, algorithms=["HS256"])
        
        print(f"\n📊 Decoded token data:")
        print(json.dumps(decoded, default=str, indent=2))
        
        if decoded["sub"] == "test_user":
            print("\n✅ TEST PASSED: JWT token generation and verification worked correctly")
            print("   - Token was successfully generated with the secret key")
            print("   - Token was successfully decoded with the same key")
            print("   - Token payload data was preserved correctly")
            return True
        else:
            print(f"\n❌ TEST FAILED: JWT token decoded incorrectly. Expected 'test_user', got '{decoded['sub']}'")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST FAILED: Error during JWT operations: {str(e)}")
        print(f"   Exception type: {type(e).__name__}")
        return False
        
if __name__ == "__main__":
    print("Running JWT configuration and token generation test...")
    success = test_jwt_secret()
    
    if success:
        print("\n🎉 All JWT tests passed! The JWT authentication system is properly configured.")
    else:
        print("\n❌ JWT tests failed. Please check your configuration and try again.")