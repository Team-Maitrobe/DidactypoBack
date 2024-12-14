from typing import Optional
from pydantic import BaseModel
from datetime import datetime

# Pydantic Models for validation and serialization
class UtilisateurBase(BaseModel):
    pseudo: str
    mot_de_passe: str
    nom: str
    prenom: str
    courriel: str
    est_admin: bool
    moyMotsParMinute: int
    numCours: int
    tempsTotal: int

class UtilisateurModele(UtilisateurBase):
    class Config:
        orm_mode = True 

#Utilisé uniquement pour afficher les statistiques d'un utilisateur
class StatsUtilisateur(BaseModel):
    moyMotsParMinute: str
    numCours: str
    tempsTotal: str

class DefiBase(BaseModel):
    titre_defi: str
    description_defi: str

class DefiModele(DefiBase):
    id_defi: int

    class Config:
        orm_mode = True 

class BadgeBase(BaseModel):
    titre_badge: str
    description_badge: str
    image_badge: str

class BadgeModele(BadgeBase):
    id_badge: int

    class Config:
        from_attributes = True

class UtilisateurDefiBase(BaseModel):
    id_defi: int
    pseudo_utilisateur: str
    temps_reussite: float

class UtilisateurDefiModele(UtilisateurDefiBase):
    date_reussite: datetime

    class Config:
        orm_mode = True 

class CoursBase(BaseModel):
    titre_cours: str
    description_cours: str
    duree_cours: int
    difficulte_cours: int

class CoursModele(CoursBase):
    id_cours: int

    class Config:
        orm_mode = True

class SousCoursBase(BaseModel):
    id_cours_parent: int
    titre_sous_cours: Optional[str] = ""  # Valeur par défaut si None
    contenu_cours: Optional[str] = ""
    chemin_img_sous_cours: Optional[str] = ""  # Valeur par défaut si None

    class Config:
        orm_mode = True

class SousCoursModele(SousCoursBase):
    id_sous_cours: int

    class Config:
        orm_mode = True

class GroupeBase(BaseModel):
    nom_groupe : str
    description_groupe : str

class GroupeModele(GroupeBase):
    id_groupe : int

    class Config:
        orm_mode = True

class UtilisateurGroupeBase(BaseModel):
        pseudo_utilisateur : str
        id_groupe : int
        est_admin : bool

class UtilisateurGroupeModele(UtilisateurGroupeBase):
    class Config:
        orm_mode = True 

class UtilisateurCoursBase(BaseModel):
    pseudo_utilisateur: str
    id_cours: int
    progression: int

class UtilisateurCoursModele(UtilisateurCoursBase):
    class Config:
        orm_mode = True
        
class UtilisateurBadgeBase(BaseModel):
    pseudo_utilisateur: str
    id_badge: int

class UtilisateurBadgeModele(UtilisateurBadgeBase):
    class Config:
        orm_mode = True