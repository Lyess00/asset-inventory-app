import logging
import os
import threading
import time
from datetime import date, datetime
from typing import List

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
import secrets

from app.models import AssetCreate, AssetUpdate, AssetResponse
from app.database import get_connection, init_db

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialisation de l'application
app = FastAPI(title="Asset Inventory API")

# Sécurité Basic Auth
security = HTTPBasic()


def update_expired_assets():
    while True:
        try:
            conn = get_connection()
            today = date.today().isoformat()
            conn.execute(
                "UPDATE assets SET status='expired' WHERE expiry_date IS NOT NULL AND expiry_date < ? AND status != 'decommissioned'",
                (today,)
            )
            conn.commit()
            conn.close()
            logger.info('{"event": "expired_assets_updated"}')
        except Exception as e:
            logger.error('{"event": "expired_update_error", "error": "%s"}', str(e))
        time.sleep(3600)


@app.on_event("startup")
def startup():
    init_db()
    logger.info('{"event": "app_started"}')
    thread = threading.Thread(target=update_expired_assets, daemon=True)
    thread.start()


# Montage des fichiers statiques
app.mount("/static", StaticFiles(directory="app/static"), name="static")


# ---- Vérification des credentials ----
def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_user = secrets.compare_digest(
        credentials.username,
        os.environ.get("ADMIN_USER", "admin")
    )
    correct_pass = secrets.compare_digest(
        credentials.password,
        os.environ.get("ADMIN_PASS", "admin")
    )
    if not (correct_user and correct_pass):
        raise HTTPException(status_code=401, detail="Unauthorized")


# ---- Routes GET (lecture, publiques) ----
@app.get("/assets", response_model=List[AssetResponse])
def get_assets():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM assets ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.get("/assets/expiring", response_model=List[AssetResponse])
def get_expiring_assets():
    today = date.today().isoformat()
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM assets WHERE expiry_date IS NOT NULL AND expiry_date <= ? ORDER BY expiry_date ASC",
        (today,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.get("/assets/{asset_id}", response_model=AssetResponse)
def get_asset(asset_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM assets WHERE id = ?", (asset_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Asset not found")
    return dict(row)


# ---- Routes POST/PUT/DELETE (écriture, protégées) ----
@app.post("/assets", response_model=AssetResponse, status_code=201)
def create_asset(asset: AssetCreate, _=Depends(verify_credentials)):
    conn = get_connection()
    created_at = datetime.utcnow().date().isoformat()
    cursor = conn.execute(
        "INSERT INTO assets (name, asset_type, status, expiry_date, created_at) VALUES (?, ?, ?, ?, ?)",
        (asset.name, asset.asset_type, asset.status,
         asset.expiry_date.isoformat() if asset.expiry_date else None,
         created_at)
    )
    conn.commit()
    row = conn.execute("SELECT * FROM assets WHERE id = ?", (cursor.lastrowid,)).fetchone()
    conn.close()
    logger.info('{"event": "asset_created", "asset_id": %d}', cursor.lastrowid)
    return dict(row)


@app.put("/assets/{asset_id}", response_model=AssetResponse)
def update_asset(asset_id: int, asset: AssetUpdate, _=Depends(verify_credentials)):
    conn = get_connection()
    row = conn.execute("SELECT * FROM assets WHERE id = ?", (asset_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Asset not found")
    current = dict(row)
    updated = {
        "name": asset.name if asset.name is not None else current["name"],
        "asset_type": asset.asset_type if asset.asset_type is not None else current["asset_type"],
        "status": asset.status if asset.status is not None else current["status"],
        "expiry_date": asset.expiry_date.isoformat() if asset.expiry_date else current["expiry_date"],
    }
    conn.execute(
        "UPDATE assets SET name=?, asset_type=?, status=?, expiry_date=? WHERE id=?",
        (updated["name"], updated["asset_type"], updated["status"], updated["expiry_date"], asset_id)
    )
    conn.commit()
    row = conn.execute("SELECT * FROM assets WHERE id = ?", (asset_id,)).fetchone()
    conn.close()
    logger.info('{"event": "asset_updated", "asset_id": %d}', asset_id)
    return dict(row)


@app.delete("/assets/{asset_id}", status_code=204)
def delete_asset(asset_id: int, _=Depends(verify_credentials)):
    conn = get_connection()
    row = conn.execute("SELECT * FROM assets WHERE id = ?", (asset_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Asset not found")
    conn.execute("DELETE FROM assets WHERE id = ?", (asset_id,))
    conn.commit()
    conn.close()
    logger.info('{"event": "asset_deleted", "asset_id": %d}', asset_id)


# ---- Health check ----
@app.get("/health")
def health():
    return {"status": "ok", "database": "ok", "timestamp": datetime.utcnow().isoformat()}