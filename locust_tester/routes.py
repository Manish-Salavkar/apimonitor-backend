import subprocess
import asyncio
import os
import signal
import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.locust_tester.schemas import StressTestConfig

router = APIRouter(prefix="/stress", tags=["Stress Testing"])
LOCUST_FILE_PATH = "app/locust_tester/locustfile.py"

async def run_locust_process(config: StressTestConfig):
    # 1. Prepare Environment Variables
    env = os.environ.copy()
    env["TARGET_ENDPOINT"] = config.target_endpoint
    env["API_KEY"] = config.api_key  # <--- Pass Key to Subprocess

    cmd = [
        "locust",
        "-f", LOCUST_FILE_PATH,
        "--headless",
        "--host", config.target_host,
        "--users", str(config.num_users),
        "--spawn-rate", str(config.spawn_rate),
        "--run-time", f"{config.duration}s"
    ]

    process = None
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            env=env # <--- Inject the environment here
        )

        while True:
            line = await process.stdout.readline()
            if not line:
                break
            
            text = line.decode("utf-8").strip()
            if text:
                yield json.dumps({"log": text}) + "\n"

        await process.wait()
        yield json.dumps({"status": "completed"}) + "\n"

    except Exception as e:
        yield json.dumps({"error": str(e)}) + "\n"
        
    finally:
        if process and process.returncode is None:
            try:
                os.kill(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass

@router.post("/start")
async def start_stress_test(config: StressTestConfig):
    if not os.path.exists(LOCUST_FILE_PATH):
        raise HTTPException(status_code=500, detail="Locustfile not found")

    return StreamingResponse(
        run_locust_process(config),
        media_type="application/x-ndjson"
    )