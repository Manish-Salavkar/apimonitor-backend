from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, db_commit
from app.core.analytics_aggregator import aggregate_analytics

router = APIRouter(prefix="/admin/analytics", tags=["Admin Analytics"])


@router.post("/aggregate")
async def aggregate(db: AsyncSession = Depends(get_db)):
    await aggregate_analytics(db)
    return {"message": "Analytics aggregated successfully"}
