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
        # формат input_params {'age': ['34', '57'], 'sex': '1', 'city': 'новосибирск'}

        '''Возвращает список пользователей с номером id и их именами'''

        url = "https://api.vk.com/method/users.search"
        headers = self.get_headers() # формат {'Content-Type': 'application/json', 'Authorization': 'OAuth vk1.a.Y45795E4...nsUC3NqXDQ'}
        city = input_params.get('city') # формат 'новосибирск'
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

        res = requests.get(url=url, params={**self.params, **params}, headers=headers) # формат <Response [200]> '{"response":{"count":870277,"items":[{"id":488749963,"bdate":"1.6.1980","blacklisted":0,"track_code":"ab6e1d82rhEPr3d-cs639e2Rj5EqRgu-huz0LNSYdOb2ANITtEnJeEr-LBJ-k7bz2AohU-ZEY7CA7_Qs2v4Gjw","first_name":"Юлия","last_name":"Волкова","can_access_closed":true,"is_closed":false},{"id":576362782,"bdate":"25.10.1984","city":{"id":5094582,"title":"Santa Barbara"},"blacklisted":0,"track_code":"c0bffc11N5qTfQJ63Zn1tGERBkOOgDkmawlk3OZeLLUxjuInvkJQ84J7DEaLyqG0VYGmj0OCUShtCmTc6Dhe3A","first_name":"Katy","last_name":"Perry","can_access_closed":true,"is_closed":false},{"id":402957890,"bdate":"17.3.1986","blacklisted":0,"track_code":"4914399b-V44uFWrGyMgrtm3eA4W_gRIrDDhk4cKqpS1wGO0p_6eNynuCJYeciXz7yLXw9n8bEaqM-GTiWzY_Q","first_name":"Женя","last_name":"Усова","can_access_closed":false,"is_closed":true},{"id":574435155,"bdate":"3.2.1984","blacklisted":0,"track_code":"127bbdc5u0OpzTlstilGq0P4XmJwSKB4rKPiDLUusoOfd9WVFZHcKuOaZVC6fET-dG_4o7pKyHaqoOIMu0jA6g","first_name":"Кристина","last_name":"Белова","can_access_closed":true,"is_closed":false},{"id":400790625,"bdate":"1.5.1986","city":{"id":99,"title":"Новосибирск"},"blacklisted":0,"track_code":"10d5903bbn8WpIeOsk25xQk_ZWnug98gtSMloe7iYTkMB3_br5QJFlX_jLPiSrjCNa3ErySBty6zICWh4IQTUA","first_name":"Яна","last_name":"Гончарова","can_access_closed":true,"is_closed":false},{"id":417877132,"bdate":"3.6.1970","blacklisted":0,"track_code":"8a62e93f0sVE0k59z0G-XjFpv4zngN1AKulxSVLAUE9iV0kiqA21rAaCQETPRewHAPwZSyqCtU4s6nFJXKYiJg","first_name":"Ирина","last_name":"Родомакина","can_access_closed":true,"is_closed":false},{"id":323416007,"bdate":"8.8.1978","blacklisted":0,"track_code":"907ca90bxGr3ph9O9Dseo4aPL15fE_cmkkab_10CgFm69YtcGVmjA7LzEXbyPxiisBuImpcRnyiURZv_U2TyMA","first_name":"Виктория","last_name":"Иванова","can_access_closed":false,"is_closed":true},{"id":436528490,"bdate":"4.5.1978","city":{"id":99,"title":"Новосибирск"},"blacklisted":0,"track_code":"7c3b97daPz2NgeyUrPqGTnKn6sfLThf8F7egJ5VrCahudlKkXB1YVMyG56n-rIJNSD1JCgRMf_IRtKAnmw17wQ","first_name":"Вика","last_name":"Ларина","can_access_closed":false,"is_closed":true},{"id":433476343,"bdate":"25.4.1985","blacklisted":0,"track_code":"15e438cct3VHhLcG8-EeNn0XO12m5AzTPfMy3vUZhOfSJL6swL_QHFbV5j6lt08xQ4OfnWrmZN078DLe-3_2jg","first_name":"Кира","last_name":"Чудина","can_access_closed":true,"is_closed":false},{"id":397419005,"bdate":"8.11.1980","blacklisted":0,"track_code":"831e4513qQi3hhm4uz61Xvlk5yZCoV1iyCoLLlEaZsze1wnboYjOYaCERIaxZeRYwv9A4oijNWzOKQsuX3wUpQ","first_name":"Tanya","last_name":"Aronovich","can_access_closed":true,"is_closed":false}]}}'
        result = res.json().get('response').get('items') # формат [{'id': 488749963, 'bdate': '1.6.1980', 'blacklisted': 0, 'track_code': 'ab6e1d82rhEPr3d-cs63...7_Qs2v4Gjw', 'first_name': 'Юлия', 'last_name': 'Волкова', 'can_access_closed': True, 'is_closed': False}, {'id': 576362782, 'bdate': '25.10.1984', 'city': {...}, 'blacklisted': 0, 'track_code': 'c0bffc11N5qTfQJ63Zn1...CmTc6Dhe3A', 'first_name': 'Katy', 'last_name': 'Perry', 'can_access_closed': True, 'is_closed': False}, {'id': 402957890, 'bdate': '17.3.1986', 'blacklisted': 0, 'track_code': '4914399b-V44uFWrGyMg...M-GTiWzY_Q', 'first_name': 'Женя', 'last_name': 'Усова', 'can_access_closed': False, 'is_closed': True}, {'id': 574435155, 'bdate': '3.2.1984', 'blacklisted': 0, 'track_code': '127bbdc5u0OpzTlstilG...oOIMu0jA6g', 'first_name': 'Кристина', 'last_name': 'Белова', 'can_access_closed': True, 'is_closed': False}, {'id': 400790625, 'bdate': '1.5.1986', 'city': {...}, 'blacklisted': 0, 'track_code': '10d5903bbn8WpIeOsk25...ICWh4IQTUA', 'first_name': 'Яна', 'last_name': 'Гончарова', 'can_access_closed': True, 'is_closed': False}, {'id': 417877132, 'bdate': '3.6.1970', 'blacklisted': 0, 'track_code': '8a62e93f0sVE0k59z0G-...6nFJXKYiJg', 'first_name': 'Ирина', 'last_name': 'Родомакина', 'can_access_closed': True, 'is_closed': False}, {'id': 323416007, 'bdate': '8.8.1978', 'blacklisted': 0, 'track_code': '907ca90bxGr3ph9O9Dse...RZv_U2TyMA', 'first_name': 'Виктория', 'last_name': 'Иванова', 'can_access_closed': False, 'is_closed': True}, {'id': 436528490, 'bdate': '4.5.1978', 'city': {...}, 'blacklisted': 0, 'track_code': '7c3b97daPz2NgeyUrPqG...tKAnmw17wQ', 'first_name': 'Вика', 'last_name': 'Ларина', 'can_access_closed': False, 'is_closed': True}, {'id': 433476343, 'bdate': '25.4.1985', 'blacklisted': 0, 'track_code': '15e438cct3VHhLcG8-Ee...8DLe-3_2jg', 'first_name': 'Кира', 'last_name': 'Чудина', 'can_access_closed': True, 'is_closed': False}, {'id': 397419005, 'bdate': '8.11.1980', 'blacklisted': 0, 'track_code': '831e4513qQi3hhm4uz61...KQsuX3wUpQ', 'first_name': 'Tanya', 'last_name': 'Aronovich', 'can_access_closed': True, 'is_closed': False}]
        with open('data.json', 'w', encoding='utf-8') as file:
            json.dump(res.json(), file, ensure_ascii=False, indent=3)

        list_users = []
        for item in result:
            list_user = []
            if item.get('blacklisted') == 0 and item.get('is_closed') is False :
                list_user.append(item.get('id')) # формат [488749963]
                user_name = f"{item.get('first_name')} {item.get('last_name')}" # формат 'Юлия Волкова'
                list_user.append(user_name) # формат [488749963, 'Юлия Волкова']
                list_users.append(list_user) # формат [[488749963, 'Юлия Волкова'], ...]
        return list_users

    def get_users_photo(self, user_id):
        # формат user_id '488749963'

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
        headers = self.get_headers() # format {'Content-Type': 'application/json', 'Authorization': 'OAuth vk1.a.Y45795E4...nsUC3NqXDQ'}
        res1 = requests.get(url=url, params={**self.params, **params1}, headers=headers) # format <Response [200]> content: '{"response":{"count":1012,"items":[{"album_id":-7,"date":1526899792,"id":456239046,"owner_id":488749963,"can_comment":1,"sizes":[{"height":130,"type":"m","width":97,"url":"https:\\/\\/sun9-1.userapi.com\\/impf\\/dUxDPhYlGTIK_fQXW2APeNPc76sGwhFr2KdEAg\\/p8lU2Pz_CsE.jpg?size=97x130&quality=96&sign=4523b97bd3745b01f71d48aa475c3a06&c_uniq_tag=26i6HUYYFQn5ANZYe-q14-bXSIrc7kGHUvjf6ZodvlQ&type=album"},{"height":173,"type":"o","width":130,"url":"https:\\/\\/sun9-1.userapi.com\\/impf\\/dUxDPhYlGTIK_fQXW2APeNPc76sGwhFr2KdEAg\\/p8lU2Pz_CsE.jpg?size=130x173&quality=96&sign=e86a82008bf8076363b5ca8e5f8d4289&c_uniq_tag=azDo1TUF5op70MZG4nYldHsY995nsCK22zS_vTTl2_E&type=album"},{"height":267,"type":"p","width":200,"url":"https:\\/\\/sun9-1.userapi.com\\/impf\\/dUxDPhYlGTIK_fQXW2APeNPc76sGwhFr2KdEAg\\/p8lU2Pz_CsE.jpg?size=200x267&quality=96&sign=0addd0d6c7e3ab5c3bd8f538af40c198&c_uniq_tag=_c0zhlj8259iRZ2YfgSYZfFeR5LdtjpUTTz7tDePLrE&type=album"},{"height":427,"type":"q","width":320,"url":"https:\\/\\/sun9-1.userapi.com\\/impf\\/dUxDPhYlGTIK_fQXW2APeNPc76sGwhFr2KdEAg\\/p8lU2Pz_CsE.jpg?size=320x427&quality=96&sign=f758aba662597faa0d6b7579d5d2d927&c_uniq_tag=EpPRhAGVznbi_9jb8eKg7vRHuOPH9Q6Q-y30ElUmH5U&type=album"},{"height":680,"type":"r","width":510,"url":"https:\\/\\/sun9-1.userapi.com\\/impf\\/dUxDPhYlGTIK_fQXW2APeNPc76sGwhFr2KdEAg\\/p8lU2Pz_CsE.jpg?size=510x680&quality=96&sign=e2c550f1571aba90f95c80350b5b58cb&c_uniq_tag=kepYApS_npkunTWjG2f7PmMBOAtpVf8sOaKTetIzIrs&type=album"},{"height":75,"type":"s","width":56,"url":"https:\\/\\/sun9-1.userapi.com\\/impf\\/dUxDPhYlGTIK_fQXW2APeNPc76sGwhFr2KdEAg\\/p8lU2Pz_CsE.jpg?size=56x75&quality=96&sign=b19f63f4e396dd37dc6e2b9c2b32e805&c_uniq_tag=-kJESyZn0KozFFfgoEABx8NZEdCAA4hd1l0-B7iAfS0&type=album"},{"height":2160,"type":"w","width":1620,"url":"https:\\/\\/sun9-1.userapi.com\\/impf\\/dUxDPhYlGTIK_fQXW2APeNPc76sGwhFr2KdEAg\\/p8lU2Pz_CsE.jpg?size=1620x2160&quality=96&sign=b1a48f60a587986ae30c06c4b56b0b4c&c_uniq_tag=MbOh6EWd5vq5jLOoC725Ra9XsSPfpDyZ3kg34SnSSK8&type=album"},{"height":604,"type":"x","width":453,"url":"https:\\/\\/sun9-1.userapi.com\\/impf\\/dUxDPhYlGTIK_fQXW2APeNPc76sGwhFr2KdEAg\\/p8lU2Pz_CsE.jpg?size=453x604&quality=96&sign=ce979191defa21b891802c3f3fbe294c&c_uniq_tag=YWM0aJaLZHzT-RKwbG1hWkUaWSfBdpjtjwDTxLNE0Kc&type=album"},{"height":807,"type":"y","width":605,"url":"https:\\/\\/sun9-1.userapi.com\\/impf\\/dUxDPhYlGTIK_fQXW2APeNPc76sGwhFr2KdEAg\\/p8lU2Pz_CsE.jpg?size=605x807&quality=96&sign=c1edcba2ef41500d3cb137671c2cab88&c_uniq_tag=d7FLYEgIF-ihw0dGcy5C5vEj8FFq6YgP_C39xuIUebQ&type=album"},{"height":1080,"type":"z","width":810,"url":"https:\\/\\/sun9-1.userapi.com\\/impf\\/dUxDPhYlGTIK_fQXW2APeNPc76sGwhFr2KdEAg\\/p8lU2Pz_CsE.jpg?size=810x1080&quality=96&sign=ce7ad10e4f5391ce15d3256fc8a42ca9&c_uniq_tag=3INxWtah9LqitbXruWgMX7_F9Sx7c2GOrM935GDklgk&type=album"}],"text":"","has_tags":false,"likes":{"count":849,"user_likes":0},"comments":{"count":25},"reposts":{"count":0},"tags":{"count":0}}, ... ...
        res2 = requests.get(url=url, params={**self.params, **params2}, headers=headers) # format <Response [200]> content: '{"response":{"count":1,"items":[{"album_id":-6,"date":1526898727,"id":456239045,"owner_id":488749963,"can_comment":1,"post_id":5,"sizes":[{"height":130,"type":"m","width":97,"url":"https:\\/\\/sun1-89.userapi.com\\/impf\\/c844321\\/v844321090\\/5f0d2\\/DL1exc5mS4U.jpg?size=97x130&quality=96&sign=d376f274cc2e968ff827ebebcdff9428&c_uniq_tag=XOkh-ivCOQlMtXI2a9_QufZxBPRCQzk6AmdsYsP5WAU&type=album"},{"height":173,"type":"o","width":130,"url":"https:\\/\\/sun1-89.userapi.com\\/impf\\/c844321\\/v844321090\\/5f0d2\\/DL1exc5mS4U.jpg?size=130x173&quality=96&sign=04fcd531c2815b541e09d8c5517c09ac&c_uniq_tag=TUAsuENtSZWB43HuQMsuramx2nl9utOD-OSvZlwQkAQ&type=album"},{"height":267,"type":"p","width":200,"url":"https:\\/\\/sun1-89.userapi.com\\/impf\\/c844321\\/v844321090\\/5f0d2\\/DL1exc5mS4U.jpg?size=200x267&quality=96&sign=083853194b40638dc21d4828ab8b2a68&c_uniq_tag=hi08SI4r__rLkBGR2FaVSmDR23xE8LdIuGn22kl6NBg&type=album"},{"height":427,"type":"q","width":320,"url":"https:\\/\\/sun1-89.userapi.com\\/impf\\/c844321\\/v844321090\\/5f0d2\\/DL1exc5mS4U.jpg?size=320x427&quality=96&sign=0e09fc04896c42226c91a1c7aad4f83e&c_uniq_tag=pxFfTynJhz3vRikrVqPnuLF1FUmcTyE21YSZzJEq18g&type=album"},{"height":680,"type":"r","width":510,"url":"https:\\/\\/sun1-89.userapi.com\\/impf\\/c844321\\/v844321090\\/5f0d2\\/DL1exc5mS4U.jpg?size=510x680&quality=96&sign=5c367a71777160e23fef8b8137a69f4f&c_uniq_tag=zBojfWMxh-MkC7VCJ6UDodY-L73y9CvAzQG0iNtn_tA&type=album"},{"height":75,"type":"s","width":56,"url":"https:\\/\\/sun1-89.userapi.com\\/impf\\/c844321\\/v844321090\\/5f0d2\\/DL1exc5mS4U.jpg?size=56x75&quality=96&sign=263cd34ec08534cf5c20f1a6df15b33f&c_uniq_tag=2NVltDWuj_zn506YglVRxf7g95P6jOk69wWjD3LEK3M&type=album"},{"height":2160,"type":"w","width":1620,"url":"https:\\/\\/sun1-89.userapi.com\\/impf\\/c844321\\/v844321090\\/5f0d2\\/DL1exc5mS4U.jpg?size=1620x2160&quality=96&sign=ab6ff0f74f3c74fad45e0aad239f4e04&c_uniq_tag=H3wU4KdOUSHdO3Q3WpIVcEZOJfT2ej7AvTMZozsAPgY&type=album"},{"height":604,"type":"x","width":453,"url":"https:\\/\\/sun1-89.userapi.com\\/impf\\/c844321\\/v844321090\\/5f0d2\\/DL1exc5mS4U.jpg?size=453x604&quality=96&sign=4874c4567aa0b1dd5f219de57885974d&c_uniq_tag=oB12NoaIpYtsknUm6gOo3uqzDwOCV2WVQjJfymCLfys&type=album"},{"height":807,"type":"y","width":605,"url":"https:\\/\\/sun1-89.userapi.com\\/impf\\/c844321\\/v844321090\\/5f0d2\\/DL1exc5mS4U.jpg?size=605x807&quality=96&sign=9d00713f4192f36ce47c3361fe41f627&c_uniq_tag=PkeMs1q-A_f2Via62J4W5xLe3uTBSNxWVWiqnHoST50&type=album"},{"height":1080,"type":"z","width":810,"url":"https:\\/\\/sun1-89.userapi.com\\/impf\\/c844321\\/v844321090\\/5f0d2\\/DL1exc5mS4U.jpg?size=810x1080&quality=96&sign=7ad52fbc1a526d52c6f309e4132c3696&c_uniq_tag=89A5nG6lPjSYeMdcL8h3fTgsUOVwo-d9QnrL223BU1c&type=album"}],"square_crop":"85,573,1448","text":"","has_tags":false,"likes":{"count":2107,"user_likes":0},"comments":{"count":168},"reposts":{"count":5},"tags":{"count":0}}]}}'

        # with open('photo.json', 'w') as file:
        #      json.dump(res1.json(), file, ensure_ascii=False, indent=3)
        #      json.dump(res2.json(), file, ensure_ascii=False, indent=3)
        photos_info1 = res1.json().get('response').get('items') # format [{'album_id': -7, 'date': 1526899792, 'id': 456239046, 'owner_id': 488749963, 'can_comment': 1, 'sizes': [...], 'text': '', 'has_tags': False, 'likes': {...}, ...}, {'album_id': -7, 'date': 1526899796, 'id': 456239047, 'owner_id': 488749963, 'can_comment': 1, 'sizes': [...], 'text': '', 'has_tags': False, 'likes': {...}, ...}, {'album_id': -7, 'date': 1526899800, 'id': 456239048, 'owner_id': 488749963, 'can_comment': 1, 'sizes': [...], 'text': '', 'has_tags': False, 'likes': {...}, ...}, {'album_id': -7, 'date': 1526899803, 'id': 456239049, 'owner_id': 488749963, 'can_comment': 1, 'sizes': [...], 'text': '', 'has_tags': False, 'likes': {...}, ...}, {'album_id': -7, 'date': 1526899807, 'id': 456239050, 'owner_id': 488749963, 'can_comment': 1, 'sizes': [...], 'text': '', 'has_tags': False, 'likes': {...}, ...}, {'album_id': -7, 'date': 1526899810, 'id': 456239051, 'owner_id': 488749963, 'can_comment': 1, 'sizes': [...], 'text': '', 'has_tags': False, 'likes': {...}, ...}, {'album_id': -7, 'date': 1526899814, 'id': 456239052, 'owner_id': 488749963, 'can_comment': 1, 'sizes': [...], 'text': '', 'has_tags': False, 'likes': {...}, ...}, {'album_id': -7, 'date': 1526899818, 'id': 456239053, 'owner_id': 488749963, 'can_comment': 1, 'sizes': [...], 'text': '', 'has_tags': False, 'likes': {...}, ...}, {'album_id': -7, 'date': 1526899821, 'id': 456239054, 'owner_id': 488749963, 'can_comment': 1, 'sizes': [...], 'text': '', 'has_tags': False, 'likes': {...}, ...}, {'album_id': -7, 'date': 1526899825, 'id': 456239055, 'owner_id': 488749963, 'can_comment': 1, 'sizes': [...], 'text': '', 'has_tags': False, 'likes': {...}, ...}, {'album_id': -7, 'date': 1526900519, 'id': 456239056, 'owner_id': 488749963, 'can_comment': 1, 'sizes': [...], 'text': '', 'has_tags': False, 'likes': {...}, ...}, {'album_id': -7, 'date': 1526900523, 'id': 456239057, 'owner_id': 488749963, 'can_comment': 1, 'sizes': [...], 'text': '', 'has_tags': False, 'likes': {...}, ...}, {'album_id': -7, 'date': 1526900526, 'id': 456239058, 'owner_id': 488749963, 'can_comment': 1, 'sizes': [...], 'text': '', 'has_tags': False, 'likes': {...}, ...}, {'album_id': -7, 'date': 1526900530, 'id': 456239059, 'owner_id': 488749963, 'can_comment': 1, 'sizes': [...], 'text': '', 'has_tags': False, 'likes': {...}, ...}, ...]
        photos_info2 = res2.json().get('response').get('items') # format [{'album_id': -6, 'date': 1526898727, 'id': 456239045, 'owner_id': 488749963, 'can_comment': 1, 'post_id': 5, 'sizes': [...], 'square_crop': '85,573,1448', 'text': '', ...}]
        # берем фото из запроса по фото с профиля и по  фото со стены
        photos_info = photos_info1 + photos_info2 # format [{'album_id': -7, 'date': 1526899792, 'id': 456239046, 'owner_id': 488749963, 'can_comment': 1, 'sizes': [...], 'text': '', 'has_tags': False, 'likes': {...}, ...}, {'album_id': -7, 'date': 1526899796, 'id': 456239047, 'owner_id': 488749963, 'can_comment': 1, 'sizes': [...], 'text': '', 'has_tags': False, 'likes': {...}, ...}, {'album_id': -7, 'date': 1526899800, 'id': 456239048, 'owner_id': 488749963, 'can_comment': 1, 'sizes': [...], 'text': '', 'has_tags': False, 'likes': {...}, ...}, {'album_id': -7, 'date': 1526899803, 'id': 456239049, 'owner_id': 488749963, 'can_comment': 1, 'sizes': [...], 'text': '', 'has_tags': False, 'likes': {...}, ...}, {'album_id': -7, 'date': 1526899807, 'id': 456239050, 'owner_id': 488749963, 'can_comment': 1, 'sizes': [...], 'text': '', 'has_tags': False, 'likes': {...}, ...}, {'album_id': -7, 'date': 1526899810, 'id': 456239051, 'owner_id': 488749963, 'can_comment': 1, 'sizes': [...], 'text': '', 'has_tags': False, 'likes': {...}, ...}, {'album_id': -7, 'date': 1526899814, 'id': 456239052, 'owner_id': 488749963, 'can_comment': 1, 'sizes': [...], 'text': '', 'has_tags': False, 'likes': {...}, ...}, {'album_id': -7, 'date': 1526899818, 'id': 456239053, 'owner_id': 488749963, 'can_comment': 1, 'sizes': [...], 'text': '', 'has_tags': False, 'likes': {...}, ...}, {'album_id': -7, 'date': 1526899821, 'id': 456239054, 'owner_id': 488749963, 'can_comment': 1, 'sizes': [...], 'text': '', 'has_tags': False, 'likes': {...}, ...}, {'album_id': -7, 'date': 1526899825, 'id': 456239055, 'owner_id': 488749963, 'can_comment': 1, 'sizes': [...], 'text': '', 'has_tags': False, 'likes': {...}, ...}, {'album_id': -7, 'date': 1526900519, 'id': 456239056, 'owner_id': 488749963, 'can_comment': 1, 'sizes': [...], 'text': '', 'has_tags': False, 'likes': {...}, ...}, {'album_id': -7, 'date': 1526900523, 'id': 456239057, 'owner_id': 488749963, 'can_comment': 1, 'sizes': [...], 'text': '', 'has_tags': False, 'likes': {...}, ...}, {'album_id': -7, 'date': 1526900526, 'id': 456239058, 'owner_id': 488749963, 'can_comment': 1, 'sizes': [...], 'text': '', 'has_tags': False, 'likes': {...}, ...}, {'album_id': -7, 'date': 1526900530, 'id': 456239059, 'owner_id': 488749963, 'can_comment': 1, 'sizes': [...], 'text': '', 'has_tags': False, 'likes': {...}, ...}, ...]

        if len(photos_info) < 3 or photos_info is None:
            return None

        dict_likes = {'count': [], 'href': [], 'owner_id': ""}
        dict_likes_max = {'href': [], 'owner_id': ""}

        for photo in photos_info:
            dict_likes['count'].append(photo.get('likes').get('count')) # format {'count': [849], 'href': ['https://sun9-1.usera...type=album'], 'owner_id': ''}
            dict_likes['href'].append(photo.get('sizes')[-1].get('url'))
            dict_likes['owner_id'] = str(photo.get('owner_id'))
            # format {'count': [849, 858, 272, 341, 316, 214, 304, 253], 'href': ['https://sun9-1.usera...type=album', 'https://sun9-64.user...type=album', 'https://sun9-75.user...type=album', 'https://sun9-80.user...type=album', 'https://sun9-9.usera...type=album', 'https://sun9-9.usera...type=album', 'https://sun9-80.user...type=album', 'https://sun9-61.user...type=album'], 'owner_id': '488749963'}


        while len(dict_likes_max.get("href")) < 3:

            max_like = max(dict_likes.get('count')) # format 2107
            index = dict_likes.get('count').index(max_like) # format 30

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
        res = requests.get(url=url,  params={**self.params, **params}, headers=headers) # формат <Response [200]>  '{"response":{"count":3,"items":[{"id":99,"title":"Новосибирск","country":"Новосибирская область"}]}}'
        city_id = res.json().get('response').get('items')[0].get('id') # формат 99
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



