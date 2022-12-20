import json
import requests
from pprint import pprint
import token_vk
from datetime import time
import time


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

    def get_users(self, input_params):  # нужен параметр offset
        # формат input_params {'age': ['34', '57'], 'sex': 1, 'city': 'новосибирск'}

        '''Возвращает список пользователей с номером id и их именами'''

        url = "https://api.vk.com/method/users.search"
        headers = self.get_headers()  # формат {'Content-Type': 'application/json', 'Authorization': 'OAuth vk1.a.Y45795E4...nsUC3NqXDQ'}
        city = input_params.get('city')  # формат 'новосибирск'
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

        res = requests.get(url=url, params={**self.params, **params},
                           headers=headers)  # формат <Response [200]> '{"response":{"count":870277,"items":[{"id":488749963,"bdate":"1.6.1980","blacklisted":0,"track_code":"ab6e1d82rhEPr3d-cs639e2Rj5EqRgu-huz0LNSYdOb2ANITtEnJeEr-LBJ-k7bz2AohU-ZEY7CA7_Qs2v4Gjw","first_name":"Юлия","last_name":"Волкова","can_access_closed":true,"is_closed":false},{"id":576362782,"bdate":"25.10.1984","city":{"id":5094582,"title":"Santa Barbara"},"blacklisted":0,"track_code":"c0bffc11N5qTfQJ63Zn1tGERBkOOgDkmawlk3OZeLLUxjuInvkJQ84J7DEaLyqG0VYGmj0OCUShtCmTc6Dhe3A","first_name":"Katy","last_name":"Perry","can_access_closed":true,"is_closed":false},{"id":402957890,"bdate":"17.3.1986","blacklisted":0,"track_code":"4914399b-V44uFWrGyMgrtm3eA4W_gRIrDDhk4cKqpS1wGO0p_6eNynuCJYeciXz7yLXw9n8bEaqM-GTiWzY_Q","first_name":"Женя","last_name":"Усова","can_access_closed":false,"is_closed":true},{"id":574435155,"bdate":"3.2.1984","blacklisted":0,"track_code":"127bbdc5u0OpzTlstilGq0P4XmJwSKB4rKPiDLUusoOfd9WVFZHcKuOaZVC6fET-dG_4o7pKyHaqoOIMu0jA6g","first_name":"Кристина","last_name":"Белова","can_access_closed":true,"is_closed":false},{"id":400790625,"bdate":"1.5.1986","city":{"id":99,"title":"Новосибирск"},"blacklisted":0,"track_code":"10d5903bbn8WpIeOsk25xQk_ZWnug98gtSMloe7iYTkMB3_br5QJFlX_jLPiSrjCNa3ErySBty6zICWh4IQTUA","first_name":"Яна","last_name":"Гончарова","can_access_closed":true,"is_closed":false},{"id":417877132,"bdate":"3.6.1970","blacklisted":0,"track_code":"8a62e93f0sVE0k59z0G-XjFpv4zngN1AKulxSVLAUE9iV0kiqA21rAaCQETPRewHAPwZSyqCtU4s6nFJXKYiJg","first_name":"Ирина","last_name":"Родомакина","can_access_closed":true,"is_closed":false},{"id":323416007,"bdate":"8.8.1978","blacklisted":0,"track_code":"907ca90bxGr3ph9O9Dseo4aPL15fE_cmkkab_10CgFm69YtcGVmjA7LzEXbyPxiisBuImpcRnyiURZv_U2TyMA","first_name":"Виктория","last_name":"Иванова","can_access_closed":false,"is_closed":true},{"id":436528490,"bdate":"4.5.1978","city":{"id":99,"title":"Новосибирск"},"blacklisted":0,"track_code":"7c3b97daPz2NgeyUrPqGTnKn6sfLThf8F7egJ5VrCahudlKkXB1YVMyG56n-rIJNSD1JCgRMf_IRtKAnmw17wQ","first_name":"Вика","last_name":"Ларина","can_access_closed":false,"is_closed":true},{"id":433476343,"bdate":"25.4.1985","blacklisted":0,"track_code":"15e438cct3VHhLcG8-EeNn0XO12m5AzTPfMy3vUZhOfSJL6swL_QHFbV5j6lt08xQ4OfnWrmZN078DLe-3_2jg","first_name":"Кира","last_name":"Чудина","can_access_closed":true,"is_closed":false},{"id":397419005,"bdate":"8.11.1980","blacklisted":0,"track_code":"831e4513qQi3hhm4uz61Xvlk5yZCoV1iyCoLLlEaZsze1wnboYjOYaCERIaxZeRYwv9A4oijNWzOKQsuX3wUpQ","first_name":"Tanya","last_name":"Aronovich","can_access_closed":true,"is_closed":false}]}}'
        result = res.json().get('response').get(
            'items')  # формат [{'id': 488749963, 'bdate': '1.6.1980', 'blacklisted': 0, 'track_code': 'ab6e1d82rhEPr3d-cs63...7_Qs2v4Gjw', 'first_name': 'Юлия', 'last_name': 'Волкова', 'can_access_closed': True, 'is_closed': False}, {'id': 576362782, 'bdate': '25.10.1984', 'city': {...}, 'blacklisted': 0, 'track_code': 'c0bffc11N5qTfQJ63Zn1...CmTc6Dhe3A', 'first_name': 'Katy', 'last_name': 'Perry', 'can_access_closed': True, 'is_closed': False}, {'id': 402957890, 'bdate': '17.3.1986', 'blacklisted': 0, 'track_code': '4914399b-V44uFWrGyMg...M-GTiWzY_Q', 'first_name': 'Женя', 'last_name': 'Усова', 'can_access_closed': False, 'is_closed': True}, {'id': 574435155, 'bdate': '3.2.1984', 'blacklisted': 0, 'track_code': '127bbdc5u0OpzTlstilG...oOIMu0jA6g', 'first_name': 'Кристина', 'last_name': 'Белова', 'can_access_closed': True, 'is_closed': False}, {'id': 400790625, 'bdate': '1.5.1986', 'city': {...}, 'blacklisted': 0, 'track_code': '10d5903bbn8WpIeOsk25...ICWh4IQTUA', 'first_name': 'Яна', 'last_name': 'Гончарова', 'can_access_closed': True, 'is_closed': False}, {'id': 417877132, 'bdate': '3.6.1970', 'blacklisted': 0, 'track_code': '8a62e93f0sVE0k59z0G-...6nFJXKYiJg', 'first_name': 'Ирина', 'last_name': 'Родомакина', 'can_access_closed': True, 'is_closed': False}, {'id': 323416007, 'bdate': '8.8.1978', 'blacklisted': 0, 'track_code': '907ca90bxGr3ph9O9Dse...RZv_U2TyMA', 'first_name': 'Виктория', 'last_name': 'Иванова', 'can_access_closed': False, 'is_closed': True}, {'id': 436528490, 'bdate': '4.5.1978', 'city': {...}, 'blacklisted': 0, 'track_code': '7c3b97daPz2NgeyUrPqG...tKAnmw17wQ', 'first_name': 'Вика', 'last_name': 'Ларина', 'can_access_closed': False, 'is_closed': True}, {'id': 433476343, 'bdate': '25.4.1985', 'blacklisted': 0, 'track_code': '15e438cct3VHhLcG8-Ee...8DLe-3_2jg', 'first_name': 'Кира', 'last_name': 'Чудина', 'can_access_closed': True, 'is_closed': False}, {'id': 397419005, 'bdate': '8.11.1980', 'blacklisted': 0, 'track_code': '831e4513qQi3hhm4uz61...KQsuX3wUpQ', 'first_name': 'Tanya', 'last_name': 'Aronovich', 'can_access_closed': True, 'is_closed': False}]
        with open('data.json', 'w', encoding='utf-8') as file:
            json.dump(res.json(), file, ensure_ascii=False, indent=3)

        list_users = []
        for item in result:
            list_user = []
            if item.get('blacklisted') == 0 and item.get('is_closed') is False:
                list_user.append(item.get('id'))  # формат [488749963]
                user_name = f"{item.get('first_name')} {item.get('last_name')}"  # формат 'Юлия Волкова'
                list_user.append(user_name)  # формат [488749963, 'Юлия Волкова']
                bdate = item.get('bdate')
                list_user.append(bdate)
                list_users.append(list_user)  # формат [[488749963, 'Юлия Волкова'], ...]

        return list_users

    def get_users_photo(self, user_id):
        # формат user_id '488749963'

        """ возвращает 3 фото пользователя с макс. количеством лайков.
        Фото берутся со страницы пользователя и стены"""

        url = "https://api.vk.com/method/photos.get"

        params = {
            'owner_id': user_id,
            'album_id': -6,
            'extended': 1,
            'photo_sizes': 1
        }
        headers = self.get_headers()
        time.sleep(2)
        res = requests.get(url=url, params={**self.params, **params}, headers=headers)

        with open('photo.json', 'w') as file:
            json.dump(res.json(), file, ensure_ascii=False, indent=3)

        photos_info = res.json().get('response').get('items')

        # берем фото из запроса по фото с профиля и по  фото со стены

        if len(photos_info) < 3 or photos_info is None:
            return None

        dict_likes = {'count': [], 'href': [], 'owner_id': ""}
        dict_likes_max = {'href': [], 'owner_id': ""}

        for photo in photos_info:
            dict_likes['count'].append(photo.get('likes').get(
                'count'))  # format {'count': [849], 'href': ['https://sun9-1.usera...type=album'], 'owner_id': ''}
            dict_likes['href'].append(photo.get('sizes')[-1].get('url'))
            dict_likes['owner_id'] = str(photo.get('owner_id'))
            # format {'count': [849, 858, 272, 341, 316, 214, 304, 253], 'href': ['https://sun9-1.usera...type=album', 'https://sun9-64.user...type=album', 'https://sun9-75.user...type=album', 'https://sun9-80.user...type=album', 'https://sun9-9.usera...type=album', 'https://sun9-9.usera...type=album', 'https://sun9-80.user...type=album', 'https://sun9-61.user...type=album'], 'owner_id': '488749963'}

        while len(dict_likes_max.get("href")) < 3:
            max_like = max(dict_likes.get('count'))  # format 2107
            index = dict_likes.get('count').index(max_like)  # format 30

            dict_likes.get('count').pop(index)
            dict_likes_max['href'].append(dict_likes.get('href').pop(index))
            dict_likes_max['owner_id'] = dict_likes.get('owner_id')

        print(type(user_id))
        if self.get_photo_tag(str(user_id)):  # берем фото с отметками пользователя
            dict_likes_max['href'] = dict_likes_max['href'] + self.get_photo_tag(str(user_id))

        return dict_likes_max

    def get_photo_tag(self, user_id):

        """ Метод возвращает список ссылок на фотографии, где отмечен пользователь"""

        url = "https://api.vk.com/method/newsfeed.get"
        headers = self.get_headers()
        start_time = 1  # int(datetime.datetime.now().timestamp()-365.24*86400)# - 365.24*86400)

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
        res = requests.get(url=url, params={**self.params, **params},
                           headers=headers)  # формат <Response [200]>  '{"response":{"count":3,"items":[{"id":99,"title":"Новосибирск","country":"Новосибирская область"}]}}'
        if not res.json().get('response').get('items'):
            return None
        city_id = res.json().get('response').get('items')[0].get('id')  # формат 99
        return city_id
    


if __name__ == '__main__':
    pass
    access_token = token_vk.token_vk
    # #для теста
    list_input = [[30, 30], 1, 'новосибирск']
    age = list_input[0]
    city = list_input[2]
    sex = int(list_input[1])
    vk = RequestsVk(access_token)
    # # user_info = vk.get_user(user_id)
    # # возвращает список словарей пользователей вида {"href": [], "first_name": "", "last_name": "", "user_link": ""}
    input_params = {'age': ['15', '25'], 'sex': 1, 'city': 'сочи'}
    # pprint(vk.get_users(input_params))
    list_ = [[621028572, 'Ирина Павлова', '11.3.1997'],
             [638832767, 'Lumıne Blondeshıne', '11.4.2006'],
             [559067825, 'Арина Фатова', '2.2.2001'],
             [96847160, 'Елена Поволоцкая', '28.9.1998'],
             [265143019, 'Юлия Секси', '7.4.1998'],
             [559378944, 'Екатерина Миронова', '9.6.2000'],
             [458593529, 'Мика Цугба', '24.3.2003'],
             [122226091, 'Дарья Постникова', '12.11.1997'],
             [568368117, 'Анжелика Пожидаева', '26.1.1998']]
    # pprint(vk.get_users_photo())
    # offset = 1
    # while True:
    users = vk.get_users(input_params)
    for i in users:
        # pprint(vk.get_photo_tag(i[0]))
        pprint(vk.get_users_photo(i[0]))
    #     offset += 10

    # #pprint(users)
    # for user in users:
    #     time.sleep(2)
    #     pprint(vk.get_users_photo(user[0]))
    # # print(vk.get_city_id('сочи'))

    # pprint(vk.get_photo_tag('243426041'))
