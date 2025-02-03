from typing import Optional

from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic import BaseModel

# éxecuter "openssl rand -hex 32" pour obtenir une nouvelle clef
SECRET_KEY = "73980ab468f0a5be1b530fbe5c7e43654aee29faf486bcd63040de51105b951a"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 600

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    pseudo: Optional[str] = None

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")