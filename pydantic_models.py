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
        orm_mode = True

class UtilisateurDefiBase(BaseModel):
    id_defi: int
    pseudo_utilisateur: str
    temps_reussite: float

class UtilisateurDefiModele(UtilisateurDefiBase):
    date_reussite: datetime

    class Config:
        orm_mode = True 

class CoursBase(BaseModel):
    titre_cours : str
    description_cours : str
    duree_cours : int
    difficulte_cours : int

class CoursModele(CoursBase):
    id_cours : int

    class Config:
        orm_mode = True

class SousCoursBase(BaseModel):
    id_cours_parent: int
    titre_sous_cours: str
    contenu_cours: str
    chemin_img_sous_cours: str = None

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

