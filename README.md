# Asset Inventory App

## Stack technique

- **Backend** : Python 3.12 + FastAPI + SQLite

## Lancer en local

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
mkdir data
$env:ADMIN_USER="admin"; $env:ADMIN_PASS="admin"; $env:DB_PATH=".\data\assets.db"
uvicorn app.main:app --reload
```

App disponible sur http://localhost:8000

## Endpoints

 Méthode  Route  Description 
-----------------------------|
 GET | /health - Health check 
 GET | /assets - Lister les assets 
 POST | /assets - Créer un asset 
 PUT | /assets/{id} - Modifier un asset 
 DELETE | /assets/{id} - Supprimer un asset 