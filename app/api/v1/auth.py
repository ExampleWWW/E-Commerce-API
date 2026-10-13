from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database import get_async_session
from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserRead
from app.services.user import create_user, get_user_by_email

router = APIRouter(prefix="/auth", tags=["Auth 🔑"])


# ----- AUTH ENDPOINTS -----


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
)
async def register(user_in: UserCreate, session: AsyncSession = Depends(get_async_session)):
    user = await get_user_by_email(
        session, user_in.email
    )  # Проверяем, что пользователь с таким email не существует
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    new_user = await create_user(session, user_in)
    return new_user


@router.post("/login", response_model=dict, status_code=status.HTTP_200_OK, summary="Получение JWT токена")
async def login(user_in: UserLogin, session: AsyncSession = Depends(get_async_session)):
    user = await get_user_by_email(session, user_in.email)
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    access_token = create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserRead, summary="Получить профиль текущего пользователя")
async def get_current_profile(current_user: User = Depends(get_current_user)):
    return current_user  # Возвращаем данные текущего авторизованного пользователя
