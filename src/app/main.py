import json
from datetime import date as dt
from datetime import timedelta as td
from typing import Annotated

from fastapi import FastAPI, Form, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.app.utils import (
    cache_has_key,
    get_cached_data,
    get_graph_json_by_dict,
    set_data_in_cache,
)
from src.scraper import get_locations, get_weather_data

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


@app.get('/')
def home(request: Request, cache_key: str = '') -> Response:
    df_locations = get_locations()

    start_date = dt.today()  # noqa: DTZ011
    final_date = start_date + td(days=14)

    weather_data = get_cached_data(cache_key)
    graph_json = get_graph_json_by_dict(weather_data)

    return templates.TemplateResponse(
        'index.html',
        {
            'request': request,
            'title': 'Weather API',
            'locations': df_locations['location'].to_list(),
            'start_date': start_date.strftime('%Y-%m-%d'),
            'final_date': final_date.strftime('%Y-%m-%d'),
            'weather_data': weather_data,
            'location': cache_key.split(';')[0],
            'graph_json': graph_json,
        },
    )


@app.post('/get_weather')
def get_weather(
    location: Annotated[str, Form()],
    start_date: Annotated[dt, Form()],
    final_date: Annotated[dt, Form()],
) -> RedirectResponse:
    """Fetch weather data for a city with caching."""

    cache_key = f'{location};{start_date};{final_date}'

    if cache_has_key(cache_key):
        return RedirectResponse(
            url='/',
            status_code=303,
            headers={'cache-key': cache_key},
        )

    weather_data = get_weather_data(
        location,
        start_date,
        final_date,
    )

    set_data_in_cache(cache_key, json.dumps(weather_data), 60)

    return RedirectResponse(
        url=f'/?cache_key={cache_key}',
        status_code=303,
    )
