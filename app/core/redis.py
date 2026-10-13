from collections.abc import AsyncGenerator

from redis.asyncio import Redis

from app.core.config import settings

redis = Redis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}", decode_responses=True)


async def get_redis() -> AsyncGenerator[Redis, None]:
    yield redis
