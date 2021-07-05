from typing import AsyncGenerator, AsyncIterator, Generator
import redis
from redis import Redis
import aioredis
from aioredis import Redis

from config.settings import settings
from utils.logger import getLogger

logger = getLogger(__name__)

pool = redis.ConnectionPool(host=settings.REDIS_SERVER, port=settings.REDIS_PORT, db=0)


def redis_session() -> Generator:
    connection = redis.Redis(connection_pool=pool)
    try:
        yield connection
    except Exception as e:
        logger.error(f"Error while connecting to redis {e}")
    finally:
        connection.close()


async def async_redis_session() -> AsyncIterator[Redis]:
    try:
        redis_db = aioredis.from_url(settings.AIOREDIS_URI, decode_responses=True)
        yield redis_db
    finally:
        await redis_db.close()
