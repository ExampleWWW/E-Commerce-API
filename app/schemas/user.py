from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


class UserCreate(BaseModel):  # Схема для регистраций
    email: EmailStr
    password: str = Field(min_length=8)


class UserLogin(BaseModel):  # Схема для входа
    email: EmailStr
    password: str


class UserRead(BaseModel):  # Схема ответа
    id: int
    email: EmailStr
    role: UserRole
    is_active: bool
