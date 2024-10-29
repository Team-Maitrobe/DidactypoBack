from fastapi import FastAPI, HTTPException, Depends
from typing import Annotated, List
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal, engine
import models

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    'http://localhost:5173',
    'http://localhost:3000',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UtilisateursBase(BaseModel):
    pseudo: str
    mot_de_passe: str
    nom: str
    prenom: str
    courriel: str
    est_admin: bool
    moyMotsParMinute: int
    numCours: int
    tempsTotal: int

class UtilisateurModele(UtilisateursBase):
    class Config:
        from_attributes = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependencies = Annotated[Session, Depends(get_db)]

models.Base.metadata.create_all(bind=engine)

@app.post('/utilisateurs/', response_model=UtilisateurModele)
async def creer_utilisateur(utilisateur: UtilisateursBase, db: Session = Depends(get_db)):
    db_utilisateur = models.Utilisateur(**utilisateur.dict())
    db.add(db_utilisateur)
    db.commit()
    db.refresh(db_utilisateur)
    
    return db_utilisateur

@app.get('/utilisateurs/', response_model=List[UtilisateurModele])
async def lire_utilisateurs(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    utilisateurs = db.query(models.Utilisateur).offset(skip).limit(limit).all()
    return utilisateurs
