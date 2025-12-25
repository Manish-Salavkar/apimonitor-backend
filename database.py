# app/database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.config import settings


engine = create_async_engine(settings.DATABASE_URL, connect_args={"ssl": False})

SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

async def db_commit(session: AsyncSession):
    try:
        print(settings.DEBUG)
        await session.commit()
        print("Database commit successful")
        # if settings.DEBUG:
        #     print("Database rollback successful")
        #     await session.rollback()
    except Exception as e:
        await session.rollback()
        raise e



async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()