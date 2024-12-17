import json

from fastapi import FastAPI, Response

from src.app.cache import RedisClient

app = FastAPI(
    title='Weather API',
    description='Fetch weather data for a city',
    version='0.1.0',
)


@app.get('/')
def root() -> dict[str, str]:
    return {'message': 'Welcome to the Weather API'}


@app.get('/weather/{city}')
def get_weather(city: str) -> Response:
    """Fetch weather data for a city with caching."""
    with RedisClient() as redis_client:
        cached_data = redis_client.get(f'weather:{city}')

        if cached_data:
            return Response(
                json.loads(cached_data),
                media_type='application/json',
            )

        weather_data = json.dumps({'city': city, 'temperature': '72°F'})

        redis_client.set(f'weather:{city}', weather_data, ex=60)

        return Response(
            weather_data,
            media_type='application/json',
        )
