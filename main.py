# Imports standards Python
import logging
from datetime import datetime, timedelta, timezone

# Imports tiers
import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from fastapi import FastAPI, HTTPException, Depends, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel

# Imports internes
from database import SessionLocal, engine
from auth import Token, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM, pwd_context, oauth2_scheme
import models
from pydantic_models import (
    UtilisateurBase, UtilisateurModele,
    StatsUtilisateur,
    DefiBase, DefiModele,
    UtilisateurDefiBase, UtilisateurDefiModele,
    BadgeBase, BadgeModele,
    CoursBase, CoursModele,
    SousCoursBase, SousCoursModele,
    GroupeBase, GroupeModele,
    UtilisateurGroupeBase, UtilisateurGroupeModele,
)

# Typing
from typing import Annotated, List


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
        utilisateur.mot_de_passe = get_mdp_hashe(utilisateur.mot_de_passe)
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

#Utilisateur stats
@app.get('/stats/{pseudo}', response_model=StatsUtilisateur)
async def lire_stats_utilisateur(pseudo: str, db: Session = Depends(get_db)):
    utilisateur = get_utilisateur(db, pseudo)
    
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Prepare the data for the response
    return StatsUtilisateur(
        moyMotsParMinute=str(utilisateur.moyMotsParMinute or 0),
        numCours=str(utilisateur.numCours or 0),
        tempsTotal=str(utilisateur.tempsTotal or 0)
    )

# Define password hash verification
def verifier_mdp(plain_password, mot_de_passe):
    return pwd_context.verify(plain_password, mot_de_passe)


def get_mdp_hashe(mot_de_passe):
    return pwd_context.hash(mot_de_passe)


# Fetch user logic
def get_utilisateur(db, pseudo: str):
    utilisateur = db.query(models.Utilisateur).filter(models.Utilisateur.pseudo == pseudo).first()
    if utilisateur:
        return utilisateur
    return None


def authenticate_user(db, pseudo: str, mot_de_passe: str):
    utilisateur = get_utilisateur(db, pseudo)
    if not utilisateur:
        return False
    if not verifier_mdp(mot_de_passe, utilisateur.mot_de_passe):
        return False
    return utilisateur


# Token creation logic
def creer_token_acces(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# JWT decode & user authentication
async def get_utilisateur_courant(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        pseudo: str = payload.get("sub")
        if not pseudo:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        utilisateur = db.query(models.Utilisateur).filter(models.Utilisateur.pseudo == pseudo).first()
        if not utilisateur:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="L'utilisateur n'éxiste pas"
            )
        return utilisateur
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

#/default/lire_utilisateurs_utilisateurs__get
# Token endpoint
@app.post("/token")
async def login_pour_token_acces(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db=Depends(get_db)
) -> Token:
    utilisateur = authenticate_user(db, form_data.username, form_data.password)
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


@app.get("/utilisateurs/moi/badge/", response_model=List[BadgeModele])
async def lire_ses_badges(
    current_user: Annotated[models.Utilisateur, Depends(get_utilisateur_courant)],
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    # Query only badges belonging to the authenticated user
    badges = db.query(models.Badge).filter(models.Badge.user_id == current_user.id).offset(skip).limit(limit).all()
    # Serialize database models into Pydantic models
    return [BadgeModele.from_orm(badge) for badge in badges]

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

@app.get('/defis/{id_defi}', response_model=DefiModele)
async def lire_infos_defi(id_defi: int, db: Session = Depends(get_db)):
    defis = db.query(models.Defi).filter(models.Defi.id_defi == id_defi).first()
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
            if (temps_reussite < existing_reussite.temps_reussite):
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

#Cours
@app.post('/cours/', response_model=CoursModele)
async def ajouter_cour(cour: CoursBase, db: Session = Depends(get_db)):
    try:
        db_cour = models.Cours(**cour.dict())
        db.add(db_cour)
        db.commit()
        db.refresh(db_cour)
        return db_cour
    except Exception as e:
        db.rollback()  # Rollback the transaction if an error occurs
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'ajout du cours : {str(e)}")

@app.get('/cours/', response_model=List[CoursModele])
async def lire_cours(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    cours = db.query(models.Cours).offset(skip).limit(limit).all()
    return cours

@app.get('/cours/{id_cour}', response_model=CoursModele)
async def lire_infos_cour(id_cour: int, db: Session = Depends(get_db)):
    cours = db.query(models.Cours).filter(models.Cours.id_cours == id_cour).first()
    return cours

@app.delete('/cours/{id_cour}', response_model=dict)
async def supprimer_cour(id_cour: int, db: Session = Depends(get_db)):
    # Récupérer le cours en fonction de son id
    db_cour = db.query(models.Cours).filter(models.Cours.id_cours == id_cour).first()
    
    # Si le cours n'est pas trouvé, erreur 404
    if not db_cour:
        raise HTTPException(status_code=404, detail="Défi non trouvé")
    
    # Récupérer titre du cours pour le message de succès
    titre_cour = db_cour.titre_cours
    
    # Supprimer le cours
    db.delete(db_cour)
    db.commit()
    
    # Message de réussiyte
    return {"message": f"Défi '{titre_cour}' supprimé avec succès."}

#Sous cours
def get_next_sous_cours_id(db: Session, id_cours_parent: int) -> int:
    # Find the maximum existing `id_sous_cours` for this `id_cours_parent`
    max_id_query = db.query(func.max(models.SousCours.id_sous_cours)).filter(models.SousCours.id_cours_parent == id_cours_parent)
    max_id = max_id_query.scalar()

    # If there are no existing records for this parent, start at 1
    return max_id + 1 if max_id else 1

def get_sous_cours(db: Session, id_sous_cours: int) -> models.SousCours:
    return db.query(models.SousCours).filter(models.SousCours.id_sous_cours == id_sous_cours).first()

def get_sous_cours_by_parent(db: Session, id_cours_parent: int):
    return db.query(models.SousCours).filter(models.SousCours.id_cours_parent == id_cours_parent).all()

def delete_sous_cours(db: Session, id_sous_cours: int):
    sous_cours = db.query(models.SousCours).filter(models.SousCours.id_sous_cours == id_sous_cours).first()
    if sous_cours:
        db.delete(sous_cours)
        db.commit()
        return True
    return False

@app.post("/sous_cours/", response_model=SousCoursModele)
def add_sous_cours(sous_cours_data: SousCoursBase, db: Session = Depends(get_db)):
    # Check if the parent course exists
    parent_cours = db.query(models.Cours).filter(models.Cours.id_cours == sous_cours_data.id_cours_parent).first()
    if not parent_cours:
        raise HTTPException(status_code=404, detail="Parent course not found")
    
    # Generate the next SousCours ID specifically for this course
    next_id = get_next_sous_cours_id(db, sous_cours_data.id_cours_parent)

    # Create the new sous_cours
    new_sous_cours = models.SousCours(
        id_cours_parent=sous_cours_data.id_cours_parent,
        id_sous_cours=next_id,
        titre_sous_cours=sous_cours_data.titre_sous_cours,
        contenu_cours=sous_cours_data.contenu_cours,
        chemin_img_sous_cours=sous_cours_data.chemin_img_sous_cours
    )

    try:
        db.add(new_sous_cours)
        db.commit()
        db.refresh(new_sous_cours)
    except Exception as e:
        db.rollback()  # Ensure the transaction is rolled back on error
        raise HTTPException(status_code=500, detail=f"Error while adding sub-course: {str(e)}")

    return new_sous_cours

@app.get("/sous_cours/{id_cours_parent}", response_model=List[SousCoursModele])
def get_sous_cours_by_parent(id_cours_parent: int, db: Session = Depends(get_db)):
    sous_cours_list = db.query(models.SousCours).filter(models.SousCours.id_cours_parent == id_cours_parent).all()
    
    if not sous_cours_list:
        raise HTTPException(status_code=404, detail="No sub-courses found for this parent course")
    
    return sous_cours_list

@app.delete("/sous_cours/{id_sous_cours}", response_model=dict)
def delete_sous_cours(id_sous_cours: int, db: Session = Depends(get_db)):
    # Check if the sous_cours exists
    sous_cours = db.query(models.SousCours).filter(models.SousCours.id_sous_cours == id_sous_cours).first()
    
    if not sous_cours:
        raise HTTPException(status_code=404, detail="Sous-cours not found")
    
    db.delete(sous_cours)
    db.commit()

    return {"message": f"Sous-cours with ID {id_sous_cours} deleted successfully."}

# Groupes

@app.post('/groupe/', response_model=GroupeModele)
async def ajouter_groupe(groupe: GroupeBase, db: Session = Depends(get_db)):
    try:
        db_groupe = models.Groupe(**groupe.dict())
        db.add(db_groupe)
        db.commit()
        db.refresh(db_groupe)
        return db_groupe
    except Exception as e:
        db.rollback()  # Rollback the transaction if an error occurs
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'ajout du groupe : {str(e)}")

@app.get('/groupe/', response_model=List[GroupeModele])
async def lire_groupe(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    groupe = db.query(models.Groupe).offset(skip).limit(limit).all()
    return groupe

@app.get('/groupe/{id_groupe}', response_model=GroupeModele)
async def lire_infos_groupe(id_groupe: int, db: Session = Depends(get_db)):
    groupe = db.query(models.Groupe).filter(models.Groupe.id_groupe == id_groupe).first()
    return groupe

@app.delete('/groupe/{id_groupe}', response_model=dict)
async def supprimer_groupe(id_groupe: int, db: Session = Depends(get_db)):
    # Récupérer le groupe en fonction de son id
    db_groupe = db.query(models.Groupe).filter(models.Groupe.id_groupe == id_groupe).first()
    
    # Si le groupe n'est pas trouvé, erreur 404
    if not db_groupe:
        raise HTTPException(status_code=404, detail="groupe non trouvé")
    
    # Récupérer nom du groupe pour le message de succès
    nom_groupe = db_groupe.nom_groupe
    
    # Supprimer le groupe
    db.delete(db_groupe)
    db.commit()
    
    # Message de réussite
    return {"message": f"groupe '{nom_groupe}' supprimé avec succès."}



#Groupe d'utilisateurs

@app.post('/groupe_utilisateurs/', response_model=UtilisateurGroupeModele)
async def ajout_groupe_utilisateurs(
    id_groupe : int,  # ID du groupe (passé en paramètre de la requête)
    pseudo_utilisateur: str,  # Pseudo de l'utilisateur (passé en paramètre de la requête)
    est_admin : bool,  # booleen pour definir l'admin du groupe
    db: Session = Depends(get_db)  # Dépendance pour obtenir la session de base de données
):
    try:
        # Vérifier si l'utilisateur existe dans la base de données
        db_utilisateur = db.query(models.Utilisateur).filter(models.Utilisateur.pseudo == pseudo_utilisateur).first()
        if not db_utilisateur:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        # Vérifier si le défi existe dans la base de données
        db_groupe = db.query(models.Groupe).filter(models.Groupe.id_groupe == id_groupe).first()
        if not db_groupe:
            raise HTTPException(status_code=404, detail="Groupe non trouvé")
        
        # Vérifier si l'utilisateur appartient deja à ce groupe
        existing_reussite = db.query(models.UtilisateurGroupe).filter(
            models.UtilisateurGroupe.pseudo_utilisateur == pseudo_utilisateur,
            models.UtilisateurGroupe.id_groupe == id_groupe
        ).first()

        if existing_reussite:
            # Si l'utilisateur appartient à ce groupe
            return existing_reussite  # Voir quelle action effectuer ici
        else:
            # Si l'utilisateur n'appartient pas a ce groupe, l'ajouter au groupe
            db_utilisateur_groupe = models.UtilisateurGroupe(
                pseudo_utilisateur=pseudo_utilisateur,
                id_groupe=id_groupe,
                est_admin=est_admin,
            )
            db.add(db_utilisateur_groupe)  # Ajouter la nouvelle réussite dans la base de données
            db.commit()  # Commit les changements
            db.refresh(db_utilisateur_groupe)  # Rafraîchir l'instance pour obtenir les données mises à jour
            return db_utilisateur_groupe  # Retourner la nouvelle réussite ajoutée
    
    except Exception as e:
        # Si une erreur se produit, annuler la transaction et retourner un message d'erreur
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'ajout de la réussite du défi : {str(e)}")


@app.get('/groupe_utilisateurs', response_model=List[UtilisateurGroupeModele])
async def lire_tous_les_groupes_utilisateurs(
    db: Session = Depends(get_db),  # Dépendance pour obtenir la session de base de données
    skip: int = 0,  # Paramètre optionnel pour le décalage (pagination)
    limit: int = 100  # Paramètre optionnel pour la limite du nombre de résultats
):
    try:
        # Récupérer toutes les relations entre groupes et utilisateurs
        tous_les_groupes_utilisateurs = db.query(models.UtilisateurGroupe).offset(skip).limit(limit).all()

        # Si aucune relation n'est trouvée
        if not tous_les_groupes_utilisateurs:
            raise HTTPException(status_code=404, detail="Aucune relation groupe-utilisateur trouvée.")
        
        return tous_les_groupes_utilisateurs  # Retourner la liste complète des relations
    
    except Exception as e:
        # Gestion des erreurs
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des relations groupe-utilisateur : {str(e)}")



@app.get('/groupe_utilisateurs/{pseudo_utilisateur}', response_model=List[UtilisateurGroupeModele])
async def lire_groupes_d_utilisateur(
    pseudo_utilisateur: str,  # Pseudo de l'utilisateur dont on veut les groupes
    db: Session = Depends(get_db),  # Dépendance pour obtenir la session de base de données
    skip: int = 0,  # Paramètre optionnel pour le décalage (pagination)
    limit: int = 100  # Paramètre optionnel pour la limite du nombre de résultats
):
    try:
        # Récupérer les groupes auxquels appartient l'utilisateur
        groupes_utilisateur = db.query(models.UtilisateurGroupe).filter(
            models.UtilisateurGroupe.pseudo_utilisateur == pseudo_utilisateur
        ).offset(skip).limit(limit).all()

        # Si aucun groupe n'est trouvé pour cet utilisateur
        if not groupes_utilisateur:
            raise HTTPException(status_code=404, detail="Aucun groupe trouvé pour cet utilisateur.")
        
        return groupes_utilisateur  # Retourner la liste des groupes de l'utilisateur
    
    except Exception as e:
        # Gestion des erreurs
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des groupes de l'utilisateur : {str(e)}")


@app.delete('/groupes_utilisateurs', response_model=dict)
async def supprimer_relation_utilisateur_groupe(
    id_groupe: int,  # ID du groupe à supprimer
    pseudo_utilisateur: str,  # Pseudo de l'utilisateur dont on veut supprimer la relation
    db: Session = Depends(get_db)  # Dépendance pour obtenir la session de base de données
):
    try:
        # Chercher la relation entre l'utilisateur et le groupe
        relation = db.query(models.UtilisateurGroupe).filter(
            models.UtilisateurGroupe.id_groupe == id_groupe,
            models.UtilisateurGroupe.pseudo_utilisateur == pseudo_utilisateur
        ).first()
        
        # Vérifier si la relation existe
        if not relation:
            raise HTTPException(status_code=404, detail="Relation utilisateur-groupe non trouvée.")
        
        # Supprimer la relation
        db.delete(relation)
        db.commit()
        
        # Retourner une réponse avec statut 200 OK
        return {"detail": "Relation supprimée avec succès."}
    
    except Exception as e:
        # Gestion des erreurs
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression de la relation : {str(e)}")
