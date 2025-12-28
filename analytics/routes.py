from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.analytics import services, schemas
from app.auth.services import get_current_user
from app.auth.models import User

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get(
    "/me",
    response_model=schemas.AnalyticsListResponse
)
async def read_my_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await services.get_user_analytics(db, current_user)


@router.get(
    "/admin",
    response_model=schemas.AnalyticsListResponse
)
async def read_all_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_id == 2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    return await services.get_admin_analytics(db)
