import json

import plotly.graph_objs as go
import plotly.utils as p_utils
import polars as pl

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


def get_graph_json_by_dict(weather_data: dict) -> str:
    if weather_data is None:
        return None

    df_weather_data = pl.DataFrame(data=weather_data)

    df_weather_data = df_weather_data.with_columns(
        pl.col('date').str.to_date('%d/%m/%Y').alias('date'),
        pl.col('tempmin').cast(pl.Float32),
        pl.col('temp').cast(pl.Float32),
        pl.col('tempmax').cast(pl.Float32),
    )

    # Criar múltiplos objetos Scatter para cada série
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

    return json.dumps(fig, cls=p_utils.PlotlyJSONEncoder)
