import time
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import models


async def log_usage(
    db: AsyncSession,
    *,
    api_id: str,
    api_key_id: str,
    user_id: int,
    endpoint: str,
    method: str,
    status_code: int,
    response_time_ms: int
):
    log = models.UsageLog(
        api_id=api_id,
        api_key_id=api_key_id,
        user_id=user_id,
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        response_time_ms=response_time_ms
    )

    db.add(log)
