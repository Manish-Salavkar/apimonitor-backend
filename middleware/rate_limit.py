# app/middleware/rate_limit.py

import time
from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.database import SessionLocal
from app.api import models
from app.core.rate_limiter import check_rate_limit
from app.core.usage_logger import log_usage
from app.core.analytics_counter import increment_request_counters


async def rate_limit_middleware(request: Request, call_next):
    # Only protect internal APIs
    if not request.url.path.startswith("/internal"):
        return await call_next(request)

    # =========================================================
    # 🛑 BYPASS LOGIC FOR STRESS TESTING
    # =========================================================
    # If this header is present, we skip ALL tracking (DB, Redis, Limits)
    # This keeps the stress test "pure" and prevents polluting prod data.
    if request.headers.get("X-STRESS-TEST") == "true":
        return await call_next(request)
    # =========================================================

    api_key_value = request.headers.get("X-API-KEY")
    if not api_key_value:
        return JSONResponse(
            status_code=401,
            content={"detail": "API key missing"}
        )

    start_time = time.perf_counter()

    async with SessionLocal() as db:
        # ... (Rest of your existing logic: DB fetch, Rate Limit, etc.)
        result = await db.execute(
            select(models.APIKey)
            .options(
                selectinload(models.APIKey.api),
                selectinload(models.APIKey.tier)
                    .selectinload(models.Tier.rate_limit_rules)
            )
            .where(
                models.APIKey.key_value == api_key_value,
                models.APIKey.enabled == True
            )
        )
        api_key = result.scalar_one_or_none()

        if not api_key:
            return JSONResponse(status_code=401, content={"detail": "Invalid API key"})

        if not api_key.api.enabled:
            return JSONResponse(status_code=403, content={"detail": "API is disabled"})

        rate_limit = api_key.tier.rate_limit_rules.requests_per_minute

        # Rate limit check
        try:
            await check_rate_limit(api_key=api_key_value, limit=rate_limit)
        except Exception:
            await increment_request_counters(
                api_id=api_key.api_id,
                api_key_id=api_key.id,
                status_code=429,
                response_time_ms=0,
                rate_limited=True
            )
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})

        # Forward request
        response = await call_next(request)

        end_time = time.perf_counter()
        response_time_ms = int((end_time - start_time) * 1000)

        # Redis analytics
        await increment_request_counters(
            api_id=api_key.api_id,
            api_key_id=api_key.id,
            status_code=response.status_code,
            response_time_ms=response_time_ms
        )

        # MySQL usage log
        await log_usage(
            db=db,
            api_id=api_key.api_id,
            api_key_id=api_key.id,
            user_id=api_key.user_id,
            endpoint=str(request.url.path),
            method=request.method,
            status_code=response.status_code,
            response_time_ms=response_time_ms
        )

        await db.commit()

        return response