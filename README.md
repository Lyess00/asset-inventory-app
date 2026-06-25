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

## Tests

```bash
pytest tests/ -v
```

11 tests unitaires avec mock DB couvrant CRUD, auth, et validation.

## Frontend

Interface disponible sur `/static/index.html` permettant de gérer les assets via le navigateur.

Ajoute dans le README la section frontend comme ça :
markdown## Frontend

Interface web disponible sur `/static/index.html`.

Fonctionnalités :
- Affichage de la liste des assets en temps réel
- Ajout d'un asset (nom, type, statut, date d'expiration)
- Suppression d'un asset
- Badge de santé du système (appel `/health` au chargement)
- Gestion des statuts colorés : `active` (vert), `expired` (rouge), `decommissioned` (gris)

Stack : HTML + Bootstrap 5 + JavaScript vanilla, pas de framework frontend.

> Les opérations d'écriture (POST, DELETE) nécessitent une authentification Basic Auth.


## Infrastructure

Terraform gère l'infrastructure AWS :
- ECS Fargate + ALB
- ECR
- CloudWatch Logs + Dashboard + Alarme SNS
- IAM roles + OIDC GitHub Actions
- ACM certificat HTTPS