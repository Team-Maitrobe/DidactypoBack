from typing import Optional
import os
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

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")