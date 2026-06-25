import os
import secrets
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from app.database import init_db, get_db
from app.models import AssetCreate, AssetUpdate, AssetResponse
from typing import List

app = FastAPI(title="Asset Inventory")
security = HTTPBasic()

ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASS = os.environ.get("ADMIN_PASS", "admin")


@app.on_event("startup")
def startup():
    init_db()


def auth(credentials: HTTPBasicCredentials = Depends(security)):
    ok_user = secrets.compare_digest(credentials.username, ADMIN_USER)
    ok_pass = secrets.compare_digest(credentials.password, ADMIN_PASS)
    if not (ok_user and ok_pass):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return credentials.username


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/assets", response_model=List[AssetResponse])
def list_assets(user=Depends(auth)):
    conn = get_db()
    rows = conn.execute("SELECT * FROM assets").fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.post("/assets", response_model=AssetResponse, status_code=201)
def create_asset(asset: AssetCreate, user=Depends(auth)):
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO assets (name, type, status, owner) VALUES (?, ?, ?, ?)",
        (asset.name, asset.type, asset.status, asset.owner)
    )
    conn.commit()
    row = conn.execute("SELECT * FROM assets WHERE id=?", (cur.lastrowid,)).fetchone()
    conn.close()
    return dict(row)


@app.put("/assets/{asset_id}", response_model=AssetResponse)
def update_asset(asset_id: int, asset: AssetUpdate, user=Depends(auth)):
    conn = get_db()
    existing = conn.execute("SELECT * FROM assets WHERE id=?", (asset_id,)).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Asset not found")
    updated = {**dict(existing), **asset.model_dump(exclude_none=True)}
    conn.execute(
        "UPDATE assets SET name=?, type=?, status=?, owner=? WHERE id=?",
        (updated["name"], updated["type"], updated["status"], updated["owner"], asset_id)
    )
    conn.commit()
    row = conn.execute("SELECT * FROM assets WHERE id=?", (asset_id,)).fetchone()
    conn.close()
    return dict(row)


@app.delete("/assets/{asset_id}", status_code=204)
def delete_asset(asset_id: int, user=Depends(auth)):
    conn = get_db()
    existing = conn.execute("SELECT * FROM assets WHERE id=?", (asset_id,)).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Asset not found")
    conn.execute("DELETE FROM assets WHERE id=?", (asset_id,))
    conn.commit()
    conn.close()


app.mount("/static", StaticFiles(directory="app/static"), name="static")