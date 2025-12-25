from fastapi import FastAPI, Depends
from app.database import get_db, Base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.auth.routes import router as auth_router
from app.api.routes import api_router
from app.api.routes import key_router
from app.api.routes import tier_router
from app.middleware.rate_limit import rate_limit_middleware
from fastapi.middleware.cors import CORSMiddleware
from app.admin.routes import router as admin_router

app = FastAPI(
    root_path="/"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(api_router)
app.include_router(key_router)
app.include_router(tier_router)
app.include_router(admin_router)


app.middleware("http")(rate_limit_middleware)


@app.get("/")
async def check_health(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT id FROM health LIMIT 1"))
        return {"status": "Healthy"}
    except Exception as e:
        print(e)
        return {"status": "Unhealthy"}