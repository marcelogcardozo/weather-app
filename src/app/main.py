from cache import get_cached_data, set_cached_data
from fastapi import FastAPI

app = FastAPI(
    title='Weather API',
    description='Fetch weather data for a city',
    version='0.1.0',
)


# Routes
@app.get('/')
def root() -> dict[str, str]:
    return {'message': 'Welcome to the Weather API'}


@app.get('/weather/{city}')
def get_weather(city: str) -> dict[str, str]:
    """Fetch weather data for a city with caching."""
    # Check if data is in cache
    cached_data = get_cached_data(city)
    if cached_data:
        return {'source': 'cache', 'data': cached_data}

    # Fetch data from 3rd party API
    weather_data = {'city': city, 'temperature': '72°F'}

    # Cache the data
    set_cached_data(city, str(weather_data))

    return {'source': 'api', 'data': weather_data}
