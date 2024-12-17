import os

from dotenv import load_dotenv

load_dotenv()

WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')
TEMPLATE_URL_API = (
    'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/'
    '{location}/{start_date}/{final_date}?key={WEATHER_API_KEY}&unitGroup=metric&include=days&contentType=csv'
)

ICON_URL = 'https://raw.githubusercontent.com/visualcrossing/WeatherIcons/main/SVG/1st%20Set%20-%20Color/{icon}.svg'

TEMPLATE_ICON_TAG = (
    '<img src=""https://raw.githubusercontent.com/visualcrossing/WeatherIcons/'
    'main/SVG/1st%20Set%20-%20Color/{icon}.svg" alt="{icon}">'
)
