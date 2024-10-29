CREATE DATABASE DIDACTYPO;

CREATE TABLE DIDACTYPO.UTILISATEUR (
    pseudo VARCHAR(15) NOT NULL,
    mot_de_passe VARCHAR(255) NOT NULL,
    nom VARCHAR(64),
    prenom VARCHAR(64),
    courriel VARCHAR(128),
    est_admin BOOLEAN NOT NULL DEFAULT FALSE,
    moyMotsParMinute INT DEFAULT 0,
    numCours INT,
    tempsTotal INT,

    PRIMARY KEY (pseudo)
);

CREATE TABLE DIDACTYPO.COURS (
    id_cours INT NOT NULL AUTO_INCREMENT,
    titre_cours VARCHAR(128) NOT NULL,
    description_cours VARCHAR(1024) NOT NULL,
    duree_cours INT NOT NULL,
    difficulte_cours INT NOT NULL,

    PRIMARY KEY (id_cours),
);

CREATE TABLE DIDACTYPO.GROUPE (
    id_groupe INT NOT NULL AUTO_INCREMENT,
    nom_groupe VARCHAR(128) NOT NULL,
    description_groupe VARCHAR(1024) NOT NULL,

    PRIMARY KEY (id_groupe),
);

CREATE TABLE DIDACTYPO.DEFI (
    id_defi INT NOT NULL AUTO_INCREMENT,
    titre_defi VARCHAR(128) NOT NULL,
    description_defi VARCHAR(1024) NOT NULL,   

    PRIMARY KEY (id_defi),
);

CREATE TABLE DIDACTYPO.BADGES (
    id_badge INT NOT NULL AUTO_INCREMENT,
    titre_badge VARCHAR(128) NOT NULL,
    description_badge VARCHAR(1024) NOT NULL,
    image_badge VARCHAR(128) NOT NULL,

    PRIMARY KEY (id_badge),
);

-- Tables de jointure

CREATE TABLE DIDACTYPO.GROUPE_UTILISATEUR (
    id_groupe INT NOT NULL,
    pseudo VARCHAR(15) NOT NULL,
    est_admin BOOLEAN NOT NULL DEFAULT FALSE,

    PRIMARY KEY (id_groupe, pseudo),

    FOREIGN KEY (id_groupe) REFERENCES DIDACTYPO.GROUPE(id_groupe),
    FOREIGN KEY (pseudo) REFERENCES DIDACTYPO.UTILISATEUR(pseudo)
);

CREATE TABLE DIDACTYPO.COURS_UTILISATEUR (
    id_cours INT NOT NULL,
    pseudo VARCHAR(15) NOT NULL,
    dateRéussite DATE,

    PRIMARY KEY (id_cours, pseudo),

    FOREIGN KEY (id_cours) REFERENCES DIDACTYPO.COURS(id_cours),
    FOREIGN KEY (pseudo) REFERENCES DIDACTYPO.UTILISATEUR(pseudo)
);

CREATE TABLE DIDACTYPO.DEFI_UTILISATEUR (
    id_defi INT NOT NULL,
    pseudo VARCHAR(15) NOT NULL,
    dateRéussite DATE,

    PRIMARY KEY (id_defi, pseudo),

    FOREIGN KEY (id_defi) REFERENCES DIDACTYPO.DEFI(id_defi),
    FOREIGN KEY (pseudo) REFERENCES DIDACTYPO.UTILISATEUR(pseudo)
);

CREATE TABLE DIDACTYPO.BADGES_UTILISATEUR (
    id_badge INT NOT NULL,
    pseudo VARCHAR(15) NOT NULL,
    dateObtention DATE,

    PRIMARY KEY (id_badge, pseudo),

    FOREIGN KEY (id_badge) REFERENCES DIDACTYPO.BADGES(id_badge),
    FOREIGN KEY (pseudo) REFERENCES DIDACTYPO.UTILISATEUR(pseudo)
);