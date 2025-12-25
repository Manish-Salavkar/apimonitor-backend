from datetime import datetime
from app.core.redis import redis_client


def get_time_window():
    return datetime.utcnow().strftime("%Y%m%d%H%M")


async def increment_request_counters(
    *,
    api_id: str,
    api_key_id: str,
    status_code: int,
    response_time_ms: int,
    rate_limited: bool = False
):
    window = get_time_window()
    redis_key = f"analytics:{api_id}:{api_key_id}:{window}"

    pipe = redis_client.pipeline()

    # total requests
    pipe.hincrby(redis_key, "requests", 1)

    # success / error
    if status_code >= 400:
        pipe.hincrby(redis_key, "errors", 1)
    else:
        pipe.hincrby(redis_key, "success", 1)

    # rate limit hits
    if rate_limited:
        pipe.hincrby(redis_key, "rate_limit_exceeded", 1)

    # latency stats
    pipe.hincrby(redis_key, "total_latency_ms", response_time_ms)

    # max latency (manual compare)  
    current_max = await redis_client.hget(redis_key, "max_latency_ms")
    if not current_max or response_time_ms > int(current_max):
        pipe.hset(redis_key, "max_latency_ms", response_time_ms)

    # TTL (5 minutes)
    pipe.expire(redis_key, 300)

    await pipe.execute()
