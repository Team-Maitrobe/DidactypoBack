from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel

# éxecuter "openssl rand -hex 32" pour obtenir une nouvelle clef
SECRET_KEY = "73980ab468f0a5be1b530fbe5c7e43654aee29faf486bcd63040de51105b951a"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


db = {
    "johndoe": {
        "pseudo": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "mot_de_passe": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    pseudo: str | None = None


class UtilisateurBase(BaseModel):
    pseudo: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UtilisateurModele(UtilisateurBase):
    mot_de_passe: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()


def verifier_mdp(plain_password, mot_de_passe):
    return pwd_context.verify(plain_password, mot_de_passe)


def get_mdp_hashe(mot_de_passe):
    return pwd_context.hash(mot_de_passe)


def get_utilisateur(db, pseudo: str):
    if pseudo in db:
        user_dict = db[pseudo]
        return UtilisateurModele(**user_dict)


def authenticate_user(db, pseudo: str, mot_de_passe: str):
    utilisateur = get_utilisateur(db, pseudo)
    if not utilisateur:
        return False
    if not verifier_mdp(mot_de_passe, utilisateur.mot_de_passe):
        return False
    return utilisateur


def creer_token_acces(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_utilisateur_courant(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        pseudo: str = payload.get("sub")
        if pseudo is None:
            raise credentials_exception
        token_data = TokenData(pseudo=pseudo)
    except InvalidTokenError:
        raise credentials_exception
    utilisateur = get_utilisateur(db, pseudo=token_data.pseudo)
    if utilisateur is None:
        raise credentials_exception
    return utilisateur


async def get_utilisateur_courant_actif(
    current_user: Annotated[UtilisateurBase, Depends(get_utilisateur_courant)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive utilisateur")
    return current_user


@app.post("/token")
async def login_pour_token_acces(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    utilisateur = authenticate_user(db, form_data.pseudo, form_data.mot_de_passe)
    if not utilisateur:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Mot de passe ou pseudo incorrecte",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = creer_token_acces(
        data={"sub": utilisateur.pseudo}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/utilisateurs/moi/", response_model=UtilisateurBase)
async def lire_utilisateurs_moi(
    current_user: Annotated[UtilisateurBase, Depends(get_utilisateur_courant_actif)],
):
    return current_user


@app.get("/utilisateurs/moi/items/")
async def lire_ses_items(
    current_user: Annotated[UtilisateurBase, Depends(get_utilisateur_courant_actif)],
):
    return [{"item_id": "Foo", "owner": current_user.pseudo}]