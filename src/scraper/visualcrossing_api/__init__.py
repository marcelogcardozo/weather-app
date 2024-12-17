from datetime import date as dt
from urllib.parse import quote

import polars as pl

import src.scraper.visualcrossing_api.config as cfg


def _get_weather_forecast(
    location: str, start_date: str, end_date: str
) -> pl.DataFrame:
    url = cfg.TEMPLATE_URL_API.format(
        location=location,
        start_date=start_date,
        final_date=end_date,
        API_KEY=cfg.API_KEY,
    )

    return pl.read_csv(url)


def _get_icons_urls(icon: str):
    return cfg.ICON_URL.format(icon=icon)


def get_weather_data(location: str, start_date: dt, final_date: dt) -> pl.DataFrame:
    df_forecast = _get_weather_forecast(quote(location), start_date, final_date)

    df_forecast = df_forecast.with_columns(
        pl.col("datetime")
        .str.to_datetime(strict=False)
        .dt.strftime("%d/%m/%Y")
        .alias("datetime")
    )

    df_forecast = df_forecast.with_columns(
        pl.col("icon").map_elements(_get_icons_urls, return_dtype=pl.Utf8).alias("icon")
    )

    return df_forecast.select(
        ["datetime", "tempmin", "temp", "tempmax", "description", "icon"]
    )
