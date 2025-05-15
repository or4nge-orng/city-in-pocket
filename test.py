from requests import get
import os
from dotenv import load_dotenv
from pprint import pprint

load_dotenv()

json = {
        'key': os.getenv('WEATHER_TOKEN'),
        'q': 'Благовещенск'
    }

request = 'http://api.weatherapi.com/v1/forecast.json'
        
pprint(get(request, params=json).json())