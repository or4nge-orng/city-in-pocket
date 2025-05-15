import os
from requests import get
from random import choice
from dotenv import load_dotenv
from vkpymusic import Service
from datetime import timezone, tzinfo


load_dotenv()
def get_city_by_lat_long(lat, long):
    json = {
        'key': os.getenv('WEATHER_TOKEN'),
        'q': f'{lat},{long}'
    }

    request = 'http://api.weatherapi.com/v1/current.json'
        
    return get(request, params=json).json()['location']['name']


def get_region_by_lat_long(lat, long):
    json = {
        'key': os.getenv('WEATHER_TOKEN'),
        'q': f'{lat},{long}'
    }

    request = 'http://api.weatherapi.com/v1/current.json'
        
    return get(request, params=json).json()['location']['region']


def get_weather_now(lat, long):
    json = {
        'key': os.getenv('WEATHER_TOKEN'),
        'q': f'{lat},{long}'
    }

    request = 'http://api.weatherapi.com/v1/current.json'

    data = float(get(request, params=json).json()['current']['temp_c'])
    if data > 0:
        return f'+{data}°C'
    elif data < 0:
        return f'-{data}°C'
    return f'{data}°C'


def get_city_by_name(city):
    json = {
        'key': os.getenv('WEATHER_TOKEN'),
        'q': city
    }

    request = 'http://api.weatherapi.com/v1/current.json'
        
    return get(request, params=json).json()['location']['name']


def get_weather_for_day(lat, long):
    json = {
        'key': os.getenv('WEATHER_TOKEN'),
        'q': f'{lat},{long}'
    }

    request = get('http://api.weatherapi.com/v1/forecast.json', params=json).json()["forecast"]["forecastday"][0]["day"]

    res = {
        'avgtemp_c': f'{request["avgtemp_c"]}°C',
        'maxtemp_c': f'{request["maxtemp_c"]}°C',
        'maxwind_kph': f'{request["maxwind_kph"]} км/ч',
        'avghumidity': f'{request["avghumidity"]}%',
    }
    if request['daily_chance_of_rain'] > 0:
        res['daily_chance_of_rain'] = f'{request["daily_chance_of_rain"]}%'
    if request['daily_chance_of_snow'] > 0:
        res['daily_chance_of_snow'] = f'{request["daily_chance_of_snow"]}%'
    return res


def get_song_of_a_day():
    load_dotenv()
    service = Service(os.getenv('VK_AGENT'), os.getenv('VK_TOKEN'))
    tracks = service.get_playlists_by_userid(479699743)
    for i in tracks:
        if i.title == 'tool':
            playlist = service.get_songs_by_playlist(i, count=100) 
            break
        
    # return service.save_music(choice(playlist), overwrite=True)
    return choice(playlist)