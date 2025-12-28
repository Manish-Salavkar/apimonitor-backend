import asyncio
import random
from fastapi import APIRouter, HTTPException

router = APIRouter(
    prefix="/internal",
    tags=["Internal APIs"]
)


# --------------------------------------------------
# 1️⃣ Fast health-check API (very low latency)
# --------------------------------------------------
@router.get("/ping")
async def ping():
    await asyncio.sleep(0.01)  # 10ms
    return {"status": "ok", "message": "pong"}


# --------------------------------------------------
# 2️⃣ Simulated DB read (IO-bound)
# --------------------------------------------------
@router.get("/users")
async def get_users():
    # simulate DB/network latency
    await asyncio.sleep(random.uniform(0.05, 0.15))  # 50–150ms

    return {
        "users": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
            {"id": 3, "name": "Charlie"},
        ]
    }


# --------------------------------------------------
# 3️⃣ Simulated async processing job
# --------------------------------------------------
@router.post("/process")
async def process_job():
    steps = random.randint(3, 6)

    for _ in range(steps):
        # simulate async work chunks
        await asyncio.sleep(0.05)

    return {
        "status": "completed",
        "steps": steps
    }


# --------------------------------------------------
# 4️⃣ Flaky API (errors + latency variance)
# --------------------------------------------------
@router.get("/flaky")
async def flaky_api():
    await asyncio.sleep(random.uniform(0.02, 0.2))

    # 30% chance of failure
    if random.random() < 0.3:
        raise HTTPException(
            status_code=500,
            detail="Simulated internal error"
        )

    return {"status": "success"}
