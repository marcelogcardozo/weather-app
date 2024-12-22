from datetime import date as dt
from datetime import timedelta as td
from urllib.parse import quote

import polars as pl

from src.scraper.visualcrossing_api import config


def _get_weather_forecast(
    location: str,
    start_date: dt,
    end_date: dt,
) -> pl.DataFrame:
    url = config.build_api_url(
        location,
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d'),
    )
    return pl.read_csv(url)


def get_weather_data(
    location: str,
    start_date: dt | None = None,
    final_date: dt | None = None,
) -> list[dict[str, str]]:
    if not start_date:
        start_date = dt.today()  # noqa: DTZ011

    if not final_date:
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
        .map_elements(config.build_icon_tag, return_dtype=pl.Utf8)
        .alias('icon'),
    )

    return df_forecast.select(
        ['date', 'tempmin', 'temp', 'tempmax', 'description', 'icon'],
    ).to_dicts()
