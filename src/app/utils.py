import json

from src.app.cache import RedisClient


def cache_has_key(key: str) -> bool:
    with RedisClient() as redis_client:
        return redis_client.exists(key)


def get_cached_data(key: str | None) -> str | None:
    with RedisClient() as redis_client:
        cached_data = redis_client.get(key)
        if cached_data:
            return json.loads(cached_data)
    return None


def set_data_in_cache(key: str, data: str, ex: int) -> None:
    with RedisClient() as redis_client:
        redis_client.set(key, data, ex=ex)
