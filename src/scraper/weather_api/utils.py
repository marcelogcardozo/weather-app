from urllib.parse import urlencode, urljoin

import polars as pl

from src.scraper.weather_api.config import BASE_API_URL


def build_api_url(
    latitude: float,
    longitude: float,
    start_date: str,
    final_date: str,
) -> str:
    params = {
        'latitude': latitude,
        'longitude': longitude,
        'start_date': start_date,
        'end_date': final_date,
        'hourly': ['temperature_2m', 'apparent_temperature'],
        'daily': [
            'temperature_2m_max',
            'temperature_2m_min',
            'apparent_temperature_max',
            'apparent_temperature_min',
        ],
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
            'temperature_2m': 'temp',
            'apparent_temperature': 'apparent_temp',
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
            'temperature_2m_max': 'tempmax',
            'temperature_2m_min': 'tempmin',
            'apparent_temperature_max': 'apparent_tempmax',
            'apparent_temperature_min': 'apparent_tempmin',
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
        pl.col('date').dt.strftime('%d/%m/%Y').alias('date'),
    )

    return df_weather_data_by_day.select(
        [
            'date',
            'tempmin',
            'temp',
            'tempmax',
            'apparent_tempmin',
            'apparent_temp',
            'apparent_tempmax',
        ],
    )
