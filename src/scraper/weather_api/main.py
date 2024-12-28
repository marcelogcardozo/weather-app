from datetime import date as dt
from datetime import timedelta as td

import polars as pl
from requests import request

from src.scraper.weather_api import utils


def _get_weather_forecast(
    latitude: float,
    longitude: float,
    start_date: dt,
    end_date: dt,
) -> pl.DataFrame | None:
    url = utils.build_api_url(
        latitude,
        longitude,
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d'),
    )

    r = request('GET', url, timeout=60)

    if not r.ok:
        return None
    return utils.mount_dataframe(r.json())


def get_weather_data(
    latitude: float,
    longitude: float,
    start_date: dt | None = None,
    final_date: dt | None = None,
) -> list[dict[str, str]] | None:
    if latitude is None or longitude is None:
        msg = 'Latitude and longitude are required'
        raise ValueError(msg)

    if not start_date:
        start_date = dt.today()  # noqa: DTZ011

    if not final_date:
        final_date = start_date + td(days=15)

    df_forecast = _get_weather_forecast(
        latitude,
        longitude,
        start_date,
        final_date,
    )

    return df_forecast.to_dicts() if df_forecast is not None else None
