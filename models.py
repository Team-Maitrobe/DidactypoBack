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

class Cours(Base):
    __tablename__ = 'COURS'
    id_cours = Column(Integer, primary_key=True, autoincrement=True)
    titre_cours = Column(String(128), nullable=False)
    description_cours = Column(String(1024), nullable=False)
    duree_cours = Column(Integer, nullable=False)
    difficulte_cours = Column(Integer, nullable=False)

class Groupe(Base):
    __tablename__ = 'GROUPE'
    id_groupe = Column(Integer, primary_key=True, autoincrement=True)
    nom_groupe = Column(String(128), nullable=False)
    description_groupe = Column(String(1024), nullable=False)

class Defi(Base):
    __tablename__ = 'DEFI'
    id_defi = Column(Integer, primary_key=True, autoincrement=True)
    titre_defi = Column(String(128), nullable=False)
    description_defi = Column(String(1024), nullable=False)

class Badge(Base):
    __tablename__ = 'BADGES'
    id_badge = Column(Integer, primary_key=True, autoincrement=True)
    titre_badge = Column(String(128), nullable=False)
    description_badge = Column(String(1024), nullable=False)
    image_badge = Column(String(128), nullable=False)
    
# Tables de jointure

class UtilisateurCours(Base):
    __tablename__ = 'UTILISATEUR_COURS'
    id_utilisateur = Column(String(15), ForeignKey('UTILISATEUR.pseudo'), primary_key=True)
    id_cours = Column(Integer, ForeignKey('COURS.id_cours'), primary_key=True)
    progression = Column(Integer, nullable=False, default=0)
    
class UtilisateurGroupe(Base):
    __tablename__ = 'UTILISATEUR_GROUPE'
    id_utilisateur = Column(String(15), ForeignKey('UTILISATEUR.pseudo'), primary_key=True)
    id_groupe = Column(Integer, ForeignKey('GROUPE.id_groupe'), primary_key=True)
    
class UtilisateurDefi(Base):
    __tablename__ = 'UTILISATEUR_DEFI'
    id_utilisateur = Column(String(15), ForeignKey('UTILISATEUR.pseudo'), primary_key=True)
    id_defi = Column(Integer, ForeignKey('DEFI.id_defi'), primary_key=True)
    date_reussite = Column(String(11), nullable=True)
    
class UtilisateurBadge(Base):
    __tablename__ = 'UTILISATEUR_BADGE'
    id_utilisateur = Column(String(15), ForeignKey('UTILISATEUR.pseudo'), primary_key=True)
    id_badge = Column(Integer, ForeignKey('BADGES.id_badge'), primary_key=True)
    
class GroupeCours(Base):
    __tablename__ = 'GROUPE_COURS'
    id_groupe = Column(Integer, ForeignKey('GROUPE.id_groupe'), primary_key=True)
    id_cours = Column(Integer, ForeignKey('COURS.id_cours'), primary_key=True)
