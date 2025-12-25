from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis import redis_client
from app.api import models


def parse_window(window: str):
    """
    YYYYMMDDHHMM → datetime
    """
    start = datetime.strptime(window, "%Y%m%d%H%M")
    end = start + timedelta(minutes=1)
    return start, end


async def aggregate_analytics(db: AsyncSession):
    """
    Pull analytics counters from Redis and persist to MySQL
    """
    keys = await redis_client.keys("analytics:*")

    for key in keys:
        # analytics:{api_id}:{api_key_id}:{window}
        parts = key.split(":")
        if len(parts) != 4:
            continue

        _, api_id, api_key_id, window = parts

        data = await redis_client.hgetall(key)
        if not data:
            continue

        window_start, window_end = parse_window(window)

        request_count = int(data.get("requests", 0))
        success_count = int(data.get("success", 0))
        error_count = int(data.get("errors", 0))
        rate_limit_exceeded = int(data.get("rate_limit_exceeded", 0))
        total_latency = int(data.get("total_latency_ms", 0))
        max_latency = int(data.get("max_latency_ms", 0))

        avg_latency = (
            int(total_latency / request_count)
            if request_count > 0 else 0
        )

        summary = models.AnalyticsSummary(
            api_id=api_id,
            api_key_id=api_key_id,
            window_start=window_start,
            window_end=window_end,
            request_count=request_count,
            success_count=success_count,
            error_count=error_count,
            rate_limit_exceeded_count=rate_limit_exceeded,
            avg_response_time_ms=avg_latency,
            max_response_time_ms=max_latency
        )

        db.add(summary)

        # Remove Redis key after aggregation
        await redis_client.delete(key)

    await db.commit()
