from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from app.api.models import AnalyticsSummary, APIKey, UsageLog
from app.auth.models import User
from app.api.models import API, UsageLog
from app.analytics import schemas
from sqlalchemy.orm import selectinload
from sqlalchemy import func


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


async def get_user_usage_stats(db: AsyncSession):
    """
    Returns analytics focused on User activity:
    1. API Summary: How many unique users hit each API.
    2. User Activity: Detailed breakdown of (User -> API) call counts.
    """
    
    # 1. API Summary: Group by API Name
    # Counts total calls and unique users per API
    api_summary_stmt = (
        select(
            API.name,
            func.count(func.distinct(UsageLog.user_id)).label("unique_users"),
            func.count(UsageLog.id).label("total_calls")
        )
        .join(UsageLog, API.id == UsageLog.api_id)
        .group_by(API.name)
    )
    
    api_summary_result = await db.execute(api_summary_stmt)
    api_summary_rows = api_summary_result.all()

    # 2. User Activity: Group by User AND API
    # Shows "User A called API X 50 times, last active at..."
    user_activity_stmt = (
        select(
            User.username,
            API.name,
            func.count(UsageLog.id).label("total_calls"),
            func.max(UsageLog.timestamp).label("last_called")
        )
        .join(UsageLog, User.id == UsageLog.user_id)
        .join(API, UsageLog.api_id == API.id)
        .group_by(User.username, API.name)
        .order_by(func.count(UsageLog.id).desc()) # Show heaviest users first
    )

    user_activity_result = await db.execute(user_activity_stmt)
    user_activity_rows = user_activity_result.all()

    # Structure the data
    return {
        "api_summary": [
            {
                "api_name": row.name,
                "unique_users": row.unique_users,
                "total_calls": row.total_calls
            }
            for row in api_summary_rows
        ],
        "user_activity": [
            {
                "username": row.username,
                "api_name": row.name,
                "total_calls": row.total_calls,
                "last_called": row.last_called
            }
            for row in user_activity_rows
        ]
    }