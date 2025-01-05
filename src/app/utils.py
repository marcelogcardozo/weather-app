import json

import polars as pl
from redis.exceptions import ConnectionError as RedisConnectionError

from src.app.cache import RedisClient
from src.scraper.locations_api import get_locations


def get_cache_health() -> bool:
    with RedisClient() as redis_client:
        try:
            redis_client.ping()
        except RedisConnectionError:
            return False
        else:
            return True


def get_locations_and_save_in_cache() -> pl.DataFrame:
    if not cache_has_key('locations'):
        df_locations = get_locations()
        set_data_in_cache(
            'locations',
            json.dumps(df_locations.to_dicts()),
            ex=None,
        )
    else:
        locations_dict = get_cached_data('locations')
        df_locations = pl.DataFrame(locations_dict)

    return df_locations


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
