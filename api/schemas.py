# backend/app/api/schemas.py

from typing import List, Optional
from pydantic import BaseModel


# -------------------------
# API Schemas
# -------------------------
class APIBase(BaseModel):
    name: str
    endpoint: str
    method: Optional[str] = "GET"
    enabled: Optional[bool] = True


class APICreate(APIBase):
    pass


class APIUpdate(BaseModel):
    name: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    enabled: Optional[bool] = None


class APIOut(APIBase):
    id: str

    class Config:
        from_attributes = True


class APIResponse(BaseModel):
    data: APIOut
    message: str


class APIsListResponse(BaseModel):
    data: List[APIOut]
    message: str


# -------------------------
# Tier Schemas
# -------------------------
class TierBase(BaseModel):
    name: str
    description: Optional[str] = None


class TierCreate(TierBase):
    requests_per_minute: int


class TierUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    requests_per_minute: Optional[int] = None


class TierOut(TierBase):
    id: str
    requests_per_minute: int

    class Config:
        from_attributes = True


class TierResponse(BaseModel):
    data: TierOut
    message: str


class TiersListResponse(BaseModel):
    data: List[TierOut]
    message: str


# -------------------------
# API Key Schemas
# -------------------------
class APIKeyCreate(BaseModel):
    api_id: str
    tier_id: str


class APIKeyOut(BaseModel):
    id: str
    key_value: str
    enabled: bool
    api_id: str
    tier_id: str

    class Config:
        from_attributes = True


class APIKeyResponse(BaseModel):
    data: APIKeyOut
    message: str


class APIKeysListResponse(BaseModel):
    data: List[APIKeyOut]
    message: str
