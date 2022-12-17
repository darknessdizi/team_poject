import base
import bot_vkontakte as bot
from datetime import date
import psycopg2


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

        result = self.session.users.search(count=1000, blacklisted_by_me=0, fields=['photo_id', 'sex', 'bdate', 'city',
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
        for black_user in search_users_dict:
            if not black_user['is_closed']:
                print('. ', end="")
                attachment = self._find_photo(black_user['id'])
                find_users.append({'user_name': f"{black_user['first_name']} {black_user['first_name']}" ,
                                   'url': f"https://vk.com/id{black_user['id']}",
                                   'attachment': attachment, 'id': black_user['id']})

        print("\nПоиск фото окончен, данные сформированы")
        return find_users


    def calculate_age(self, born):  ### добавила self
        born = born.split(".")
        today = date.today()
        return today.year - int(born[2]) - ((today.month, today.day) < (int(born[1]), int(born[0])))


    def add_to_database(cur, sender_id, result):

        '''Пишет полученные данные из поиска в базу данных'''
        for i_user in result:
            if not base.check_find_user(cur, i_user['id']):
                if base.add_find_users(cur, i_user['id'], sender_id, i_user['user_name'], i_user['url']):
                    for item in i_user['attachment']:
                        base.add_find_users_photos(cur, i_user['id'], item)
        return True


    def checking_the_user_in_the_database(self, cur, sender_id, response): ### добавила self

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

    def the_command_to_greet(cur, sender_id: str, object_vk_api: object):

        '''Функция отвечает на приветствие пользователя'''

        ask_user = base.get_ask_user_data(cur, sender_id)
        print(f'Пользователь = {ask_user}')

        ask_user = base.get_ask_user_data(cur, sender_id)
        bot.write_msg(object_vk_api, sender_id, f"Здравствуйте, {ask_user[1]}!\n"
                                                f"Ваши параметры:\nГород: {ask_user[3]}\n"
                                                f"Пол: {ask_user[4]}\nВозраст: {ask_user[2]}\n"
                                                f"(Введите: старт\список) \U0001F60E")
        return ask_user

    def data_conversion(db_source):

        '''Преобразует данные из базы данных для бота '''
        users = list()
        for item in db_source:
            users.append({'id': item[0], 'name': f'{item[1]} {item[2]}', 'url': item[3]})
        return users

    def checking_the_favorites_list(cur, sender_id: str, object_vk_api: object):
        if base.get_favourites(cur, sender_id):
            db_source = base.get_favourites(cur, sender_id)
            favourites = base.data_conversion(db_source)
            for item in favourites:
                bot.write_msg(object_vk_api, sender_id, f"{item['name']}\n{item['url']}")
                bot.write_msg(object_vk_api, sender_id, "Просмотреть данные")
        else:
            bot.write_msg(object_vk_api, sender_id, f"Список избранных пуст")
            return True
        return False

    def search_function(cur, sender_id: str, object_vk_api: object, ask_user, session, longpoll):
        if base.get_favourites(cur, sender_id):
            bot.write_msg(object_vk_api, sender_id, f"Поиск...")

            v_kinder = VKinder(longpoll, session)
            result = v_kinder.find_user(ask_user)

            if base.add_to_database(cur, ask_user[0], result):
                print('Добавлено в базу')
                bot.write_msg(object_vk_api, sender_id, "Данные записаны в базу")
            else:
                print('Ошибка')
        else:
            bot.write_msg(object_vk_api, sender_id, "Смотреть данные")
