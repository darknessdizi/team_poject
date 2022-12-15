import json
import requests
from pprint import pprint
import datetime
import time
import token_vk


class RequestsVk:
    def __init__(self, access_token, version='5.131'):
        self.access_token = access_token
        self.version = version
        self.params = {'access_token': self.access_token, 'v': self.version}

    def get_headers(self):
        return {'Content-Type': 'application/json', 'Authorization': f'OAuth {self.access_token}'}

    def get_user(self, user_id):

        """ возвращает инф-ию о пользователе"""

        url = "https://api.vk.com/method/users.get"
        headers = self.get_headers()
        params = {"user_ids": user_id,
                  "fields": "city, sex, bdate"}
        res = requests.get(url=url, params={**self.params, **params}, headers=headers)
        pprint(res.json())
        user_info = {"city": "", "age": "", "user_name": "", "sex": ""}
        first_name = res.json().get('response')[0].get("first_name")
        last_name = res.json().get('response')[0].get("last_name")
        name = first_name + " " + last_name
        user_info['user_name'] = name
        if res.json().get('response')[0].get("city"):
            city = res.json().get('response')[0].get("city").get("title")
        else:
            city = ""
        user_info['city'] = city
        if res.json().get('response')[0].get("sex"):
            sex = res.json().get('response')[0].get("sex")
        else:
            sex = ""
        user_info['sex'] = sex
        if res.json().get('response')[0].get("bdate"):
            age = res.json().get('response')[0].get("bdate")
        else:
            age = ""
        user_info['age'] = age
        return user_info

    def get_users(self, city=None, sex=None, age=None, status=None):

        url = "https://api.vk.com/method/users.search"
        headers = self.get_headers()
        if "-" in age:
            age_from, age_to = age.split("-")
            params = {'fields': "first_name, last_name, bdate, sex",
                      'q': city,
                      'count': 50,
                      'offset': 1,
                      'age_from': age_from,
                      'age_to': age_to,
                      'sex': sex
                      }
        else:
            age = datetime.datetime.now() - datetime.timedelta(days=365 * int(age))
            age = age.year
            params = {'fields': "first_name, last_name, bdate, sex",
                      'q': city,
                      'count': 2,
                      'offset': 1,
                      'birth_year': age,
                      'sex': sex
                      }
        res = requests.get(url=url, params={**self.params, **params}, headers=headers)

        result = res.json().get('response').get('items')

        with open('data.json', 'w') as file:
            json.dump(result, file, ensure_ascii=False, indent=3)
        return result

    def get_users_photo(self, user_id):
        """ метод возвращает словарь вида {'href': [], 'owner_id': ""}
           с ссылками на фото пользователя """
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

        photo_dict = res.json().get('response').get('items')

        if len(photo_dict) < 3:
            return None

        dict_likes = {'count': [], 'href': []}
        dict_likes_max = {'href': [], 'owner_id': "", "user_link": ""}
        for photo in photo_dict:
            dict_likes['count'].append(photo.get('likes').get('count'))
            dict_likes['href'].append(photo.get('sizes')[-1].get('url'))

        while len(dict_likes_max.get("href")) < 3:
            max_like = max(dict_likes.get('count'))
            index = dict_likes.get('count').index(max_like)

            dict_likes.get('count').pop(index)
            dict_likes_max['href'].append(dict_likes.get('href').pop(index))

        dict_likes_max['user_link'] = "https://vk.com/id" + str(photo_dict[0].get('owner_id'))
        dict_likes_max['owner_id'] = photo_dict[0].get('owner_id')

        return dict_likes_max


if __name__ == '__main__':
    pass

    # #для теста
    # access_token = token_vk.access_token
    # list_input = ['30-40', 1, "Сочи"]
    # age = list_input[0]
    # city = list_input[2]
    # sex = int(list_input[1])
    # vk = RequestsVk(access_token)
    # # user_info = vk.get_user(user_id)
    # pprint(vk.get_users(city=city, sex=sex, age=age, status=None))
    #pprint(vk.get_users_photo('710698165'))
    # # возвращает список словарей пользователей вида {"href": [], "first_name": "", "last_name": "", "user_link": ""}
    # pprint(vk.users_info(age, city, sex))
