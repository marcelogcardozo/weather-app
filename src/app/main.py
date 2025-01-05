import json
from datetime import datetime as dt
from typing import Annotated

import polars as pl
from fastapi import FastAPI, Form, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.app.utils import (
    cache_has_key,
    get_cache_health,
    get_cached_data,
    get_locations_and_save_in_cache,
    set_data_in_cache,
)
from src.scraper.weather_api import get_weather_data

app = FastAPI(
    title='Weather APP',
    description='Fetch weather data for a city',
    version='0.1.0',
)

templates = Jinja2Templates(directory='src/frontend/templates')
app.mount(
    '/static',
    StaticFiles(directory='src/frontend/static'),
    name='static',
)


@app.get('/', include_in_schema=False)
def home(request: Request, cache_key: str = '') -> Response:
    redis_is_ok = get_cache_health()

    if not redis_is_ok:
        return Response(
            content='Redis is not available',
            status_code=503,
        )

    df_locations = get_locations_and_save_in_cache()

    weather_data = get_cached_data(cache_key)

    return templates.TemplateResponse(
        'index.html',
        {
            'request': request,
            'title': 'Weather APP',
            'locations': df_locations['location'].to_list(),
            'location': cache_key.split(';')[0],
            'unity': '°C',
            'last_week': weather_data[0] if weather_data else [],
            'current_week': weather_data[1] if weather_data else [],
            'next_week': weather_data[2] if weather_data else [],
            'now': dt.today(),  # noqa: DTZ002
            'today': next(
                (
                    item
                    for item in weather_data[1]
                    if item['date'] == dt.today().strftime('%Y-%m-%d')  # noqa: DTZ002
                ),
                None,
            )
            if weather_data
            else {},
        },
    )


@app.get('/get_locations')
def get_locations() -> JSONResponse:
    """Get locations."""

    locations = get_locations_and_save_in_cache()

    return JSONResponse(
        locations['location'].to_list(),
    )


@app.post('/get_weather')
def get_weather(
    location: Annotated[str, Form()],
) -> RedirectResponse:
    """Fetch weather data for a city with caching."""

    cache_key = f'{location}'

    if cache_has_key(cache_key):
        return RedirectResponse(
            url='/',
            status_code=303,
            headers={'cache-key': cache_key},
        )

    df_locations = get_locations_and_save_in_cache()

    df_location = df_locations.filter(pl.col('location') == location)

    latitude = df_location['latitude'][0]
    longitude = df_location['longitude'][0]

    weather_data = get_weather_data(
        latitude,
        longitude,
    )

    set_data_in_cache(cache_key, json.dumps(weather_data), 60)

    return RedirectResponse(
        url=f'/?cache_key={cache_key}',
        status_code=303,
    )
