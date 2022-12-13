import json
import requests
from pprint import pprint
from  dotenv import load_dotenv
import os
load_dotenv(".env")
#access_token = os.getenv("access_token")


class VK:
    def __init__(self, access_token, version='5.131'):
        self.access_token = access_token
        self.version = version
        self.params = {'access_token': self.access_token, 'v': self.version}

    def get_headers(self):
        return {'Content-Type': 'application/json', 'Authorization': f'OAuth {self.access_token}'}

    def get_users(self, city):
        url = "https://api.vk.com/method/users.search"
        headers = self.get_headers()
        params = {'fields': "city, birth_day, birth_month, birth_year, sex",
                  'q': 'новосибирск',
                  'count': 1000,
                  'offset': 1
                }
        while True:
            res = requests.get(url=url, params={**self.params, **params}, headers=headers)
            print(len(res.json().get('response').get('items')))
            with open("data.json", "w", encoding='utf-8') as file:
                json.dump(res.json(), file, ensure_ascii=False, indent=3)
            pprint(res.json())

    def get_cities(self):
       pass


if __name__ == '__main__':
    access_token = os.getenv("access_token")
    vk_user_id = '710698165'
    list_requests_from_user = ['возраст', 'пол', 'москва']
    city = list_requests_from_user[2]
    vk = VK(access_token)
    pprint(vk.get_users(city))

