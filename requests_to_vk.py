import json
import requests
from pprint import pprint
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

        '''Возвращает инф-ию о пользователе'''

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
        else: city = ""
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

    def get_users(self, input_params):

        '''Возвращает список пользователей с номером id и их именами'''

        url = "https://api.vk.com/method/users.search"
        headers = self.get_headers()
        city = input_params.get('city')
        city_id = self.get_city_id(city)

        if city_id is None:
            print("город не найден. уточните название города")
            return None

        sex = input_params.get('sex')
        age = input_params.get('age')
        age_from, age_to = age
        age_from = int(age_from)
        age_to = int(age_to)
        params = {'fields': "first_name, bdate, deactivated, is_closed, blacklisted, city",
                  'q': "",
                  'count': 10,

                  'age_from': age_from,
                  'age_to': age_to,
                  'sex': sex,
                  'city': city_id
                  }

        res = requests.get(url=url, params={**self.params, **params}, headers=headers)
        result = res.json().get('response').get('items')
        with open('data.json', 'w', encoding='utf-8') as file:
            json.dump(res.json(), file, ensure_ascii=False, indent=3)

        list_users = []
        for item in result:
            list_user = []
            if item.get('blacklisted') == 0 and item.get('is_closed') is False :
                list_user.append(item.get('id'))
                user_name = f"{item.get('first_name')} {item.get('last_name')}"
                list_user.append(user_name)
                list_users.append(list_user)
        return list_users

    def get_users_photo(self, user_id):

        """ возвращает 3 фото пользователя с макс. количеством лайков.
        Фото берутся со страницы пользователя и стены"""

        url = "https://api.vk.com/method/photos.get"
        params1 = {
            'owner_id': user_id,
            'album_id': -7,
            'extended': 1,
            'photo_sizes': 1,

            'count': 30
        }
        params2 = {
            'owner_id': user_id,
            'album_id': -6,
            'extended': 1,
            'photo_sizes': 1,

            'count': 30
        }
        headers = self.get_headers()
        res1 = requests.get(url=url, params={**self.params, **params1}, headers=headers)
        res2 = requests.get(url=url, params={**self.params, **params2}, headers=headers)

        with open('photo.json', 'w') as file:
             json.dump(res1.json(), file, ensure_ascii=False, indent=3)
             json.dump(res2.json(), file, ensure_ascii=False, indent=3)
        photos_info1 = res1.json().get('response').get('items')
        photos_info2 = res2.json().get('response').get('items')
        # берем фото из запроса по фото с профиля и по  фото со стены
        photos_info = photos_info1 + photos_info2

        if len(photos_info) < 3 or photos_info is None:
            return None

        dict_likes = {'count': [], 'href': [], 'owner_id': ""}
        dict_likes_max = {'href': [], 'owner_id': ""}

        for photo in photos_info:
            dict_likes['count'].append(photo.get('likes').get('count'))
            dict_likes['href'].append(photo.get('sizes')[-1].get('url'))
            dict_likes['owner_id'] = str(photo.get('owner_id'))


        while len(dict_likes_max.get("href")) < 3:

            max_like = max(dict_likes.get('count'))
            index = dict_likes.get('count').index(max_like)

            dict_likes.get('count').pop(index)
            dict_likes_max['href'].append(dict_likes.get('href').pop(index))

        return dict_likes_max

    def get_city_id(self, city):
        url = "https://api.vk.com/method/database.getCities"
        headers = self.get_headers()
        params = {
            'q': city,
            'count': 1
        }
        res = requests.get(url=url,  params={**self.params, **params}, headers=headers)
        city_id = res.json().get('response').get('items')[0].get('id')
        return city_id


if __name__ == '__main__':
    pass
    access_token = token_vk.token_vk
    # #для теста
    list_input = [[30,30], 1, 'новосибирск']
    age = list_input[0]
    city = list_input[2]
    sex = int(list_input[1])
    vk = RequestsVk(access_token)
    # # user_info = vk.get_user(user_id)
    # # возвращает список словарей пользователей вида {"href": [], "first_name": "", "last_name": "", "user_link": ""}
    # input_params = {'age': ['34', '57'], 'sex': '1', 'city': 99}
    # users = vk.get_users(input_params)
    # pprint(users)
    #pprint(vk.get_users_photo('370844284'))
    print(vk.get_city_id('сочи'))



