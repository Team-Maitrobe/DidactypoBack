# Imports standards Python
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Annotated, List

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
from database import SessionLocal, engine, execute_sql_file, is_initialized
from auth import Token, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM, pwd_context, oauth2_scheme
import models
from pydantic_models import (
    UtilisateurBase,  UtilisateurModele,
    StatsUtilisateur, UtilisateurRenvoye,
    DefiBase, DefiModele,
    UtilisateurDefiBase, UtilisateurDefiModele,
    BadgeBase, BadgeModele,
    CoursBase, CoursModele,
    UtilisateurCoursModele,
    SousCoursBase, SousCoursModele,
    GroupeBase, GroupeModele,
    UtilisateurGroupeBase, UtilisateurGroupeModele,
    UtilisateurBadgeModele,
)

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

@app.on_event("startup")
async def on_startup():
    sql_file_path = Path(__file__).parent / "cours.sql"

    db = SessionLocal()
    try:
        if not is_initialized(db, models.Cours):
            # Run the SQL file only if the database is uninitialized
            execute_sql_file(sql_file_path)
            print("La base de donnée a été initialisée avec les données existantes")
        else:
            print("La base de donnée est déjà initialisée")
    finally:
        db.close()

# Fetch user logic
def get_utilisateur(db, pseudo: str):
    utilisateur = db.query(models.Utilisateur).filter(models.Utilisateur.pseudo == pseudo).first()
    if utilisateur:
        return utilisateur
    return None

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

@app.get('/utilisateurs/', response_model=List[UtilisateurRenvoye])
async def lire_utilisateurs(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    try:
        utilisateurs = db.query(models.Utilisateur).offset(skip).limit(limit).all()
        if not utilisateurs:
            raise HTTPException(status_code=404, detail="No users found")
        valUtilisateurs = [UtilisateurRenvoye(pseudo=user.pseudo, nom=user.nom, prenom=user.prenom) for user in utilisateurs]
        return valUtilisateurs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching users: {str(e)}")

@app.delete('/utilisateurs/{pseudo}', response_model=dict)
async def supprimer_utilisateur(pseudo: str, db: Session = Depends(get_db)):
    db_utilisateur = get_utilisateur(db, pseudo)
    if not db_utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    db.delete(db_utilisateur)
    db.commit()
    return {"message": f"Utilisateur '{pseudo}' supprimé avec succès."}

#Utilisateur stats
# @app.patch('/stats/temps', response_model=UtilisateurBase)
# async def ajouter_stats_temps_defi(pseudo: str = Query(...), temps: float = Query(...), db: Session = Depends(get_db)):
#     utilisateur = get_utilisateur(db, pseudo)

#     if not utilisateur:
#         raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
#     utilisateur.tempsTotal += temps
#     db.commit()  # Commit the changes to the database
#     return utilisateur  # Return the updated user object
        
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

@app.get('/utilisateur/moi')
async def lire_utilisateur_courant(
    current_user: Annotated[models.Utilisateur, Depends(get_utilisateur_courant)]
):
    return current_user

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
        db_utilisateur = get_utilisateur(db, pseudo_utilisateur)

        # Vérifier si le défi existe dans la base de données
        db_defi = db.query(models.Defi).filter(models.Defi.id_defi == id_defi).first()
        if not db_defi:
            raise HTTPException(status_code=404, detail="Défi non trouvé")
    
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
        # Subquery to get the minimum time for each user and challenge
        subquery = db.query(
            models.UtilisateurDefi.pseudo_utilisateur,
            models.UtilisateurDefi.id_defi,
            func.min(models.UtilisateurDefi.temps_reussite).label('min_temps_reussite')
        ).group_by(
            models.UtilisateurDefi.pseudo_utilisateur,
            models.UtilisateurDefi.id_defi
        ).subquery()

        # Join the subquery with the main table to get the full records
        reussites_defi = db.query(models.UtilisateurDefi).join(
            subquery,
            (models.UtilisateurDefi.pseudo_utilisateur == subquery.c.pseudo_utilisateur) &
            (models.UtilisateurDefi.id_defi == subquery.c.id_defi) &
            (models.UtilisateurDefi.temps_reussite == subquery.c.min_temps_reussite)
        ).offset(skip).limit(limit).all()

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

@app.post("/sous_cours/", response_model=SousCoursModele)
async def add_sous_cours(sous_cours_data: SousCoursBase, db: Session = Depends(get_db)):
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
        db.rollback()  # Rollback en cas d'erreur
        raise HTTPException(status_code=500, detail=f"Error while adding sub-course: {str(e)}")

    return new_sous_cours

@app.get("/sous_cours/{id_cours_parent}", response_model=List[SousCoursModele])
async def get_sous_cours_by_parent(id_cours_parent: int, db: Session = Depends(get_db)):
    sous_cours_list = db.query(models.SousCours).filter(models.SousCours.id_cours_parent == id_cours_parent).all()
    
    if not sous_cours_list:
        raise HTTPException(status_code=404, detail="Aucun sous-cours trouvé pour ce parent")
    
    return sous_cours_list

@app.get("/sous_cours", response_model=SousCoursModele)
def get_sous_cours(id_sous_cours: int, id_cours_parent: int, db: Session = Depends(get_db)) -> models.SousCours:
    sous_cours = db.query(models.SousCours).filter(
        models.SousCours.id_sous_cours == id_sous_cours,
        models.SousCours.id_cours_parent == id_cours_parent
    ).first()

    if not sous_cours:
        raise HTTPException(status_code=404, detail="Sous-cours non trouvé")
    
    return sous_cours

@app.delete("/sous_cours/{id_sous_cours}", response_model=dict)
def delete_sous_cours(id_sous_cours: int, id_cours_parent: int, db: Session = Depends(get_db)):
    sous_cours = db.query(models.SousCours).filter(
        models.SousCours.id_sous_cours == id_sous_cours,
        models.SousCours.id_cours_parent == id_cours_parent
    ).first()

    if not sous_cours:
        raise HTTPException(status_code=404, detail="Sous-cours non trouvé")
    
    # Delete the sous_cours if found
    db.delete(sous_cours)
    db.commit()

    return {"message": f"Sous-cours avec ID {id_sous_cours} et ID parent {id_cours_parent} supprimé."}

# Complétion cours
@app.post('/completion_cours', response_model=UtilisateurCoursModele)
async def ajouter_completion_cours(
    current_user: Annotated[models.Utilisateur, Depends(get_utilisateur_courant)],
    id_cours: int,
    db: Session = Depends(get_db)):
    
    new_completion = models.UtilisateurCours(
        id_cours=id_cours,
        pseudo_utilisateur=current_user.id,
        progression=1 
    )

    try:
        db.add(new_completion)
        db.commit()
        db.refresh(new_completion)
    except Exception as e:
        # Rollback en cas d'erreur
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur pendant l'ajout de la completion: {str(e)}")

    return new_completion 

# Groupes
@app.post('/groupe/', response_model=GroupeBase)
async def ajouter_groupe(
    groupe: GroupeBase,
    pseudo_admin: str,
    db: Session = Depends(get_db)):
    try:
        # Case 1: Ensure the group data is valid
        if not groupe:
            raise HTTPException(status_code=400, detail="Données de groupe invalides")
    

        # Create new group
        db_groupe = models.Groupe(**groupe.dict())
        db.add(db_groupe)
        db.commit()
        db.refresh(db_groupe)
        
        # Case 3: Check if the group ID was correctly generated
        if not db_groupe.id_groupe:
            raise HTTPException(status_code=500, detail="Erreur de création du groupe: ID non généré")
        
        # Case 4: Check if the admin user exists in the database
        existing_user = db.query(models.Utilisateur).filter(models.Utilisateur.pseudo == pseudo_admin).first()
        if not existing_user:
            raise HTTPException(status_code=404, detail=f"Utilisateur avec le pseudo '{pseudo_admin}' non trouvé")

        # Case 5: Check if the user is already part of another group as an admin
        existing_user_group = db.query(models.UtilisateurGroupe).filter(
            models.UtilisateurGroupe.pseudo_utilisateur == pseudo_admin,
            models.UtilisateurGroupe.est_admin == True
        ).first()
        if existing_user_group:
            raise HTTPException(status_code=400, detail=f"L'utilisateur '{pseudo_admin}' est déjà administrateur dans un autre groupe.")

        # Add the user to the group
        db_utilisateur_groupe = models.UtilisateurGroupe(
            pseudo_utilisateur=pseudo_admin,
            id_groupe=db_groupe.id_groupe,
            est_admin=True,
        )
        
        db.add(db_utilisateur_groupe)
        db.commit()
        db.refresh(db_utilisateur_groupe)

        return db_groupe

    except Exception as e:
        db.rollback()  # Rollback in case of any error
        # Case 8: General error handling
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

@app.post('/membre_classe/', response_model=UtilisateurGroupeModele)
async def ajout_membre_classe(
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


@app.get('/membre_classe_par_groupe/{id_groupe}', response_model=List[UtilisateurModele])
async def lire_tous_les_membres_classe(
    id_groupe: int,
    db: Session = Depends(get_db),  # Dépendance pour obtenir la session de base de données
    skip: int = 0,  # Paramètre optionnel pour le décalage (pagination)
    limit: int = 100  # Paramètre optionnel pour la limite du nombre de résultats
):
    try:
        # Récupérer les relations entre groupes et utilisateurs pour un groupe spécifique
        membres_classe = db.query(models.UtilisateurGroupe).filter(models.UtilisateurGroupe.id_groupe == id_groupe).offset(skip).limit(limit).all()

        if not membres_classe:
            raise HTTPException(status_code=404, detail="Aucune relation groupe-utilisateur trouvée.")

        # Extraire les pseudos des membres
        pseudos_membres = [membre.pseudo_utilisateur for membre in membres_classe]

        # Récupérer les informations des utilisateurs (modèle Utilisateur) en fonction des pseudos
        utilisateurs = db.query(models.Utilisateur).filter(models.Utilisateur.pseudo.in_(pseudos_membres)).all()

        if not utilisateurs:
            raise HTTPException(status_code=404, detail="Aucun utilisateur trouvé pour ce groupe.")

        return utilisateurs
    
    except Exception as e:
        # Gestion des erreurs
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des relations groupe-utilisateur : {str(e)}")

@app.get('/admins_groupe/{id_groupe}', response_model=List[UtilisateurModele])
async def lire_tous_les_admins_classe(
    id_groupe: int,
    db: Session = Depends(get_db),  # Dépendance pour obtenir la session de base de données
    skip: int = 0,  # Paramètre optionnel pour le décalage (pagination)
    limit: int = 100  # Paramètre optionnel pour la limite du nombre de résultats
):
    try:
        # Récupérer les relations entre groupes et utilisateurs pour un groupe spécifique
        membres_classe = db.query(models.UtilisateurGroupe).filter(models.UtilisateurGroupe.id_groupe == id_groupe and models.UtilisateurGroupe.est_admin == True).offset(skip).limit(limit).all()

        if not membres_classe:
            raise HTTPException(status_code=404, detail="Aucun admin trouvé.")

        # Extraire les pseudos des membres
        pseudos_membres = [membre.pseudo_utilisateur for membre in membres_classe]

        # Récupérer les informations des utilisateurs (modèle Utilisateur) en fonction des pseudos
        utilisateurs = db.query(models.Utilisateur).filter(models.Utilisateur.pseudo.in_(pseudos_membres)).all()

        if not utilisateurs:
            raise HTTPException(status_code=404, detail="Aucun utilisateur trouvé pour ce groupe.")

        return utilisateurs
    
    except Exception as e:
        # Gestion des erreurs
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des relations groupe-utilisateur : {str(e)}")

@app.get('/membre_classe/{pseudo_utilisateur}', response_model=UtilisateurGroupeModele)
async def lire_groupes_d_utilisateur(
    pseudo_utilisateur: str,  # Pseudo de l'utilisateur dont on veut les groupes
    db: Session = Depends(get_db),  # Dépendance pour obtenir la session de base de données
):
    try:
        # Récupérer le groupe auxquel appartient l'utilisateur
        groupe_utilisateur = db.query(models.UtilisateurGroupe).filter(
            models.UtilisateurGroupe.pseudo_utilisateur == pseudo_utilisateur
        ).first()

        # Si aucun groupe n'est trouvé pour cet utilisateur
        if not groupe_utilisateur:
            raise HTTPException(status_code=404, detail="Aucun groupe trouvé pour cet utilisateur.")
        
        return groupe_utilisateur  # Retourner la liste des groupes de l'utilisateur
    
    except Exception as e:
        # Gestion des erreurs
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des groupes de l'utilisateur : {str(e)}")


@app.delete('/membres_classe', response_model=dict)
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
    
# Badges
@app.post("/badges/", response_model=BadgeModele)
async def add_badge(badge_data: BadgeBase, db: Session = Depends(get_db)):
    # Crée le nouveau badge
    new_badge = models.Badge(
        titre_badge = badge_data.titre_badge,
        description_badge = badge_data.description_badge,
        image_badge = badge_data.image_badge
    )

    try:
        db.add(new_badge)
        db.commit()
        db.refresh(new_badge)
    except Exception as e:
        db.rollback()  # Rollback en cas d'erreur
        raise HTTPException(status_code=500, detail=f"Erreur pendant l'ajout du badge: {str(e)}")
    
    return new_badge

@app.post("/gain_badge", response_model=UtilisateurBadgeModele)
async def ajout_gain_badge(
    current_user: Annotated[models.Utilisateur, Depends(get_utilisateur_courant)],
    id_badge: int,
    db: Session = Depends(get_db)):
    new_gain = models.UtilisateurBadge(
        pseudo_utilisateur = current_user.pseudo,
        id_badge=id_badge
    )
    
    try:
        db.add(new_gain)
        db.commit()
        db.refresh(new_gain)
    except Exception as e:
        db.rollback()  # Rollback en cas d'erreur
        raise HTTPException(status_code=500, detail=f"Erreur pendant l'ajout du gain de badge: {str(e)}")
    
    return new_gain

@app.get("/badge/{pseudo}", response_model=List[BadgeModele])
async def lire_ses_badges(
    pseudo: str,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    # Query only badges belonging to the authenticated user
    infos_badges = db.query(models.UtilisateurBadge).filter(models.UtilisateurBadge.pseudo_utilisateur == pseudo).offset(skip).limit(limit).all()
    # Serialize database models into Pydantic models
    
    badges = [db.query(models.Badge).filter(models.Badge.id_badge == badge.id_badge).first() for badge in infos_badges]
    badges = [badge for badge in badges if badge is not None]  # Enlever les valeurs None
    return badges