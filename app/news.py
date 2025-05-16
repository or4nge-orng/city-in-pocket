from requests import get, post
from bs4 import BeautifulSoup
from app.request import get_city_by_lat_long, get_region_by_lat_long
from dotenv import load_dotenv
from os import getenv


class News():
    def __init__(self, loc):
        self.loc = loc

    def get_html(self):
        city = get_city_by_lat_long(*self.loc)
        region = get_region_by_lat_long(*self.loc)
        return get(f'https://news.google.com/search?q={city}%20{region}&hl=ru&gl=RU&ceid=RU%3Aru').text

    def get_news(self):
        html = BeautifulSoup(self.get_html(), 'html.parser')
        articles = html.find_all('article')
        for article in articles:
            link = article.find('a', {'class': 'JtKRv'})
            yield link
            
    def get_res(self, n):
        res = []
        for i in self.get_news():
            res.append({'title': i.get_text(), 'link': 'https://news.google.com' + i.get('href')[1:]})
            if len(res) == n:
                break
        return res
