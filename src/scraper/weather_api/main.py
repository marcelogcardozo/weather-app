from datetime import date as dt
from datetime import timedelta as td

import polars as pl
from requests import request

from src.scraper.weather_api import utils


def _get_days_of_weeks() -> tuple[list[dt], list[dt], list[dt]]:
    today = dt.today()  # noqa: DTZ011

    start_of_week = today - td(days=today.weekday())

    last_week = [
        (start_of_week - td(weeks=1) + td(days=i)).strftime('%Y-%m-%d')
        for i in range(7)
    ]

    current_week = [
        (start_of_week + td(days=i)).strftime('%Y-%m-%d') for i in range(7)
    ]

    next_week = [
        (start_of_week + td(weeks=1) + td(days=i)).strftime('%Y-%m-%d')
        for i in range(7)
    ]

    return last_week, current_week, next_week


def _get_weather_forecast(
    latitude: float,
    longitude: float,
) -> pl.DataFrame | None:
    url = utils.build_api_url(
        latitude,
        longitude,
    )

    r = request('GET', url, timeout=60)

    if not r.ok:
        return None
    return utils.mount_dataframe(r.json())


def get_weather_data(
    latitude: float,
    longitude: float,
) -> list[dict[str, str]] | None:
    if latitude is None or longitude is None:
        msg = 'Latitude and longitude are required'
        raise ValueError(msg)

    last_week, current_week, next_week = _get_days_of_weeks()

    df_forecast = _get_weather_forecast(
        latitude,
        longitude,
    )

    dfs_forecast_by_week = utils.separate_forecast_by_weeks(
        df_forecast,
        last_week,
        current_week,
        next_week,
    )

    return (
        [df_forecast.to_dicts() for df_forecast in dfs_forecast_by_week]
        if dfs_forecast_by_week is not None
        else None
    )
