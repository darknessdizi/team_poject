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


    def calculate_age(self, born):  

        born = born.split(".")
        today = date.today()
        return today.year - int(born[2]) - ((today.month, today.day) < (int(born[1]), int(born[0])))


    def checking_the_user_in_the_database(self, cur, sender_id, response): 

        if not base.get_ask_user_data(cur, sender_id):
            print('В базе отсутствует')
            user_info = response.get_user(sender_id)
            user_info['age'] = self.calculate_age(user_info['age'])  
            if user_info['sex'] == 2:
                user_info['gender'] = 'Мужской'
            elif user_info['sex'] == 1:
                user_info['gender'] = 'Женский'
            else:
                user_info['gender'] = 'Пол не указан'
            if base.add_ask_user(cur, sender_id, user_info['user_name'],
                            user_info['age'], user_info['city'],
                            user_info['gender']):
                print('Пользователь добавлен в базу')
            else:
                print('Пользователь НЕ добавлен в базу')


    def the_command_to_greet(self, cur, sender_id: str, object_vk_api: object):

        '''Функция отвечает на приветствие пользователя'''

        ask_user = base.get_ask_user_data(cur, sender_id)
        bot.write_msg(object_vk_api, sender_id, f"Здравствуйте, {ask_user[1]}!\n"
                                                f"Ваши параметры:\nГород: {ask_user[3]}\n"
                                                f"Пол: {ask_user[4]}\nВозраст: {ask_user[2]}\n"
                                                f"(Введите: старт\список) \U0001F60E")
        return ask_user


    def checking_the_favorites_list(self, cur, sender_id: str, object_vk_api: object):
        db_source = base.get_favourites(cur, sender_id) # format [('Марианна Иванова', '18.1.2000', 'волгоград', 'https://vk.com/id629503475'), ('Аза Кузинкова', '2.12.2002', 'волгоград', 'https://vk.com/id695107067'), ('Galina Abramova', '3.3.1993', 'волгоград', 'https://vk.com/id610224605'), ('Луиза Аннакулова', '18.8.1995', 'волгоград', 'https://vk.com/id706108662')]
        if db_source:
            for item in db_source:
                age = self.calculate_age(item[1])
                city = item[2].upper()
                message_text = f'Имя: {item[0]}\nВозраст: {age}\nГород: {city}\n{item[3]}'
                bot.write_msg(object_vk_api, sender_id, message_text)
        else:
            bot.write_msg(object_vk_api, sender_id, f"Список избранных пуст")
        bot.write_msg(object_vk_api, sender_id, "Выполнено \U00002705")
        return True


if __name__ == '__main__':
    pass
