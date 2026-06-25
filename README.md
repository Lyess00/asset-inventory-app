# Asset Inventory App

Application de gestion d'inventaire d'assets, containerisée et déployée sur AWS.

## Stack technique

- **Backend** : Python 3.12 + FastAPI + SQLite
- **Frontend** : HTML + Bootstrap 5 + JavaScript vanilla
- **Auth** : HTTP Basic Auth
- **Conteneurisation** : Docker multi-stage, utilisateur non-root
- **CI/CD** : GitHub Actions (lint + tests + build + push ECR + deploy ECS)
- **Infrastructure** : Terraform + AWS ECS Fargate + ALB
- **Observabilité** : CloudWatch Logs + Dashboard + Alarme SNS
- **Sécurité** : OIDC GitHub→AWS + Secrets Manager + ACM HTTPS

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

## Docker

```bash
docker build -t asset-inventory-app .
docker run -p 8000:8000 -e ADMIN_USER=admin -e ADMIN_PASS=admin asset-inventory-app
```

> En production, les credentials sont injectés via AWS Secrets Manager.

## Endpoints

| Méthode | Route | Auth | Description |
|---------|-------|------|-------------|
| GET | /health | Non | Health check |
| GET | /assets | Non | Lister les assets |
| GET | /assets/{id} | Non | Récupérer un asset |
| GET | /assets/expiring | Non | Assets expirés |
| POST | /assets | Oui | Créer un asset |
| PUT | /assets/{id} | Oui | Modifier un asset |
| DELETE | /assets/{id} | Oui | Supprimer un asset |

## Frontend

Interface web disponible sur `/static/index.html`.

Fonctionnalités :
- Affichage de la liste des assets en temps réel
- Ajout d'un asset (nom, type, statut, date d'expiration)
- Suppression d'un asset
- Badge de santé du système (appel `/health` au chargement)
- Gestion des statuts colorés : `active` (vert), `expired` (rouge), `decommissioned` (gris)

> Les opérations d'écriture nécessitent une authentification Basic Auth.
> En production, remplacer par AWS Cognito avec tokens JWT.

## Tests

```bash
pytest tests/ -v
```

11 tests unitaires avec mock DB couvrant CRUD, auth, et validation.

## Infrastructure

Terraform gère l'infrastructure AWS :
- ECS Fargate + ALB (HTTPS, redirection HTTP→HTTPS)
- ECR (scan automatique, lifecycle policy 5 images)
- CloudWatch Logs + Dashboard + Alarme SNS sur erreurs 5xx
- IAM roles + OIDC GitHub Actions (pas de clés AWS stockées)
- ACM certificat HTTPS pour www.asset-inventory.tech

## Comportement sous charge

L'ALB distribue le trafic vers les tâches ECS. ECS Fargate permet de scaler horizontalement en augmentant le `desired_count` du service. Le dashboard CloudWatch monitore les requêtes/min, la latence et les erreurs 5xx en temps réel.

## Limitations connues et améliorations

| Limitation | Amélioration |
|-----------|-------------|
| SQLite local au conteneur → perte de données à chaque redéploiement | Migrer sur AWS RDS PostgreSQL ou attacher un volume EFS |
| HTTP Basic Auth compte unique | AWS Cognito avec tokens JWT |
| State Terraform local | Backend S3 + DynamoDB pour le state distant |
| Pas d'auto-scaling | AWS Application Auto Scaling sur métriques CPU/mémoire |
| Pas de WAF | AWS WAF devant l'ALB |