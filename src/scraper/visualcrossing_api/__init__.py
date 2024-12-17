from datetime import date as dt
from urllib.parse import quote

import polars as pl

from src.scraper.visualcrossing_api import config


def _get_weather_forecast(
    location: str,
    start_date: dt,
    end_date: dt,
) -> pl.DataFrame:
    url = config.TEMPLATE_URL_API.format(
        location=location,
        start_date=start_date,
        final_date=end_date,
        WEATHER_API_KEY=config.WEATHER_API_KEY,
    )

    return pl.read_csv(url)


def _get_icons_urls(icon: str) -> str:
    return config.ICON_URL.format(icon=icon)


def get_weather_data(
    location: str,
    start_date: dt,
    final_date: dt,
) -> pl.DataFrame:
    df_forecast = _get_weather_forecast(
        quote(location),
        start_date,
        final_date,
    )

    df_forecast = df_forecast.with_columns(
        pl.col('datetime')
        .str.to_datetime(strict=False)
        .dt.strftime('%d/%m/%Y')
        .alias('datetime'),
    )

    df_forecast = df_forecast.with_columns(
        pl.col('icon')
        .map_elements(_get_icons_urls, return_dtype=pl.Utf8)
        .alias('icon'),
    )

    return df_forecast.select(
        ['datetime', 'tempmin', 'temp', 'tempmax', 'description', 'icon'],
    )
