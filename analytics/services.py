from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from app.api.models import AnalyticsSummary
from app.auth.models import User
from app.analytics import schemas


# -------------------------
# User analytics
# -------------------------
async def get_user_analytics(
    db: AsyncSession,
    user: User
):
    """
    User can only see analytics for their own API keys
    """
    result = await db.execute(
        select(AnalyticsSummary)
        .where(AnalyticsSummary.api_key_id.in_(
            [key.id for key in user.api_keys]
        ))
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
