from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

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
    
class SousCours(Base):
    __tablename__ = 'SOUSCOURS'

    id_cours_parent = Column(Integer, ForeignKey('COURS.id_cours'), nullable=False, primary_key=True)
    id_sous_cours = Column(Integer, nullable=False, primary_key=True)
    titre_sous_cours = Column(String(128), nullable=True)
    contenu_cours = Column(String(1024), nullable=True)
    chemin_img_sous_cours = Column(String(128), nullable=True)

class Groupe(Base):
    __tablename__ = 'GROUPE'
    id_groupe = Column(Integer, primary_key=True, autoincrement=True)
    nom_groupe = Column(String(128), nullable=False)
    description_groupe = Column(String(1024), nullable=False)
    
    # Définition de la relation entre Groupe et UtilisateurGroupe
    # Lorsque le groupe est supprimé, toutes les relations dans UtilisateurGroupe sont supprimées
    utilisateurs = relationship("UtilisateurGroupe", back_populates="groupe", cascade="all, delete-orphan")

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

class Exercice(Base):
    __tablename__ = 'EXERCICE'

    id_exercice = Column(Integer, primary_key=True, autoincrement=True)
    titre_exercice = Column(String)
    description_exercice = Column(String)
    
    
# Tables de jointure

class UtilisateurCours(Base):
    __tablename__ = 'UTILISATEUR_COURS'
    pseudo_utilisateur = Column(String(15), ForeignKey('UTILISATEUR.pseudo'), primary_key=True)
    id_cours = Column(Integer, ForeignKey('COURS.id_cours'), primary_key=True)
    progression = Column(Integer, nullable=False, default=0)
    
class UtilisateurGroupe(Base):
    __tablename__ = 'UTILISATEUR_GROUPE'
    pseudo_utilisateur = Column(String(15), ForeignKey('UTILISATEUR.pseudo'), primary_key=True)
    est_admin = Column(Boolean, nullable=False)
    id_groupe = Column(Integer, ForeignKey('GROUPE.id_groupe'), primary_key=True)
    
     # Relation inverse avec Groupe
    groupe = relationship("Groupe", back_populates="utilisateurs")
    
class UtilisateurDefi(Base):
    __tablename__ = 'UTILISATEUR_DEFI'
    pseudo_utilisateur = Column(String(15), ForeignKey('UTILISATEUR.pseudo'), primary_key=True)
    id_defi = Column(Integer, ForeignKey('DEFI.id_defi'), primary_key=True)
    temps_reussite =Column(Float, nullable=True)
    date_reussite = Column(DateTime, nullable=False, default=datetime.now, primary_key=True)
    
class UtilisateurBadge(Base):
    __tablename__ = 'UTILISATEUR_BADGE'
    pseudo_utilisateur = Column(String(15), ForeignKey('UTILISATEUR.pseudo'), primary_key=True)
    id_badge = Column(Integer, ForeignKey('BADGES.id_badge'), primary_key=True)
    
class GroupeCours(Base):
    __tablename__ = 'GROUPE_COURS'
    id_groupe = Column(Integer, ForeignKey('GROUPE.id_groupe'), primary_key=True)
    id_cours = Column(Integer, ForeignKey('COURS.id_cours'), primary_key=True)
