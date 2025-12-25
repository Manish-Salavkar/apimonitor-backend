# app/auth/routes.py
from fastapi import APIRouter, Depends
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from app.auth.schemas import *
from app.auth.services import *
from pydantic import ValidationError

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post("/register")
async def create_user(user: CreateUser, db: AsyncSession = Depends(get_db)):
    result = await create_user_service(db, user)
    await db.commit()
    return result


@router.post("/login")
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    try:
        credentials = LoginInput(email=form_data.username, password=form_data.password)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="email is incorrect")
    result = await authenticate_user(db, credentials)
    await db.commit()
    return result


@router.post("/logout")
async def logout(
    data: BlacklistedTokenSubmit,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    print(data.model_dump())
    result = await blacklist_token_service(db, data)
    await db.commit()
    return result


# -----------------------------------------------------------------------------------------------

@router.get("/toggle-status")
async def toggle_user_status(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await toogle_user_status_service(db, user_id)
    await db.commit()
    return result



@router.get("/me", response_model=schemas.UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user