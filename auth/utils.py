from argon2 import PasswordHasher, exceptions as argon2_exceptions
from fastapi import HTTPException, status
from datetime import datetime, timedelta
import datetime as DATETIME
from jose import JWTError, jwt
from app.config import settings


ph = PasswordHasher()

async def hash_password(password: str) -> str:
    """
    Hashes the plain password with Argon2-Cffi
    """
    return ph.hash(password)


async def verify_password(hashed_password: str, plain_password: str) -> bool:
    """
    Verifies the plain password against the hashed password.
    Raises HTTPException if verification fails.
    """
    try:
        return ph.verify(hashed_password, plain_password)
    except argon2_exceptions.VerifyMismatchError:
        return False
    except Exception as e:
        print(f"Error verifying password: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Password verification failed")


async def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(DATETIME.timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.TOKENALGORITHM)
