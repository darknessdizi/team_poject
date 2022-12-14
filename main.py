import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import psycopg2
import base
from login_sql import sql_authorization
from token_vk import token_vk_community
import bot_vkontakte as bot

    
def main():

    # Основной цикл
    variables = {'count': 0, 'start': False, 'continue': False, 'filtr_dict': {}, 'sql': {}}

    # Создание объекта для подключения к базе данных
    sql_cursor = PostgreSQL(**sql_authorization)
    # base.drop_table(sql_cursor.connect.cursor())
    base.create_db(sql_cursor.connect.cursor())


    for event in longpoll.listen():

        # Если пришло новое сообщение
        if event.type == VkEventType.MESSAGE_NEW:
        
            # Если оно имеет метку для меня(то есть бота)
            if event.to_me:

                request = event.text.lower().strip()
                if variables['start']:
                    # Активирована команда старт (поиск людей)
                    variables = bot.event_handling_start(vk, request, event, variables)
                    if variables['continue']:
                        variables['continue'] = False
                        continue
                else:
                    # Логика обычного ответа
                    variables = bot.processing_a_simple_message(vk, request, event, variables)


class PostgreSQL:

    def __init__(self, **kwargs):
        self.connect = psycopg2.connect(
            dbname=kwargs['dbname'],
            user=kwargs['user'],
            password=kwargs['password']
        )
        self.connect.autocommit = True
                    

# Авторизуемся как сообщество
vk = vk_api.VkApi(token=token_vk_community)

# Работа с сообщениями
longpoll = VkLongPoll(vk)


if __name__ == '__main__':
    main()
            