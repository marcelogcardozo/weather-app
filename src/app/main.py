import json
from datetime import date as dt
from datetime import timedelta as td
from typing import Annotated

from fastapi import FastAPI, Form, Request, Response
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.app.cache import RedisClient
from src.scraper import get_locations, get_weather_data

app = FastAPI(
    title='Weather API',
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
def home(request: Request) -> Response:
    df_locations = get_locations()

    start_date = dt.today()  # noqa: DTZ011
    final_date = start_date + td(days=15)

    return templates.TemplateResponse(
        'index.html',
        {
            'request': request,
            'title': 'Weather API',
            'locations': df_locations['location'].to_list(),
            'start_date': start_date.strftime('%Y-%m-%d'),
            'final_date': final_date.strftime('%Y-%m-%d'),
        },
    )


@app.post('/get_weather')
def get_weather(
    location: Annotated[str, Form()],
    start_date: Annotated[dt, Form()],
    final_date: Annotated[dt, Form()],
) -> dict:
    """Fetch weather data for a city with caching."""
    with RedisClient() as redis_client:
        cached_data = redis_client.get(f'weather:{location}')

        if cached_data:
            return JSONResponse(
                content={
                    'location': location,
                    'historical_data': json.loads(cached_data),
                },
            )

        weather_data = get_weather_data(
            location,
            start_date,
            final_date,
        ).to_dicts()

        redis_client.set(
            f'weather:{location}',
            json.dumps(weather_data),
            ex=60,
        )

        return JSONResponse(
            content={'location': location, 'historical_data': weather_data},
        )
