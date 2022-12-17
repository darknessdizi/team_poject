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

        '''Возвращает инф-ию о пользователе
        в виде {"city": "", "age": "", "user_name": "", "sex": ""}'''

        url = "https://api.vk.com/method/users.get"
        headers = self.get_headers()
        params = {"user_ids": user_id,
                  "fields": "city, sex, bdate"}
        res = requests.get(url=url, params={**self.params, **params}, headers=headers)
        user_info = {"city": "", "age": "", "user_name": "", "sex": ""}
        # user_name = res.json().get('response')[0].get("user_name")
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
        print(user_info)
        return user_info

    def get_users(self, city, sex, age, status=None):

        '''Возвращает список пользователей с номером id и их именами'''

        url = "https://api.vk.com/method/users.search"
        headers = self.get_headers()
        if "-" in age:
            age_from, age_to = age.split("-")
            params = {'fields': "first_name, last_name, bdate, sex",
                      'q': city,
                      'count': 20,
                      'offset': 1,
                      'age_from': age_from,
                      'age_to': age_to,
                      'sex': sex
                      }
        else:
            age = datetime.datetime.now() - datetime.timedelta(days=365 * int(age))
            age = age.year
            # params = {'fields': "first_name, bdate",
            params = {'fields': "user_name, bdate",
                      'q': city,
                      'count': 20,
                      'offset': 1,
                      'birth_year': age,
                      'sex': sex
                      }
        res = requests.get(url=url, params={**self.params, **params}, headers=headers)

        result = res.json().get('response').get('items')
        with open('data.json', 'w', encoding='utf-8') as file:
            json.dump(res.json(), file, ensure_ascii=False, indent=3)
        list_users = []
        for item in result:
            if item.get('is_closed') is not True:
                list_user = []
                list_user.append(item.get('id'))
                user_name = f"{item.get('first_name')} {item.get('last_name')}"
                list_user.append(user_name)
                list_users.append(list_user)

        return list_users

    def get_users_photo(self, user_id):

        """ метод возвращает словарь вида {'href': [], 'owner_id': "", "user_link": ""}
           с ссылками на фото пользователя.
           При отсутствии фото в профиле пользователя или их количестве < 3 возвращает None"""

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

        if len(photo_dict) < 3 or photo_dict is None:
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

    def get_photo_from_iterator(self, list_of_users, len_list, kursor):
        # передаем список пользователей
        iterator = iter(list_of_users)
        # цикл пока не найдет пользователя с фото
        while True:
            if kursor < len_list:
                item = next(iterator)
                id = item[0]
                print(id)
                time.sleep(2.5)
                photos = vk.get_users_photo(str(id))
                # смещение по индексу списка
                kursor += 1
                if photos is not None:
                    name = item[1]
                    photos['user_name'] = name
                    return photos, kursor
            else:
                print('фото закончились')
                break


if __name__ == '__main__':
    pass

    #для теста

    # access_token = token_vk.token_vk
    # # #для теста
    # list_input = ['30-40', 2, "Сочи"]
    # age = list_input[0]
    # city = list_input[2]
    # sex = int(list_input[1])
    # vk = RequestsVk(access_token)
    # user_info = vk.get_user('710698165')
    # # возвращает список словарей пользователей вида {"href": [], "user_name": "", "user_link": ""}
    # pprint(vk.get_users(city, sex, age))

    # pprint(vk.get_users_photo('738206322'))
    # pprint(vk.users_info(city, sex, age))

    # итератором проходим по списку полученных пользователей в рез-те поиска

    #list_of_users = vk.get_users(city, sex, age)

    # def get_photo_from_iterator(iterator, kursor):
    #     iterator = iter(iterator)
    #     while True:
    #         item = next(iterator)
    #         id = item[0]
    #         photos = vk.get_users_photo(str(id))
    #         kursor += 1
    #         if photos is not None:
    #             return photos, kursor

    # kursor = 0
    #
    # answer = input('еще искать? (ответ: еще): ')
    # len_list = len(list_of_users)
    #
    # while answer == 'еще':
    #
    #     photos, kursor = vk.get_photo_from_iterator(list_of_users[kursor:], len_list, kursor=kursor)
    #     if photos is None:
    #         continue
    #     pprint(photos)
    #     pprint(kursor)
    #     kursor += 1
    #     answer = input('еще искать? ответ: еще')
    #     if kursor == len(list_of_users) - 1:
    #         print('поиск завершен')
    #         break
    #     if answer == 'нет':
    #         break
