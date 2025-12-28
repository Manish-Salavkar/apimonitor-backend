# app/api/services.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
import secrets

from app.api import models, schemas


# ======================================================
# API SERVICES (CRUD)
# ======================================================

async def create_api(db: AsyncSession, api: schemas.APICreate):
    try:
        db_api = models.API(**api.model_dump())
        db.add(db_api)
        await db.flush()
        await db.refresh(db_api)

        return {
            "data": schemas.APIOut.model_validate(db_api).model_dump(),
            "message": "API created successfully"
        }

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create API"
        )


async def list_apis(db: AsyncSession):
    result = await db.execute(select(models.API))
    apis = result.scalars().all()

    return {
        "data": [schemas.APIOut.model_validate(api).model_dump() for api in apis],
        "message": "APIs fetched successfully"
    }


async def get_api(db: AsyncSession, api_id: str):
    result = await db.execute(
        select(models.API).where(models.API.id == api_id)
    )
    api = result.scalar_one_or_none()

    if not api:
        raise HTTPException(status_code=404, detail="API not found")

    return {
        "data": schemas.APIOut.model_validate(api).model_dump(),
        "message": "API fetched successfully"
    }


async def update_api(
    db: AsyncSession,
    api_id: str,
    payload: schemas.APIUpdate
):
    result = await db.execute(
        select(models.API).where(models.API.id == api_id)
    )
    api = result.scalar_one_or_none()

    if not api:
        raise HTTPException(status_code=404, detail="API not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(api, key, value)

    await db.flush()
    await db.refresh(api)

    return {
        "data": schemas.APIOut.model_validate(api).model_dump(),
        "message": "API updated successfully"
    }


async def delete_api(db: AsyncSession, api_id: str):
    result = await db.execute(
        select(models.API).where(models.API.id == api_id)
    )
    api = result.scalar_one_or_none()

    if not api:
        raise HTTPException(status_code=404, detail="API not found")

    await db.delete(api)

    return {
        "data": None,
        "message": "API deleted successfully"
    }


# ======================================================
# TIER SERVICES (CRUD)
# ======================================================

async def create_tier(db: AsyncSession, tier: schemas.TierCreate):
    try:
        db_tier = models.Tier(
            name=tier.name,
            description=tier.description
        )
        db.add(db_tier)
        await db.flush()  # get tier.id

        rate_rule = models.RateLimitRules(
            tier_id=db_tier.id,
            requests_per_minute=tier.requests_per_minute,
            requests_per_hour=tier.requests_per_hour,
            requests_per_day=tier.requests_per_day
        )
        db.add(rate_rule)

        return {
            "data": schemas.TierOut(
                id=db_tier.id,
                name=db_tier.name,
                description=db_tier.description,
                requests_per_minute=rate_rule.requests_per_minute,
                requests_per_hour=rate_rule.requests_per_hour,
                requests_per_day=rate_rule.requests_per_day,
            ).model_dump(),
            "message": "Tier created successfully"
        }

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create Tier"
        )

async def list_tiers(db: AsyncSession):
    result = await db.execute(
        select(models.Tier)
        .options(selectinload(models.Tier.rate_limit_rules))
    )
    tiers = result.scalars().all()

    response = [
        schemas.TierOut(
            id=t.id,
            name=t.name,
            description=t.description,
            requests_per_minute=t.rate_limit_rules.requests_per_minute,
            requests_per_hour=t.rate_limit_rules.requests_per_hour,
            requests_per_day=t.rate_limit_rules.requests_per_day,
        ).model_dump()
        for t in tiers
    ]

    return {
        "data": response,
        "message": "Tiers fetched successfully"
    }


async def get_tier(db: AsyncSession, tier_id: str):
    result = await db.execute(
        select(models.Tier)
        .options(selectinload(models.Tier.rate_limit_rules))
        .where(models.Tier.id == tier_id)
    )
    tier = result.scalar_one_or_none()

    if not tier:
        raise HTTPException(status_code=404, detail="Tier not found")

    return {
        "data": schemas.TierOut(
            id=tier.id,
            name=tier.name,
            description=tier.description,
            requests_per_minute=tier.rate_limit_rules.requests_per_minute,
            requests_per_hour=tier.rate_limit_rules.requests_per_hour,
            requests_per_day=tier.rate_limit_rules.requests_per_day,
        ).model_dump(),
        "message": "Tier fetched successfully"
    }


async def update_tier(
    db: AsyncSession,
    tier_id: str,
    payload: schemas.TierUpdate
):
    result = await db.execute(
        select(models.Tier)
        .options(selectinload(models.Tier.rate_limit_rules))
        .where(models.Tier.id == tier_id)
    )
    tier = result.scalar_one_or_none()

    if not tier:
        raise HTTPException(status_code=404, detail="Tier not found")

    data = payload.model_dump(exclude_unset=True)

    if "name" in data:
        tier.name = data["name"]
    if "description" in data:
        tier.description = data["description"]

    if "requests_per_minute" in data:
        tier.rate_limit_rules.requests_per_minute = data["requests_per_minute"]
    if "requests_per_hour" in data:
        tier.rate_limit_rules.requests_per_hour = data["requests_per_hour"]
    if "requests_per_day" in data:
        tier.rate_limit_rules.requests_per_day = data["requests_per_day"]

    return {
        "data": schemas.TierOut(
            id=tier.id,
            name=tier.name,
            description=tier.description,
            requests_per_minute=tier.rate_limit_rules.requests_per_minute,
            requests_per_hour=tier.rate_limit_rules.requests_per_hour,
            requests_per_day=tier.rate_limit_rules.requests_per_day,
        ).model_dump(),
        "message": "Tier updated successfully"
    }

async def delete_tier(db: AsyncSession, tier_id: str):
    result = await db.execute(
        select(models.Tier).where(models.Tier.id == tier_id)
    )
    tier = result.scalar_one_or_none()

    if not tier:
        raise HTTPException(status_code=404, detail="Tier not found")

    await db.delete(tier)

    return {
        "data": None,
        "message": "Tier deleted successfully"
    }

# ======================================================
# API KEY SERVICES (CRUD-ish)
# ======================================================

async def generate_api_key(
    db: AsyncSession,
    user_id: int,
    payload: schemas.APIKeyCreate
):
    try:
        key_value = secrets.token_hex(32)

        api_key = models.APIKey(
            key_value=key_value,
            user_id=user_id,
            api_id=payload.api_id,
            tier_id=payload.tier_id
        )

        db.add(api_key)
        await db.flush()
        await db.refresh(api_key)

        return {
            "data": schemas.APIKeyOut.model_validate(api_key).model_dump(),
            "message": "API key generated successfully"
        }

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate API key"
        )


async def list_user_api_keys(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(models.APIKey).where(models.APIKey.user_id == user_id)
    )
    keys = result.scalars().all()

    return {
        "data": [schemas.APIKeyOut.model_validate(k).model_dump() for k in keys],
        "message": "API keys fetched successfully"
    }


async def revoke_api_key(db: AsyncSession, api_key_id: str):
    result = await db.execute(
        select(models.APIKey).where(models.APIKey.id == api_key_id)
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    api_key.enabled = False
    await db.flush()
    await db.refresh(api_key)

    return {
        "data": schemas.APIKeyOut.model_validate(api_key).model_dump(),
        "message": "API key revoked successfully"
    }


async def delete_api_key(db: AsyncSession, api_key_id: str):
    result = await db.execute(
        select(models.APIKey).where(models.APIKey.id == api_key_id)
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    await db.delete(api_key)

    return {
        "data": None,
        "message": "API key deleted successfully"
    }


async def list_api_keys(db: AsyncSession):
    result = await db.execute(
        select(models.APIKey)
    )
    api_keys = result.scalars().all()

    return {
        "data": api_keys,
        "message": "API Keys fetched successfully"
    }