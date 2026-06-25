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

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | /health | Health check |
| GET | /assets | Lister les assets |
| POST | /assets | Créer un asset |
| PUT | /assets/{id} | Modifier un asset |
| DELETE | /assets/{id} | Supprimer un asset |

## Docker

```bash
docker build -t asset-inventory-app .
docker run -p 8000:8000 -e ADMIN_USER=admin -e ADMIN_PASS=admin asset-inventory-app
```

> En production, les credentials sont injectés via AWS Secrets Manager.