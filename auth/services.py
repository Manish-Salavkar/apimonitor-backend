from app.auth import models
from app.auth import schemas
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from app.auth.models import User
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from datetime import datetime, timezone
from app.config import settings
from jose import JWTError, jwt
from app.auth import utils

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        db_blacklisted_token = (await db.execute(select(models.BlacklistedTokens).where(models.BlacklistedTokens.token == token))).scalar_one_or_none()
        if db_blacklisted_token:
            raise credentials_exception
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.TOKENALGORITHM])
        # print("JWT payload:", payload)
        id: str = payload.get("sub")
        if not id:
            raise credentials_exception
    except JWTError as e:
        print("JWT decode error:", e)
        raise credentials_exception

    user = (await db.execute(select(User).where(User.id == id))).scalar_one_or_none()

    if not user or user.is_active == 0:
        print("User not found")
        raise credentials_exception
    return user

# -------------------------------------------------------------------------------------------------------------

async def authenticate_user(db: AsyncSession, credentials: schemas.LoginInput):
    user = (await db.execute(select(User).where(User.email == credentials.email))).scalar_one_or_none()

    if not user or not await utils.verify_password(user.password, credentials.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    token = await utils.create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


async def blacklist_token_service(db: AsyncSession, data: schemas.BlacklistedTokenSubmit):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        print(data.token, data.reason)
        payload = jwt.decode(data.token, settings.SECRET_KEY, algorithms=[settings.TOKENALGORITHM])
        id: str = payload.get("sub")
        exp_timestamp: int = payload.get("exp")
        if not id or not exp_timestamp:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = (await db.execute(select(User).where(User.id == id))).scalar_one_or_none()
    if not user:
        raise credentials_exception
    
    expires_at = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)

    db_blacklisted_token = models.BlacklistedTokens(
        token = data.token,
        expires_at = expires_at,
        reason = data.reason,
        user_id = user.id
    )

    db.add(db_blacklisted_token)
    await db.flush()

    return {"status": 1}

# def get_admin_user(current_user: User = Depends(get_current_user)):
#     if not current_user.is_admin:
#         raise HTTPException(status_code=403, detail="Admins only")
#     return current_user


# -----------------------------------------------------------------------------------------------------------------

async def create_user_service(db: AsyncSession, user: schemas.CreateUser):
    try:
        hashed_password = await utils.hash_password(user.password)
        user.password = hashed_password
        # role_id = 2

        db_user = User(
            username=user.username,
            email=user.email,
            password=hashed_password,
            role_id=2,
        )

        db.add(db_user)
        await db.flush()
        await db.refresh(db_user)
        return {"data": schemas.UserOut.model_validate(db_user).model_dump(), "message": "User created successfully"}, status.HTTP_201_CREATED
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create user")


async def toogle_user_status_service(db: AsyncSession, user_id: int):
    try:
        db_user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        db_user.status = not db_user.status

        await db.flush()
        await db.refresh(db_user)
        return {"data": schemas.UserOut.model_validate(db_user).model_dump(), "message": "User status toggled successfully"}, status.HTTP_200_OK

    except HTTPException as http_exec:
        raise http_exec

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to toggle user status"
        )