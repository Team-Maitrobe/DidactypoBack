import unittest
import httpx
import jwt
import os
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv
import subprocess
import time
import signal
import sys

# Load environment variables
load_dotenv()

class TestAuth(unittest.TestCase):
    """Test the authentication system with the updated JWT configuration."""
    
    @classmethod
    def setUpClass(cls):
        """Start the server before running tests."""
        print("Starting server for testing...")
        # Start the server as a subprocess
        cls.server_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "main:app", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        # Wait for server to start
        time.sleep(2)
        print("Server started.")
    
    @classmethod
    def tearDownClass(cls):
        """Shut down the server after tests."""
        print("Shutting down server...")
        # Send SIGTERM to the server process
        cls.server_process.terminate()
        # Wait for the process to terminate
        cls.server_process.wait()
        print("Server shut down.")
    
    def test_token_endpoint(self):
        """Test that the token endpoint returns a valid JWT token."""
        print("Testing token endpoint...")
        
        # Create a test user if it doesn't exist
        with httpx.Client() as client:
            try:
                # Check if test user exists
                response = client.get("http://localhost:8000/utilisateur/test_user")
                
                # If user doesn't exist, create it
                if response.status_code != 200:
                    user_data = {
                        "pseudo": "test_user",
                        "mot_de_passe": "Test123!",
                        "nom": "Test",
                        "prenom": "User",
                        "courriel": "test@example.com",
                        "est_admin": False,
                        "numCours": 0,
                        "tempsTotal": 0,
                        "cptDefi": 0
                    }
                    response = client.post("http://localhost:8000/utilisateurs/", json=user_data)
                    self.assertEqual(response.status_code, 200, f"Failed to create test user: {response.text}")
                
                # Test authentication
                auth_data = {
                    "username": "test_user",
                    "password": "Test123!"
                }
                
                response = client.post(
                    "http://localhost:8000/token",
                    data=auth_data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                # Check if we got a successful response
                self.assertEqual(response.status_code, 200, f"Authentication failed: {response.text}")
                
                # Check if we got a token
                json_response = response.json()
                self.assertIn("access_token", json_response, "Response doesn't contain access_token")
                self.assertIn("token_type", json_response, "Response doesn't contain token_type")
                self.assertEqual(json_response["token_type"], "bearer", "Token type is not bearer")
                
                # Verify the token
                token = json_response["access_token"]
                secret_key = os.getenv("JWT_SECRET_KEY")
                
                try:
                    decoded = jwt.decode(token, secret_key, algorithms=["HS256"])
                    self.assertEqual(decoded["sub"], "test_user", "Token subject is not test_user")
                except jwt.PyJWTError as e:
                    self.fail(f"Token verification failed: {str(e)}")
                    
                print("✅ Token endpoint test passed!")
                
            except Exception as e:
                self.fail(f"Test failed with error: {str(e)}")

if __name__ == "__main__":
    unittest.main() 