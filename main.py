from fastapi import FastAPI, HTTPException, Depends
from typing import Annotated, List
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal, engine
import models
from fastapi.middleware.cors import CORSMiddleware
import bcrypt

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
    try: 
        db_utilisateur = models.Utilisateur(**utilisateur.dict())
        db.add(db_utilisateur)
        db.commit()
        db.refresh(db_utilisateur)
        
        return db_utilisateur
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/utilisateurs/', response_model=List[UtilisateurModele])
async def lire_utilisateurs(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    utilisateurs = db.query(models.Utilisateur).offset(skip).limit(limit).all()
    return [UtilisateurModele.from_orm(u) for u in utilisateurs]

@app.delete('/utilisateurs/{pseudo}', response_model=dict)
async def supprimer_utilisateur(pseudo: str, db: Session = Depends(get_db)):
    db_utilisateur = db.query(models.Utilisateur).filter(models.Utilisateur.pseudo == pseudo).first()
    if not db_utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Convert the SQLAlchemy model to a Pydantic model for the response
    utilisateur_modele = UtilisateurModele.from_orm(db_utilisateur)
    
    db.delete(db_utilisateur)
    db.commit()
    
    return {
        "message": f"Utilisateur '{pseudo}' supprimé avec succès.",
        "utilisateur": utilisateur_modele
    }
