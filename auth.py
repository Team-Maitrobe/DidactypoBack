from typing import Optional

from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic import BaseModel

# éxecuter "openssl rand -hex 32" pour obtenir une nouvelle clef
SECRET_KEY = ""
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 600

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    pseudo: Optional[str] = None

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")