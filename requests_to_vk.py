import json
import requests
from pprint import pprint
from dotenv import load_dotenv
import os
import datetime

load_dotenv(".env")


class VK:
    def __init__(self, access_token, version='5.131'):
        self.access_token = access_token
        self.version = version
        self.params = {'access_token': self.access_token, 'v': self.version}

    def get_headers(self):
        return {'Content-Type': 'application/json', 'Authorization': f'OAuth {self.access_token}'}

    def get_users(self, city, sex, age_from, age_to):
        url = "https://api.vk.com/method/users.search"
        headers = self.get_headers()

        params = {'fields': "city, bdate, sex",
                  'q': city,
                  'count': 1000,
                  'offset': 1
                  }

        res = requests.get(url=url, params={**self.params, **params}, headers=headers)
        with open("data.json", "w", encoding='utf-8') as file:
            json.dump(res.json(), file, ensure_ascii=False, indent=3)
        result = res.json().get('response').get('items')
        time_now = datetime.datetime.now()
        age_from = time_now - datetime.timedelta(days=365 * int(age_from))
        age_to = time_now - datetime.timedelta(days=365 * int(age_to))
        list_users = []
        for item in result:
            if item.get('sex') == sex:
                if item.get('bdate') is not None and len(item.get('bdate')) == 8:
                    age = datetime.datetime.strptime(item.get('bdate'), "%d.%m.%Y")
                    list_user = []
                    if age_from >= age >= age_to:
                        list_user.append(item.get('id'))
                        list_user.append(item.get('first_name'))
                        list_user.append(item.get('last_name'))
                        list_users.append(list_user)
        return list_users

    def get_users_photo(self, user_id):
        url = "https://api.vk.com/method/photos.get"
        params = {
            'owner_id': user_id,
            'album_id': 'profile',
            'extended': 1,
            'photo_sizes': 1,
            'offset': 1,
            'count': 30
        }
        headers = self.get_headers()
        res = requests.get(url=url, params={**self.params, **params}, headers=headers)
        with open("photo.json", "w") as file:
            json.dump(res.json(), file, ensure_ascii=False, indent=3)
        photos_info_list = res.json().get('response').get('items')
        dict_likes = {'count': [], 'href': [], 'owner_id': ""}
        dict_likes_max = {'href': [], 'owner_id': ""}
        if len(photos_info_list) != 0:
            for photo in photos_info_list:
                dict_likes['count'].append(photo.get('likes').get('count'))
                dict_likes['href'].append(photo.get('sizes')[-1].get('url'))
                dict_likes['owner_id'] = photo.get('owner_id')

        if dict_likes.get('owner_id') != '':
            while True:
                if dict_likes.get('count') != []:
                    max_like = max(dict_likes.get('count'))
                    index = dict_likes.get('count').index(max_like)
                else:
                    index = 0
                href = dict_likes.get('href')
                if href != []:
                    dict_likes.get('count').pop(index)
                    max_href = href.pop(index)
                    dict_likes_max['href'].append(max_href)
                    dict_likes_max['owner_id'] = dict_likes.get('owner_id')
                if len(dict_likes_max.get('href')) == 3 or len(dict_likes.get('href')) == 0:
                    break
        return dict_likes_max

    def users_info(self):
        list_users = vk.get_users(city, sex, age_from, age_to)
        list_new = []
        for item in list_users:
            new_dict = {"href": [], "first_name": "", "last_name": "", "user_link": ""}
            dict1 = vk.get_users_photo(item[0])
            if dict1.get("href") != []:
                new_dict["href"] = dict1.get("href")
                new_dict["first_name"] = item[1]
                new_dict["last_name"] = item[2]
                new_dict["user_link"] = "https://vk.com/id" + str(item[0])
                list_new.append(new_dict)
        return list_new


if __name__ == '__main__':
    access_token = os.getenv("access_token")
    #для теста
    list_input = [25, 30, 1, "Москва"]
    city = list_input[3]
    sex = int(list_input[2])
    age_from = int(list_input[0])
    age_to = int(list_input[1])
    vk = VK(access_token)
    # возвращает список словарей пользователей вида {"href": [], "first_name": "", "last_name": "", "user_link": ""}
    pprint(vk.users_info())




