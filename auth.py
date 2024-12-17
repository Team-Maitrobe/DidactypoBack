from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel

from pydantic_models import UtilisateurBase, UtilisateurModele
import models
# éxecuter "openssl rand -hex 32" pour obtenir une nouvelle clef
SECRET_KEY = "73980ab468f0a5be1b530fbe5c7e43654aee29faf486bcd63040de51105b951a"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    pseudo: Optional[str] = None

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")