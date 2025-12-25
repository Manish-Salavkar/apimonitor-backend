from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    TOKENALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    DEBUG: bool
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_URL: str


    class Config:
        env_file = ".env"

settings = Settings()