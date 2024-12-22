import json

from src.app.cache import RedisClient


def cache_has_key(key: str) -> bool:
    with RedisClient() as redis_client:
        return bool(redis_client.exists(key))


def get_cached_data(key: str | None) -> list[dict[str, str]] | None:
    if key is None:
        return None

    with RedisClient() as redis_client:
        cached_data = redis_client.get(key)
        if cached_data:
            data = json.loads(cached_data)
            if isinstance(data, list):
                return data

    return None


def set_data_in_cache(key: str, data: str, ex: int) -> None:
    with RedisClient() as redis_client:
        redis_client.set(key, data, ex=ex)
