from pydantic import BaseModel
from typing import Optional


class AssetCreate(BaseModel):
    name: str
    type: str
    status: str
    owner: str


class AssetUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    owner: Optional[str] = None


class AssetResponse(BaseModel):
    id: int
    name: str
    type: str
    status: str
    owner: str
    created_at: str