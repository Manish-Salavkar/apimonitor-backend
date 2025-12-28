from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, db_commit
from app.api import services, schemas
from app.auth.services import get_current_user
from app.auth.models import User

# ------------------------------------------------
# Routers
# ------------------------------------------------
api_router = APIRouter(prefix="/apis", tags=["APIs"])
tier_router = APIRouter(prefix="/tiers", tags=["Tiers"])
key_router = APIRouter(prefix="/api-keys", tags=["API Keys"])


# =================================================
# API ROUTES (ADMIN)
# =================================================

@api_router.post("/",response_model=schemas.APIResponse,status_code=status.HTTP_201_CREATED)
async def create_api(
    api: schemas.APICreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_id != 1:
        raise HTTPException(status_code=403, detail="Admin access required")

    result = await services.create_api(db, api)
    await db_commit(db)
    return result


@api_router.get("/",response_model=schemas.APIsListResponse)
async def list_apis(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await services.list_apis(db)


@api_router.get("/{api_id}",response_model=schemas.APIResponse)
async def get_api(
    api_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await services.get_api(db, api_id)


@api_router.put("/{api_id}",response_model=schemas.APIResponse)
async def update_api(
    api_id: str,
    payload: schemas.APIUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_id != 1:
        raise HTTPException(status_code=403, detail="Admin access required")

    result = await services.update_api(db, api_id, payload)
    await db_commit(db)
    return result


@api_router.delete("/{api_id}",status_code=status.HTTP_200_OK)
async def delete_api(
    api_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_id != 1:
        raise HTTPException(status_code=403, detail="Admin access required")

    result = await services.delete_api(db, api_id)
    await db_commit(db)
    return result


# =================================================
# TIER ROUTES (ADMIN)
# =================================================

@tier_router.post(
    "/",
    response_model=schemas.TierResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_tier(
    tier: schemas.TierCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_id != 1:
        raise HTTPException(status_code=403, detail="Admin access required")

    result = await services.create_tier(db, tier)
    await db_commit(db)
    return result


@tier_router.get(
    "/",
    response_model=schemas.TiersListResponse
)
async def list_tiers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await services.list_tiers(db)


@tier_router.get(
    "/{tier_id}",
    response_model=schemas.TierResponse
)
async def get_tier(
    tier_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await services.get_tier(db, tier_id)


@tier_router.put(
    "/{tier_id}",
    response_model=schemas.TierResponse
)
async def update_tier(
    tier_id: str,
    payload: schemas.TierUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_id != 1:
        raise HTTPException(status_code=403, detail="Admin access required")

    result = await services.update_tier(db, tier_id, payload)
    await db_commit(db)
    return result


@tier_router.delete(
    "/{tier_id}",
    status_code=status.HTTP_200_OK
)
async def delete_tier(
    tier_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_id != 1:
        raise HTTPException(status_code=403, detail="Admin access required")

    result = await services.delete_tier(db, tier_id)
    await db_commit(db)
    return result


# =================================================
# API KEY ROUTES (USER)
# =================================================

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


@key_router.get(
    "/",
    response_model=schemas.APIKeysListResponse
)
async def list_my_api_keys(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await services.list_user_api_keys(db, current_user.id)


@key_router.put(
    "/{api_key_id}/revoke",
    response_model=schemas.APIKeyResponse
)
async def revoke_api_key(
    api_key_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await services.revoke_api_key(db, api_key_id)
    await db_commit(db)
    return result


@key_router.delete(
    "/{api_key_id}",
    status_code=status.HTTP_200_OK
)
async def delete_api_key(
    api_key_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await services.delete_api_key(db, api_key_id)
    await db_commit(db)
    return result

@key_router.get("/all", status_code=status.HTTP_200_OK)
async def get_all_keys(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await services.list_api_keys(db)
    return result