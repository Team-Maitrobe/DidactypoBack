from typing import Optional, Tuple
import os
import re
from dotenv import load_dotenv

from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Get configuration from environment variables with fallbacks for backwards compatibility
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY environment variable is not set. Please set it in your .env file.")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "600"))

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    pseudo: Optional[str] = None

# Password security config - stronger bcrypt with higher rounds (default is 12)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=14)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Password validation requirements
PASSWORD_MIN_LENGTH = 3
PASSWORD_REQUIRE_UPPERCASE = False
PASSWORD_REQUIRE_LOWERCASE = False
PASSWORD_REQUIRE_DIGITS = False
PASSWORD_REQUIRE_SPECIAL = False
PASSWORD_MAX_LENGTH = 64  # Prevent DoS with huge passwords

# Password validation functions
def validate_password(password: str) -> Tuple[bool, str]:
    """
    Validate a password meets security requirements.
    
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    # Check for minimum length
    if len(password) < PASSWORD_MIN_LENGTH:
        return False, f"Le mot de passe doit contenir au moins {PASSWORD_MIN_LENGTH} caractères."
    
    # Check for maximum length
    if len(password) > PASSWORD_MAX_LENGTH:
        return False, f"Le mot de passe ne doit pas dépasser {PASSWORD_MAX_LENGTH} caractères."
    
    # Check for at least one uppercase letter
    if PASSWORD_REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
        return False, "Le mot de passe doit contenir au moins une lettre majuscule."
    
    # Check for at least one lowercase letter
    if PASSWORD_REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
        return False, "Le mot de passe doit contenir au moins une lettre minuscule."
    
    # Check for at least one digit
    if PASSWORD_REQUIRE_DIGITS and not re.search(r'\d', password):
        return False, "Le mot de passe doit contenir au moins un chiffre."
    
    # Check for at least one special character
    if PASSWORD_REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Le mot de passe doit contenir au moins un caractère spécial (!@#$%^&*(),.?\":{}|<>)."
    
    return True, ""

# Common/leaked password checker
COMMON_PASSWORDS = {
    "123456", "password", "123456789", "12345678", "12345", "1234567", "qwerty", 
    "abc123", "password1", "admin", "welcome", "monkey", "1234567890", "letmein", 
    "trustno1", "dragon", "baseball", "111111", "iloveyou", "master", "sunshine",
    "ashley", "bailey", "superman", "football", "password123", "azerty", "soleil"
}

def is_common_password(password: str) -> bool:
    """Check if password is in list of common/leaked passwords."""
    return password.lower() in COMMON_PASSWORDS