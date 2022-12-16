import base
import json
import bot_vkontakte as bot
from token_vk import token_vk, sql_authorization
from vk_api.longpoll import VkEventType
from requests_to_vk import RequestsVk
import pprint



def main():

    # Основной цикл
    list_of_users = []
    list_of_dicts = []

    # Создание объекта для подключения к базе данных
    sql_cursor = base.PostgreSQL(**sql_authorization)
    cur = sql_cursor.connect.cursor()

    # Создание объекта для осуществления request запросов
    response = RequestsVk(token_vk)

    longpoll, session, vk = bot.connection()
    print(base.drop_table(cur)) #если нужно сбросить БД
    print(base.create_db(cur))

    for event in longpoll.listen():
        
        # Если пришло новое сообщение
        if event.type == VkEventType.MESSAGE_NEW:
            
            # Выставляем параметры для пользователя написавшего сообщение
            result = bot.user_support(event, list_of_users, list_of_dicts)
            variables = result[0]
            list_of_users = result[1]
            list_of_dicts = result[2]
                        
            base.checking_the_user_in_the_database(cur, variables['id'], response)

            if event.text.lower().strip() == 'привет':
                ask_user = base.the_command_to_greet(cur, variables['id'], vk)

            elif event.text.lower().strip() in ['список']:
                if base.checking_the_favorites_list(cur, variables['id'], vk):
                    continue

            elif event.text.lower().strip() in ['поиск']:
                base.search_function(cur, variables['id'], vk, ask_user, session, longpoll)

            elif event.text.lower().strip() in ['Смотреть данные']:

                if base.check_find_user(cur, ask_user[0]):
                    counter = base.add_to_database(cur, variables['id'], result)
                else:
                    print('Данных нет')
                    bot.write_msg(vk, variables['id'], "Данных нет. Выполнить поиск")

            elif event.text.lower().strip() in ['Добавить в список избранных']:

                if base.add_favourites(cur, counter - 1, 1):
                    # sql_cursor.commit()
                    print('Добавлено в избранное')
                    bot.write_msg(vk, variables['id'], "Добавлен в список избранных")

            elif event.text.lower().strip() in ['Добавить в черный список']:

                if base.add_favourites(cur, counter - 1, 2):
                    # sql_cursor.commit()
                    print('Добавлено в чёрный список')
                    bot.write_msg(vk, variables['id'], "Добавлен в чёрный список")

            # else:
            #     bot.write_msg(vk, variables['id'], "Ошибка")

            # Пользователь отправил сообщение или нажал кнопку для бота(бот вк)
            if event.to_me:
                message_text = event.text.lower().strip()
                if variables['fields']['start']:

                    # Активирована команда старт (поиск людей)
                    variables['fields'] = bot.event_handling_start(vk, message_text, variables)
                    if variables['fields']['continue']:
                        variables['fields']['continue'] = False
                        continue
                    else:
                        # Запросы на фото для пользователя
                        respone = response.users_info(**variables['fields']['filtr_dict'])
                        # print(respone)
                        # with open('respone.json', 'w', encoding='utf-8') as file:
                        #     json.dump(respone, file, ensure_ascii=False, indent=3)      
                        attachment = bot.add_photos(vk, respone[0]['link_photo'])
                        bot.send_photos(vk, variables['id'], attachment)
                        attachment = bot.add_photos(vk, respone[1]['link_photo'])
                        bot.send_photos(vk, variables['id'], attachment) # тест на загрузку двух найденных профилей
                        variables['fields']['filtr_dict'] = {}
                else:
                    # Логика обычного ответа
                    variables['fields'] = bot.processing_a_simple_message(vk, message_text, variables)


if __name__ == '__main__':
    main()
            