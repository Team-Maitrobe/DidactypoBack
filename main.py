from fastapi import FastAPI, HTTPException, Depends, Query
from typing import Annotated, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware

import models
from pydantic_models import UtilisateurBase, UtilisateurModele, DefiBase, DefiModele, UtilisateurDefiBase, UtilisateurDefiModele

from datetime import datetime
import logging

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

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
async def creer_utilisateur(utilisateur: UtilisateurBase, db: Session = Depends(get_db)):
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

@app.delete('/defis/{id_defi}', response_model=dict)
async def supprimer_defi(id_defi: int, db: Session = Depends(get_db)):
    # Récupérer le défi en fonction de son id
    db_defi = db.query(models.Defi).filter(models.Defi.id_defi == id_defi).first()
    
    # Si le défi n'est pass trouvé, erreur 404
    if not db_defi:
        raise HTTPException(status_code=404, detail="Défi non trouvé")
    
    # Récupérer titre du défi pour le message de succès
    titre_defi = db_defi.titre_defi
    
    # Supprimer le défi
    db.delete(db_defi)
    db.commit()
    
    # Message de réussiyte
    return {"message": f"Défi '{titre_defi}' supprimé avec succès."}

#Réussite défi

@app.post('/reussites_defi/', response_model=UtilisateurDefiModele)
async def ajout_reussite_defi(
    id_defi: int,  # ID du défi (passé en paramètre de la requête)
    pseudo_utilisateur: str,  # Pseudo de l'utilisateur (passé en paramètre de la requête)
    temps_reussite: float,  # Temps de réussite du défi
    db: Session = Depends(get_db)  # Dépendance pour obtenir la session de base de données
):
    try:
        # Vérifier si l'utilisateur existe dans la base de données
        db_utilisateur = db.query(models.Utilisateur).filter(models.Utilisateur.pseudo == pseudo_utilisateur).first()
        if not db_utilisateur:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        # Vérifier si le défi existe dans la base de données
        db_defi = db.query(models.Defi).filter(models.Defi.id_defi == id_defi).first()
        if not db_defi:
            raise HTTPException(status_code=404, detail="Défi non trouvé")
        
        # Vérifier si l'utilisateur a déjà réussi ce défi
        existing_reussite = db.query(models.UtilisateurDefi).filter(
            models.UtilisateurDefi.pseudo_utilisateur == pseudo_utilisateur,
            models.UtilisateurDefi.id_defi == id_defi
        ).first()

        if existing_reussite:
            # Si l'utilisateur a déjà réussi ce défi, mettre à jour le temps de réussite
            existing_reussite.temps_reussite = temps_reussite
            existing_reussite.date_reussite = datetime.now()  # Mettre à jour la date de réussite
            db.commit()  # Commit les changements dans la base de données
            db.refresh(existing_reussite)  # Rafraîchir l'instance pour obtenir les nouvelles données
            return existing_reussite  # Retourner la réussite mise à jour
        else:
            # Si l'utilisateur n'a pas encore réussi ce défi, on crée un nouveau record
            db_utilisateur_defi = models.UtilisateurDefi(
                pseudo_utilisateur=pseudo_utilisateur,
                id_defi=id_defi,
                temps_reussite=temps_reussite,
                date_reussite=datetime.now()  # Définir la date de réussite à l'heure actuelle
            )
            db.add(db_utilisateur_defi)  # Ajouter la nouvelle réussite dans la base de données
            db.commit()  # Commit les changements
            db.refresh(db_utilisateur_defi)  # Rafraîchir l'instance pour obtenir les données mises à jour
            return db_utilisateur_defi  # Retourner la nouvelle réussite ajoutée
    
    except Exception as e:
        # Si une erreur se produit, annuler la transaction et retourner un message d'erreur
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'ajout de la réussite du défi : {str(e)}")

#Récupérer toutes les réussites de défi
@app.get('/reussites_defi', response_model=List[UtilisateurDefiModele])
async def lire_reussite_defi(
    db: Session = Depends(get_db),  # Dépendance pour obtenir la session de base de données
    skip: int = 0,  # Paramètre optionnel pour le décalage (pagination)
    limit: int = 100  # Paramètre optionnel pour la limite du nombre de résultats
):
    try:
        # Récupérer toutes les réussites de défi pour tous les utilisateurs
        reussites_defi = db.query(models.UtilisateurDefi).offset(skip).limit(limit).all()

        # Si aucune réussite de défi n'est trouvée
        if not reussites_defi:
            raise HTTPException(status_code=404, detail="Aucune réussite de défi trouvée.")
        
        return reussites_defi  # Retourner la liste complète des réussites de défi
    
    except Exception as e:
        # Gestion des erreurs (rollback en cas d'exception)
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des réussites de défi : {str(e)}")

#Récuperer les réussites de défi d'un utilisateur
@app.get('/reussites_defi/{pseudo_utilisateur}', response_model=List[UtilisateurDefiModele])
async def lire_reussite_defi_utilisateur(
    pseudo_utilisateur: str,  # Pseudo de l'utilisateur passé en paramètre de l'URL
    db: Session = Depends(get_db),  # Dépendance pour obtenir la session de base de données
    skip: int = 0,  # Paramètre optionnel pour le décalage (pagination)
    limit: int = 100  # Paramètre optionnel pour la limite du nombre de résultats
):
    try:
        # Récupérer toutes les réussites de défi de l'utilisateur
        reussites_defi = db.query(models.UtilisateurDefi).filter(
            models.UtilisateurDefi.pseudo_utilisateur == pseudo_utilisateur
        ).offset(skip).limit(limit).all()

        # Si aucune réussite n'est trouvée pour cet utilisateur
        if not reussites_defi:
            raise HTTPException(status_code=404, detail="Aucune réussite de défi trouvée pour cet utilisateur.")
        
        return reussites_defi  # Retourner la liste des réussites de défi
    
    except Exception as e:
        # Gestion des erreurs (rollback en cas d'exception)
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des réussites de défi : {str(e)}")

#Supprimer une réussite de défi
@app.delete('/reussites_defi/', response_model=dict)
async def supprimer_reussite_defi(
    pseudo_utilisateur: str,  # Pseudo de l'utilisateur dont la réussite sera supprimée
    id_defi: int,  # ID du défi de la réussite à supprimer
    db: Session = Depends(get_db)  # Dépendance pour obtenir la session de base de données
):
    try:
        # Récupérer la réussite de défi spécifique en fonction du pseudo de l'utilisateur et de l'ID du défi
        reussite_defi = db.query(models.UtilisateurDefi).filter(
            models.UtilisateurDefi.pseudo_utilisateur == pseudo_utilisateur,
            models.UtilisateurDefi.id_defi == id_defi
        ).first()

        # Si la réussite n'est pas trouvée, renvoyer une erreur 404
        if not reussite_defi:
            raise HTTPException(status_code=404, detail="Réussite de défi non trouvée.")
        
        # Supprimer l'élément trouvé
        db.delete(reussite_defi)
        db.commit()
        
        # Retourner un message de succès
        return {"message": f"La réussite du défi avec l'ID {id_defi} pour l'utilisateur '{pseudo_utilisateur}' a été supprimée avec succès."}
    
    except Exception as e:
        # Gestion des erreurs (rollback en cas d'exception)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression de la réussite du défi : {str(e)}")
