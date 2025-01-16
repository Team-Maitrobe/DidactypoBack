# Backend Didactypo
```bash
python3 -m venv env
python.exe -m pip install --upgrade pip #pour mettre à jour
source env/bin/activate #si vous êtes sur Linux
.\env\Scripts\Activate #si vous êtes sur Windows

# il faudra peut être éxécuter cette commande en tant qu'administrateur
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# installer les librairies nécéssaires
pip install -r requirements.txt
uvicorn main:app --reload
```
Puis naviguer à l'adresse suivante : http://127.0.0.1:8000/docs