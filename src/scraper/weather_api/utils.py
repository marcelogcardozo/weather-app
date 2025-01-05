from datetime import datetime as dt
from urllib.parse import urlencode, urljoin

import polars as pl

from src.scraper.weather_api.config import BASE_API_URL


def build_api_url(
    latitude: float,
    longitude: float,
) -> str:
    params = {
        'latitude': latitude,
        'longitude': longitude,
        'hourly': ['temperature_2m', 'relative_humidity_2m'],
        'daily': [
            'temperature_2m_max',
            'temperature_2m_min',
            'sunrise',
            'sunset',
            'uv_index_max',
        ],
        'timezone': 'America/Sao_Paulo',
        'past_days': 14,
        'forecast_days': 14,
    }

    params_tratados = {}

    for param, value in params.items():
        if isinstance(value, list):
            params_tratados[param] = ','.join(value)
            continue
        params_tratados[param] = value

    query_string = urlencode(params_tratados, safe=',')

    return urljoin(BASE_API_URL, f'?{query_string}')


def _mount_hourly_dataframe_grouped_by_day(
    data: dict[str, list[float]],
) -> pl.DataFrame:
    hourly_df: pl.DataFrame = pl.DataFrame(
        data,
    )
    hourly_df = hourly_df.rename(
        {
            'time': 'date',
            'temperature_2m': 'temperature',
            'relative_humidity_2m': 'relative_humidity',
        },
    )

    hourly_df = hourly_df.with_columns(
        pl.col('date')
        .str.to_datetime(strict=False)
        .dt.strftime('%Y-%m-%d')
        .alias('date'),
    )

    grouped_df = hourly_df.group_by('date').agg(
        [
            pl.col(c).mean().round(1).alias(c)
            for c in hourly_df.columns
            if c != 'date'
        ],
    )

    grouped_df = grouped_df.with_columns(
        pl.col('date').str.to_datetime(strict=False).alias('date'),
    )

    return grouped_df.sort('date')


def _mount_daily_dataframe(data: dict[str, list[float]]) -> pl.DataFrame:
    daily_df = pl.DataFrame(data)

    daily_df = daily_df.rename(
        {
            'time': 'date',
            'temperature_2m_max': 'max_temperature',
            'temperature_2m_min': 'min_temperature',
        },
    )

    return daily_df.with_columns(
        pl.col('date').str.to_datetime(strict=False).alias('date'),
    )


def mount_dataframe(data: dict) -> pl.DataFrame:
    df_daily_average = _mount_hourly_dataframe_grouped_by_day(
        {key: data['hourly'][key] for key in data['hourly']},
    )

    df_daily = _mount_daily_dataframe(
        {key: data['daily'][key] for key in data['daily']},
    )

    df_weather_data_by_day = df_daily_average.join(df_daily, on='date')

    df_weather_data_by_day = df_weather_data_by_day.with_columns(
        pl.col('date').dt.strftime('%a').alias('day_of_week'),
        pl.col('date').dt.strftime('%A').alias('day_of_week_full'),
    )

    df_weather_data_by_day = df_weather_data_by_day.with_columns(
        pl.col('date').dt.strftime('%Y-%m-%d').alias('date'),
    )

    return df_weather_data_by_day.select(
        [
            'date',
            'day_of_week',
            'day_of_week_full',
            'temperature',
            'min_temperature',
            'max_temperature',
            'relative_humidity',
            'sunrise',
            'sunset',
            'uv_index_max',
        ],
    )


def separate_forecast_by_weeks(
    df: pl.DataFrame,
    last_week: list[dt],
    current_week: list[dt],
    next_week: list[dt],
) -> list[pl.DataFrame]:
    last_week_df = df.filter(pl.col('date').is_in(last_week))
    current_week_df = df.filter(pl.col('date').is_in(current_week))
    next_week_df = df.filter(pl.col('date').is_in(next_week))

    return [last_week_df, current_week_df, next_week_df]
