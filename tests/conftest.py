from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.core.database import get_async_session
from app.core.redis import get_redis
from app.main import app

# 1. URL базы данных (для локального прогона с ПК меняем хост db -> 127.0.0.1)
db_url = (
    settings.DATABASE_URL.replace("@db:", "@127.0.0.1:")
    if "@db:" in settings.DATABASE_URL
    else settings.DATABASE_URL
)


# 2. Подготовка схемы таблиц (создаём и очищаем перед каждым тестом)
@pytest_asyncio.fixture(scope="function", autouse=True)
async def prepare_database():
    """Пересоздаёт таблицы в чистом цикле событий каждого теста."""
    engine = create_async_engine(db_url, echo=False, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
    await engine.dispose()

    yield

    engine = create_async_engine(db_url, echo=False, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    await engine.dispose()


# 3. Асинхронный движок для конкретного теста
@pytest_asyncio.fixture(scope="function")
async def async_engine():
    engine = create_async_engine(db_url, echo=False, poolclass=NullPool)
    yield engine
    await engine.dispose()


# 4. Изолированная сессия БД под текущий тест
@pytest_asyncio.fixture(scope="function")
async def db_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
    )
    async with session_factory() as session:
        yield session


# 5. Клиент Redis с автоочисткой
@pytest_asyncio.fixture(scope="function")
async def redis_client() -> AsyncGenerator[Redis, None]:
    redis_host = "127.0.0.1" if settings.REDIS_HOST == "redis" else settings.REDIS_HOST

    client = Redis.from_url(f"redis://{redis_host}:{settings.REDIS_PORT}", decode_responses=True)
    yield client
    try:
        await client.flushdb()
    except Exception:
        pass
    await client.aclose()


# 6. HTTP-клиент (httpx.AsyncClient) с подменой зависимостей FastAPI
@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession, redis_client: Redis) -> AsyncGenerator[AsyncClient, None]:
    async def _get_test_db():
        yield db_session

    async def _get_test_redis():
        yield redis_client

    app.dependency_overrides[get_async_session] = _get_test_db
    app.dependency_overrides[get_redis] = _get_test_redis

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
