# backend/app/api/services.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
import secrets

from app.api import models, schemas


# -------------------------
# API Services
# -------------------------
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


# -------------------------
# Tier Services
# -------------------------
async def create_tier(db: AsyncSession, tier: schemas.TierCreate):
    try:
        db_tier = models.Tier(
            name=tier.name,
            description=tier.description
        )
        db.add(db_tier)
        await db.flush()

        rate_rule = models.RateLimitRules(
            tier_id=db_tier.id,
            requests_per_minute=tier.requests_per_minute
        )
        db.add(rate_rule)

        await db.refresh(db_tier)

        return {
            "data": schemas.TierOut(
                id=db_tier.id,
                name=db_tier.name,
                description=db_tier.description,
                requests_per_minute=tier.requests_per_minute
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
    result = await db.execute(select(models.Tier))
    tiers = result.scalars().all()

    response = []
    for tier in tiers:
        response.append(
            schemas.TierOut(
                id=tier.id,
                name=tier.name,
                description=tier.description,
                requests_per_minute=tier.rate_limit_rules.requests_per_minute
            ).model_dump()
        )

    return {
        "data": response,
        "message": "Tiers fetched successfully"
    }


# -------------------------
# API Key Services
# -------------------------
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
