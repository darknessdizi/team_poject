# В модуле requests_to_vk.py создан класс RequestsVk, входным параметром которого является
# токен пользователя вконтакте. В классе реализованы функции :
#
# - получение данных пользователя ВК путем обращения к API Вконтакте, используя метод
#   users.get. Входной параметр - user id пользователя. Функция возвращает параметры пользователя:
#   {"city": "", "age": "", "user_name": "", "sex": ""}
#
# - получение списка пользователей путем запроса к API ВКонтакте методом users.search.
#   Поиск осуществляется по входным параметрам вида {'age': ['34', '57'], 'sex': 1, 'city': 'новосибирск'},
#   полученных от пользователя ВК. Метод возвращает список  вида [user_id, user name, bdate]
#
# - получение фото пользователя по обращению к API Вконтакте с помощью метода photos.get. Входной параметр -
#   user id. Фото выбираются у пользователя в максим. разрешении со страницы и стены, в количестве
#   до трех штук с максимальным количеством лайков.

import json
import requests

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

    def get_users(self, input_params):  
        
        '''Возвращает список пользователей с номером id и их именами'''

        url = "https://api.vk.com/method/users.search"
        headers = self.get_headers()
        city = input_params['filtr_dict'].get('city') 
        city_id = self.get_city_id(city)

        if city_id is None:
            print("Город не найден. уточните название города")
            return None

        sex = input_params['filtr_dict'].get('sex')
        age = input_params['filtr_dict'].get('age')
        age_from = int(age[0])
        age_to = int(age[1])
        offset = input_params.get('offset')
        params = {'fields': "first_name, bdate, deactivated, is_closed, blacklisted, city, has_photo",
                  'q': "",
                  'count': 3,
                  'offset': offset,
                  'age_from': age_from,
                  'age_to': age_to,
                  'sex': sex,
                  'city_id': city_id
                  }

        res = requests.get(url=url, params={**self.params, **params},headers=headers)
        result = res.json().get('response').get('items')
        with open('data.json', 'w', encoding='utf-8') as file:
            json.dump(res.json(), file, ensure_ascii=False, indent=3)

        list_users = []
        for item in result:
            list_user = []
            if item.get('blacklisted') == 0 and item.get('is_closed') is False:
                list_user.append(item.get('id'))  
                user_name = f"{item.get('first_name')} {item.get('last_name')}"  
                list_user.append(user_name)  
                bdate = item.get('bdate')
                list_user.append(bdate)
                list_users.append(list_user)  

        return list_users

    def get_users_photo(self, user_id):
        """ Возвращает до 3-х фото пользователя с макс. количеством лайков.
        Фото берутся со страницы пользователя и стены"""

        url = "https://api.vk.com/method/photos.get"

        params_profile = {
            'owner_id': user_id,
            'album_id': -6,
            'extended': 1,
            'photo_sizes': 1,
            'has_photo': 1
        }
        params_wall = {
            'owner_id': user_id,
            'album_id': -7,
            'extended': 1,
            'photo_sizes': 1,
            'has_photo': 1
        }
        headers = self.get_headers()
        res_profile = requests.get(url=url, params={**self.params, **params_profile}, headers=headers)
        res_wall = requests.get(url=url, params={**self.params, **params_wall}, headers=headers)

        photos_profile = []
        photos_wall = []

        if res_profile.json().get('response').get('items'):
            photos_profile = res_profile.json().get('response').get('items')
        if res_wall.json().get('response').get('items'):
            photos_wall = res_wall.json().get('response').get('items')
        photos_info = photos_profile + photos_wall

        if photos_info is None:
            return None

        dict_likes = {'count': [], 'href': [], 'owner_id': ""}
        dict_likes_max = {'href': [], 'owner_id': ""}

        for photo in photos_info:
            dict_likes['count'].append(photo.get('likes').get('count'))
            dict_likes['href'].append(photo.get('sizes')[-1].get('url'))
            dict_likes['owner_id'] = str(photo.get('owner_id'))

        if len(dict_likes.get("href")) <= 3:
            dict_likes_max['href'].extend(dict_likes.get('href'))
        else:
            while len(dict_likes_max.get("href")) < 3:
                max_like = max(dict_likes.get('count')) 
                index = dict_likes.get('count').index(max_like) 

                dict_likes.get('count').pop(index)
                dict_likes_max['href'].append(dict_likes.get('href').pop(index))
        
        dict_likes_max['owner_id'] = dict_likes['owner_id']

        return dict_likes_max

    def get_photo_tag(self, user_id):

        """ Метод возвращает список ссылок на фотографии, где отмечен пользователь"""

        url = "https://api.vk.com/method/newsfeed.get"
        headers = self.get_headers()
        start_time = 1

        params = {
            'filters': 'photo_tag',
            'source_ids': user_id,
            'start_time': start_time
        }
        params = {**self.params, **params}
        res = requests.get(url=url, params=params, headers=headers)

        if not res.json().get('response').get('items'):
            return None

        list_photos = []
        for item in res.json().get('response').get('items')[0].get('photo_tags').get('items'):
            link = item.get('sizes')[-1].get('url')
            list_photos.append(link)

        return list_photos

    def get_city_id(self, city):
        url = "https://api.vk.com/method/database.getCities"
        headers = self.get_headers()
        params = {
            'q': city,
            'count': 1
        }
        res = requests.get(url=url, params={**self.params, **params}, headers=headers)
        if not res.json().get('response').get('items'):
            return None
        city_id = res.json().get('response').get('items')[0].get('id')  
        return city_id


if __name__ == '__main__':
    pass
    input = [[30], 1, ' манк']
    access_token = token_vk.token_vk
    vk = RequestsVk(access_token)
    users = vk.get_users(input)
