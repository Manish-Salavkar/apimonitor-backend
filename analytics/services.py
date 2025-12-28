from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from app.api.models import AnalyticsSummary, APIKey
from app.auth.models import User
from app.analytics import schemas
from sqlalchemy.orm import selectinload


# -------------------------
# User analytics
# -------------------------
async def get_user_analytics(db: AsyncSession, user):
    # 🔹 Explicitly load user's API keys
    result = await db.execute(
        select(APIKey.id)
        .where(APIKey.user_id == user.id)
    )

    api_key_ids = [row[0] for row in result.all()]

    if not api_key_ids:
        return {
            "data": [],
            "message": "No analytics found"
        }

    result = await db.execute(
        select(AnalyticsSummary)
        .where(AnalyticsSummary.api_key_id.in_(api_key_ids))
        .order_by(AnalyticsSummary.window_start.desc())
    )

    rows = result.scalars().all()

    return {
        "data": [
            schemas.AnalyticsOut.model_validate(row).model_dump()
            for row in rows
        ],
        "message": "User analytics fetched successfully"
    }

# -------------------------
# Admin analytics
# -------------------------
async def get_admin_analytics(db: AsyncSession):
    """
    Admin can see all analytics
    """
    result = await db.execute(
        select(AnalyticsSummary)
        # .options(selectinload(AnalyticsSummary.api))
        .order_by(AnalyticsSummary.window_start.desc())
    )

    rows = result.scalars().all()

    return {
        "data": [
            schemas.AnalyticsOut.model_validate(row).model_dump()
            for row in rows
        ],
        "message": "Admin analytics fetched successfully"
    }
