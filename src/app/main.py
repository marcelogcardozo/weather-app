import json
from datetime import date as dt
from datetime import timedelta as td
from typing import Annotated

import polars as pl
from fastapi import FastAPI, Form, HTTPException, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.app.utils import (
    cache_has_key,
    get_cached_data,
    get_graph_json_by_dict,
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
    df_locations = get_locations_and_save_in_cache()

    final_date = dt.today()  # noqa: DTZ011
    start_date = final_date - td(days=30)

    weather_data = get_cached_data(cache_key)
    graph_json = get_graph_json_by_dict(weather_data)

    return templates.TemplateResponse(
        'index.html',
        {
            'request': request,
            'title': 'Weather APP',
            'locations': df_locations['location'].to_list(),
            'start_date': start_date.strftime('%Y-%m-%d'),
            'final_date': final_date.strftime('%Y-%m-%d'),
            'weather_data': weather_data,
            'location': cache_key.split(';')[0],
            'graph_json': graph_json,
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
    start_date: Annotated[dt, Form()],
    final_date: Annotated[dt, Form()],
) -> RedirectResponse:
    """Fetch weather data for a city with caching."""

    if start_date > final_date:
        raise HTTPException(
            status_code=400,
            detail='Start date must be before final date',
        )

    if final_date > dt.today():  # noqa: DTZ011
        raise HTTPException(
            status_code=400,
            detail='Final date must be before today',
        )

    cache_key = f'{location};{start_date};{final_date}'

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
        start_date,
        final_date,
    )

    set_data_in_cache(cache_key, json.dumps(weather_data), 60)

    return RedirectResponse(
        url=f'/?cache_key={cache_key}',
        status_code=303,
    )
