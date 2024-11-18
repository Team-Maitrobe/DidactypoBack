from fastapi import FastAPI, HTTPException, Depends
from typing import Annotated, List
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal, engine
import models
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configuration CORS configuration to allow access from specific origins
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

# Pydantic Models for validation and serialization
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
        orm_mode = True  # corrected to orm_mode for SQLAlchemy compatibility

class DefiBase(BaseModel):
    titre_defi: str
    description_defi: str

class DefiModele(DefiBase):
    id_defi: int

    class Config:
        orm_mode = True  # corrected to orm_mode for SQLAlchemy compatibility

class DefiUtilisateurBase(BaseModel):
    id_defi: int
    pseudo_utilisateur: str
    date_reussite: str

class DefiUtilisateurModele(DefiUtilisateurBase):
    class Config:
        orm_mode = True  # corrected to orm_mode for SQLAlchemy compatibility

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables if they don't exist
models.Base.metadata.create_all(bind=engine)

# Utilisateur Routes
@app.post('/utilisateurs/', response_model=UtilisateurModele)
async def creer_utilisateur(utilisateur: UtilisateursBase, db: Session = Depends(get_db)):
    try:
        db_utilisateur = models.Utilisateur(**utilisateur.dict())
        db.add(db_utilisateur)
        db.commit()
        db.refresh(db_utilisateur)
        return db_utilisateur
    except Exception as e:
        db.rollback()  # Rollback the transaction if an error occurs
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/utilisateurs/', response_model=List[UtilisateurModele])
async def lire_utilisateurs(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    utilisateurs = db.query(models.Utilisateur).offset(skip).limit(limit).all()
    return utilisateurs

@app.delete('/utilisateurs/{pseudo}', response_model=dict)
async def supprimer_utilisateur(pseudo: str, db: Session = Depends(get_db)):
    db_utilisateur = db.query(models.Utilisateur).filter(models.Utilisateur.pseudo == pseudo).first()
    if not db_utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    db.delete(db_utilisateur)
    db.commit()
    return {"message": f"Utilisateur '{pseudo}' supprimé avec succès."}

# Defi Routes
@app.post('/defis/', response_model=DefiModele)
async def ajouter_defi(defi: DefiBase, db: Session = Depends(get_db)):
    try:
        db_defi = models.Defi(**defi.dict())
        db.add(db_defi)
        db.commit()
        db.refresh(db_defi)
        return db_defi
    except Exception as e:
        db.rollback()  # Rollback the transaction if an error occurs
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'ajout du défi : {str(e)}")

@app.get('/defis/', response_model=List[DefiModele])
async def lire_defis(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    defis = db.query(models.Defi).offset(skip).limit(limit).all()
    return defis
