# backend/app/api/routes.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, db_commit
from app.api import services, schemas
from app.auth.services import get_current_user
from app.auth.models import User

api_router = APIRouter(prefix="/apis", tags=["APIs"])
tier_router = APIRouter(prefix="/tiers", tags=["Tiers"])
key_router = APIRouter(prefix="/api-keys", tags=["API Keys"])


# -------------------------
# API Routes
# -------------------------
@api_router.post(
    "/",
    response_model=schemas.APIResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_api(
    api: schemas.APICreate,
    db: AsyncSession = Depends(get_db)
):
    result = await services.create_api(db, api)
    await db_commit(db)
    return result


@api_router.get(
    "/",
    response_model=schemas.APIsListResponse
)
async def list_apis(db: AsyncSession = Depends(get_db)):
    return await services.list_apis(db)


# -------------------------
# Tier Routes
# -------------------------
@tier_router.post(
    "/",
    response_model=schemas.TierResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_tier(
    tier: schemas.TierCreate,
    db: AsyncSession = Depends(get_db)
):
    result = await services.create_tier(db, tier)
    await db_commit(db)
    return result


@tier_router.get(
    "/",
    response_model=schemas.TiersListResponse
)
async def list_tiers(db: AsyncSession = Depends(get_db)):
    return await services.list_tiers(db)


# -------------------------
# API Key Routes
# -------------------------
@key_router.post(
    "/",
    response_model=schemas.APIKeyResponse,
    status_code=status.HTTP_201_CREATED
)
async def generate_api_key(
    payload: schemas.APIKeyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await services.generate_api_key(
        db=db,
        user_id=current_user.id,
        payload=payload
    )
    await db_commit(db)
    return result
