# app/core/rate_limiter.py
from fastapi import HTTPException, status
from app.core.redis import redis_client


async def check_rate_limit(
    api_key: str,
    limit: int,
    window_seconds: int = 60
):
    """
    Simple fixed-window rate limiter
    """
    redis_key = f"rate_limit:{api_key}"

    current_count = await redis_client.incr(redis_key)

    if current_count == 1:
        await redis_client.expire(redis_key, window_seconds)

    if current_count > limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
