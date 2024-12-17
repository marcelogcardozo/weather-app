import redis

from config import (
    REDIS_DB,
    REDIS_HOST,
    REDIS_PASSWORD,
    REDIS_PORT,
    REDIS_USERNAME,
)


def get_redis_client() -> redis.Redis:
    """Initialize Redis client."""
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        username=REDIS_USERNAME,
        password=REDIS_PASSWORD,
        db=REDIS_DB,
    )


redis_client = get_redis_client()


def get_cached_data(key: str) -> str:
    """Fetch data from Redis cache."""
    data = redis_client.get(key)
    if data:
        return data.decode('utf-8')
    return None


def set_cached_data(key: str, value: str, expiration: int = 43200) -> None:
    """Store data in Redis cache."""
    redis_client.set(key, value, ex=expiration)
