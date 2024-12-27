from urllib.parse import urlencode

from config import WEATHER_API_KEY

BASE_API_URL = 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline'
BASE_ICON_URL = 'https://raw.githubusercontent.com/visualcrossing/WeatherIcons/main/SVG/1st%20Set%20-%20Color'


def build_api_url(
    location: str,
    start_date: str,
    final_date: str,
) -> str:
    query_params = {
        'key': WEATHER_API_KEY,
        'unitGroup': 'metric',
        'include': 'days',
        'contentType': 'csv',
    }
    query_string = urlencode(query_params)
    return (
        f'{BASE_API_URL}/{location}/{start_date}/{final_date}?{query_string}'
    )


def build_icon_tag(icon: str) -> str:
    return f'{BASE_ICON_URL}/{icon}.svg'
