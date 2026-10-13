from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate


async def get_user_by_email(session: AsyncSession, email: str):
    statement = select(User).where(User.email == email)

    result = await session.exec(statement)
    return result.first()


async def create_user(session: AsyncSession, user_create: UserCreate):
    hash = hash_password(user_create.password)

    user = User(email=user_create.email, hashed_password=hash)
    session.add(user)

    await session.commit()
    await session.refresh(user)

    return user
