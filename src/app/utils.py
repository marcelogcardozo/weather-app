import json

import plotly.graph_objs as go
import polars as pl
from plotly.utils import PlotlyJSONEncoder
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


def get_graph_json_by_dict(
    weather_data: list[dict[str, str]] | None,
) -> str | None:
    if weather_data is None:
        return None

    df_weather_data = pl.DataFrame(data=weather_data)

    df_weather_data = df_weather_data.with_columns(
        pl.col('date').str.to_date('%d/%m/%Y').alias('date'),
        pl.col('tempmin').cast(pl.Float32),
        pl.col('temp').cast(pl.Float32),
        pl.col('tempmax').cast(pl.Float32),
    )

    data = [
        go.Scatter(
            x=df_weather_data['date'].to_list(),
            y=df_weather_data['tempmin'].to_list(),
            mode='lines+markers',
            name='Min. Temperature',
        ),
        go.Scatter(
            x=df_weather_data['date'].to_list(),
            y=df_weather_data['temp'].to_list(),
            mode='lines+markers',
            name='Avg. Temperature',
        ),
        go.Scatter(
            x=df_weather_data['date'].to_list(),
            y=df_weather_data['tempmax'].to_list(),
            mode='lines+markers',
            name='Máx. Temperature',
        ),
    ]

    layout = go.Layout(
        title='Temperature Data per Day',
        xaxis={'title': 'Date'},
        yaxis={'title': 'Temperature (°C)'},
        legend={'title': 'Legend'},
        paper_bgcolor='rgba(0,0,0,0)',
    )

    fig = go.Figure(data=data, layout=layout)

    return json.dumps(fig, cls=PlotlyJSONEncoder)
