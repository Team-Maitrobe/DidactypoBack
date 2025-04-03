README du back

Backend Didactypo
Structure du Backend
Le backend de Didactypo est structuré comme suit :

* main.py : Le point d'entrée de l'application où le serveur est initialisé.
* auth.py : La logique d'authentification de l'application.
* database.py : La création et la connexion à la BD, certaines fonctions de requêtes SQL.
* models.py : La structure des tables de la BD.
* pydantic_models.py : Les modèles Pydantic utilisés pour la validation des données et la communication avec le frontend.
* createDB.sql : Ne sert à rien, représente juste la structure de la BD.
* exercices.sql : Fichier contenant les requêtes SQL pour ajouter les exercices.
* cours.sql : Fichier contenant les requêtes SQL pour ajouter les cours.

## Configuration des variables d'environnement

Le projet utilise des variables d'environnement pour les paramètres sensibles:

1. Copier le fichier `.env.example` en `.env`:
```
cp .env.example .env
```

2. Générer une clé secrète JWT et l'ajouter dans le fichier `.env`:
```
# Sous Linux/Mac avec OpenSSL
openssl rand -hex 32

# Alternative avec Python
python -c "import secrets; print(secrets.token_hex(32))"
```

3. Modifier les autres paramètres selon les besoins

## Initialiser l'environnement virtuel
```
python3 -m venv env
python.exe -m pip install --upgrade pip #pour mettre à jour
source env/bin/activate #si vous êtes sur Linux
.\env\Scripts\Activate #si vous êtes sur Windows

# il faudra peut être éxécuter cette commande en tant qu'administrateur
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Installer / ajouter les librairies nécéssaires
```
pip install -r requirements.txt

pip install [nom de la librairie] # pour ajouter une librairie
pip check # vérifie pour les conflits et les mises à jour
pip freeze > requirements.txt # pour mettre à jour le fichier requirements.txt
```

## Lancer le serveur de développement en local
```
uvicorn main:app --reload
```

Puis naviguer à l'adresse suivante : http://127.0.0.1:8000/docs 