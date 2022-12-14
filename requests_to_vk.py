import json
import requests
from pprint import pprint
from dotenv import load_dotenv
import os
import datetime
import time


load_dotenv(".env")


class VK:
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

    def get_users(self, city, sex, age):
        url = "https://api.vk.com/method/users.search"
        headers = self.get_headers()
        if "-" in age:
            age_from, age_to = age.split("-")
            params = {'fields': "first_name, last_name, bdate, sex",
                  'q': city,
                  'count': 1000,
                  'offset': 1,
                  'age_from': age_from,
                  'age_to': age_to,
                  'sex': sex
                  }
        else:
            age = datetime.datetime.now() - datetime.timedelta(days=365 * int(age))
            age = age.year
            params = {'fields': "first_name, bdate",
                      'q': city,
                      'count': 1000,
                      'offset': 1,
                      'birth_year': age,
                      'sex': sex
                      }
        res = requests.get(url=url, params={**self.params, **params}, headers=headers)
        result = res.json().get('response').get('items')
        with open('data.json', 'w') as file:
            json.dump(res.json(), file, ensure_ascii=False, indent=3)
        list_user, list_users = [], []
        for item in result:
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
        with open('photo.json', 'w') as file:
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

    def users_info(self, city, sex, age):

        list_users = vk.get_users(city, sex, age)
        list_new = []
        for item in list_users:
            time.sleep(3)
            new_dict = {"link_photo": [], "user_name": "",  "user_link": ""}
            dict1 = vk.get_users_photo(item[0])
            if dict1.get("href") != []:
                new_dict["link_photo"] = dict1.get("href")
                new_dict["user_name"] = item[1] + item[2]
                new_dict["user_link"] = "https://vk.com/id" + str(item[0])
                list_new.append(new_dict)
        return list_new


if __name__ == '__main__':
    access_token = os.getenv("access_token")
    #для теста
    list_input = ['30-40', 1, "Сочи"]
    age = list_input[0]
    city = list_input[2]
    sex = int(list_input[1])
    vk = VK(access_token)
    user_info = vk.get_user(user_id)
    # возвращает список словарей пользователей вида {"href": [], "first_name": "", "last_name": "", "user_link": ""}
    pprint(vk.users_info(age, city, sex))




