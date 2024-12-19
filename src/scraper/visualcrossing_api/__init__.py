from datetime import date as dt
from datetime import timedelta as td
from urllib.parse import quote

import polars as pl

from config import WEATHER_API_KEY
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
        WEATHER_API_KEY=WEATHER_API_KEY,
    )

    return pl.read_csv(url)


def _get_icons_urls(icon: str) -> str:
    return config.TEMPLATE_ICON_TAG.format(icon=icon)


def get_weather_data(
    location: str,
    start_date: dt | None = None,
    final_date: dt | None = None,
) -> list[dict]:
    if start_date is None:
        start_date = dt.today()  # noqa: DTZ011
        final_date = start_date + td(days=15)

    df_forecast = _get_weather_forecast(
        quote(location),
        start_date,
        final_date,
    )

    df_forecast = df_forecast.with_columns(
        pl.col('datetime')
        .str.to_datetime(strict=False)
        .dt.strftime('%d/%m/%Y')
        .alias('date'),
    )

    df_forecast = df_forecast.with_columns(
        pl.col('icon')
        .map_elements(_get_icons_urls, return_dtype=pl.Utf8)
        .alias('icon'),
    )

    return df_forecast.select(
        ['date', 'tempmin', 'temp', 'tempmax', 'description', 'icon'],
    ).to_dicts()
