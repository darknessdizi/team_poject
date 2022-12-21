import base
import bot_vkontakte as bot
from datetime import date
import psycopg2
import requests

class PostgreSQL:

    def __init__(self, **kwargs):
        self.connect = psycopg2.connect(
            dbname=kwargs['dbname'],
            user=kwargs['user'],
            password=kwargs['password']
        )
        self.connect.autocommit = True



class VKinder:

    def __init__(self, longpoll, session):
        self.longpoll = longpoll
        self.session = session


    def _search(self, user_param):

        '''первоначальный поиск'''
        if user_param[4] == 'Мужской':
            sex = 1
        elif user_param[4] == 'Женский':
            sex = 2
        else:
            sex = 0

        result = self.session.users.search(count=1000, blacklisted_by_me=0, fields=['photo_id', 'name', 'age', 'sex', 'city',
                                                                                  'is_closed'],
                                           city=user_param[3], sex=sex,
                                           age_from=user_param[3], age_to=user_param[2], has_photo=1,)['items']
        print('Выполнен первоначальный поиск')
        return result



    def _find_photo(self, user_id):

        '''подбираем фото'''
        get_photo = self.session.photos.get(owner_id=user_id, album_id='profile', extended=1, photo_sizes=1)['items']
        photo_list = sorted(get_photo, key=lambda k: k['likes']['count'], reverse=True)
        if len(photo_list) > 3:
            photo_list = photo_list[:3]
        attachment_list = list()
        for item in photo_list:
            attachment_list.append(f'photo{user_id}_{item["id"]}')
        return attachment_list



    def find_user(self, user_param):

        '''выборка по параметрам'''
        search_users_dict = self._search(user_param)
        find_users = list()
        print("Ищем фото, формируем данные")
        for user in search_users_dict:
            if not user['is_closed']:
                print('. ', end="")
                attachment = self._find_photo(user['id'])
                find_users.append({'user_name': f"{user['user_name']} " ,
                                   'url': f"https://vk.com/id{user['id']}",
                                   'attachment': attachment, 'id': user['id']})

        print("\nПоиск фото окончен, данные сформированы")
        return find_users


    def calculate_age(self, born):  ### добавила self

        born = born.split(".")
        today = date.today()
        return today.year - int(born[2]) - ((today.month, today.day) < (int(born[1]), int(born[0])))


    def add_to_database(cur, sender_id, result):

        '''Пишет полученные данные из поиска в базу данных'''
        for i_user in result:
            if not base.add_find_users(cur, i_user['id']):
                if base.add_find_users(cur, i_user['id'], sender_id, i_user['user_name'], i_user['url']):
                    for item in i_user['attachment']:
                        base.add_find_users_photos(cur, i_user['id'], item)
        return True


    def checking_the_user_in_the_database(self, cur, sender_id, response): ### добавила self
        # format  cur: <cursor object at 0x0000025CC1D4D580; closed: 0>
        # format  sender_id: 33579332
        # format  response: <requests_to_vk.RequestsVk object at 0x0000025CC1A1F670>

        if not base.get_ask_user_data(cur, sender_id):
            print('в базе отсутствует')
            user_info = response.get_user(sender_id)
            user_info['age'] = self.calculate_age(user_info['age'])  ## изменила было  base.calculate()
            if user_info['sex'] == 2:
                user_info['gender'] = 'Мужской'
            elif user_info['sex'] == 1:
                user_info['gender'] = 'Женский'
            else:
                user_info['gender'] = 'Пол не указан'
            if base.add_ask_user(cur, sender_id, user_info['user_name'],
                            user_info['age'], user_info['city'],
                            user_info['gender']):
                print('пользователь добавлен в базу')
            else:
                print('пользователь НЕ добавлен в базу')

    def the_command_to_greet(self, cur, sender_id: str, object_vk_api: object):

        '''Функция отвечает на приветствие пользователя'''

        ask_user = base.get_ask_user_data(cur, sender_id)
        print(f'Пользователь = {ask_user}')

        ask_user = base.get_ask_user_data(cur, sender_id)
        bot.write_msg(object_vk_api, sender_id, f"Здравствуйте, {ask_user[1]}!\n"
                                                f"Ваши параметры:\nГород: {ask_user[3]}\n"
                                                f"Пол: {ask_user[4]}\nВозраст: {ask_user[2]}\n"
                                                f"(Введите: старт\список) \U0001F60E")
        return ask_user

    def data_conversion(sender_id, cur):

        '''Преобразует данные из базы данных для бота '''
        users = list()
        for item in sender_id:
            users.append({'id': item[0], 'name': f'{item[1]} {item[2]}', 'url': item[3]})
        return users


    def checking_the_favorites_list(self, cur, sender_id: str, object_vk_api: object):
        db_source = base.get_favourites(cur)
        print(db_source)
        if db_source:
            for item in db_source:
                message_text = f'Имя: {item[0]}\nДата рождения: {item[1]}\nГород: {item[2]}'
                bot.write_msg(object_vk_api, sender_id, message_text)
        else:
            bot.write_msg(object_vk_api, sender_id, f"Список избранных пуст")
        bot.write_msg(object_vk_api, sender_id, "Выполнено \U00002705")
        return True

    def search_function(cur, sender_id: str, object_vk_api: object, ask_user, session, longpoll):
        if base.get_favourites(cur, sender_id):
            bot.write_msg(object_vk_api, sender_id, f"Поиск...")

            v_kinder = VKinder(longpoll, session)
            result = v_kinder.find_user(ask_user)

            if base.add_find_users(cur, ask_user[0], result):
                print('Добавлено в базу')
                bot.write_msg(object_vk_api, sender_id, "Данные записаны в базу")
            else:
                print('Ошибка')
        else:
            bot.write_msg(object_vk_api, sender_id, "Смотреть данные")



    def request_black_users(self, user_id):

        # удаление из поиска пользователей  находяшихся в черном списке
        self.black_list = []
        self.id_users = []
        for user_id in self.black_list:
            url = 'https://api.vk.com/method/users.get'
            params = {"user_ids": user_id, "fields": "black_list"}
            response = requests.get(url=url, params=params)
            link_load = response.json()
            for link in link_load['response']:
               if link['black_list'] == 0:
                 self.id_users.append(link['user_id'])

