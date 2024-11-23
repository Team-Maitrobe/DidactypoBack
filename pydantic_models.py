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

class DefiBase(BaseModel):
    titre_defi: str
    description_defi: str

class DefiModele(DefiBase):
    id_defi: int

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