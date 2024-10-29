from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean

class Utilisateur(Base):
    __tablename__ = 'UTILISATEUR'
    pseudo = Column(String(15), primary_key=True, nullable=False)
    mot_de_passe = Column(String(255), nullable=False)
    nom = Column(String(64))
    prenom = Column(String(64))
    courriel = Column(String(128))
    est_admin = Column(Boolean, nullable=False, default=False)
    moyMotsParMinute = Column(Integer, default=0)
    numCours = Column(Integer)
    tempsTotal = Column(Integer)

