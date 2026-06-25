from pydantic import BaseModel
from typing import Optional
from datetime import date

class AssetCreate(BaseModel):
    name: str
    asset_type: str
    status: str = "active"
    expiry_date: Optional[date] = None

class AssetUpdate(BaseModel):
    name: Optional[str] = None
    asset_type: Optional[str] = None
    status: Optional[str] = None
    expiry_date: Optional[date] = None

class AssetResponse(BaseModel):
    id: int
    name: str
    asset_type: str
    status: str
    expiry_date: Optional[date] = None
    created_at: str