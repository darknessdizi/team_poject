import base
import json
import bot_vkontakte as bot
from token_vk import token_vk, sql_authorization
from vk_api.longpoll import VkEventType
from requests_to_vk import RequestsVk
from VKinder import VKinder, PostgreSQL
import pprint

def main():

    # Основной цикл
    list_of_users = []
    list_of_dicts = []

    # Создание объекта для подключения к базе данных
    sql_cursor = PostgreSQL(**sql_authorization)
    cur = sql_cursor.connect.cursor()

    # Создание объекта для осуществления request запросов
    response = RequestsVk(token_vk)

    longpoll, session, vk = bot.connection()

    small = VKinder(longpoll, session)

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

            small.checking_the_user_in_the_database(cur, variables['id'], response)

            print('point 1')

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
                        attachment = bot.add_photos(vk, respone[0]['link_photo'])
                        bot.send_photos(vk, variables['id'], attachment)
                        variables['fields']['filtr_dict'] = {}


                        # # Запросы на фото для пользователя
                        # print(variables['fields']['filtr_dict'])
                        # list_of_users = response.get_users(**variables['fields']['filtr_dict'])

                        # kursor = 0
                        # len_list = len(list_of_users)
                        # #  если пользователь запрашивает еще фото
                        # message_text = event.text
                        # #while message_text == 'еще':
                        # photos, kursor = response.get_photo_from_iterator(list_of_users[kursor:], len_list, kursor)
                        # print(photos)

                        #     #### здесь отправляем фото и предлагаем сохранить  в избранное
                        # attachment = bot.add_photos(vk, photos.get('href'))
                        # message = f"{photos.get('user_name')}\n {photos.get('user_link')}"
                        # bot.write_msg(vk, variables['id'], message)
                        #     # отправка фото
                        # bot.send_photos(vk, variables['id'], attachment)
                        #     # отправка сообщения с сылкой на профилем и именем
                        # message = f"{photos.get('user_name')}\n {photos.get('user_link')}"
                        # bot.write_msg(vk, variables['id'], message)

                        #     # if photos is None:
                        #     #     continue
                        #     # print(photos)
                        #     # kursor += 1
                        #     # # запрашиваем будет ли еще смотреть
                        #     # bot.write_msg(vk, variables['id'], "Еще фото?")
                        #     # message_text = event.text # или нажата кнопка еще
                        #     #
                        #     # if kursor == len(list_of_users) - 1:
                        #     #     print('поиск завершен')
                        #     #     break
                        #     # if message_text == 'нет':
                        #     #     break

                        # #attachment = bot.add_photos(vk, respone[1].['link_photo'])
                        # #bot.send_photos(vk, variables['id'], attachment) # тест на загрузку двух найденных профилей
                        # variables['fields']['filtr_dict'] = {}
                else:
                    # Логика обычного ответа
                    if message_text == 'привет':
                        ask_user = small.the_command_to_greet(cur, variables['id'], vk)
                        print('point 2')
                    
                    elif message_text in ['список']:
                        if small.checking_the_favorites_list(cur, variables['id'], vk):
                            continue

                    elif message_text in ['поиск']:
                        VKinder.search_function(cur, variables['id'], vk, ask_user, session, longpoll)

                    elif message_text in ['смотреть данные']:

                        if small.check_find_user(cur, ask_user[0]):   # здесь ошибка type object 'VKinder' has no attribute 'check_find_user'
                            counter = VKinder.add_to_database(cur, variables['id'], result)
                        else:
                            print('Данных нет')
                            bot.write_msg(vk, variables['id'], "Данных нет. Выполнить поиск")

                    elif message_text in ['добавить в список избранных']:

                        if VKinder.add_favourites(cur, counter - 1, 1):  # здесь ошибка type object 'VKinder' has no attribute 'add_favourites'

                            print('Добавлено в избранное')
                            bot.write_msg(vk, variables['id'], "Добавлен в список избранных")

                    elif message_text in ['добавить в черный список']:

                        if VKinder.add_favourites(cur, counter - 1, 2):  # здесь ошибка type object 'VKinder' has no attribute 'add_favourites'

                            print('Добавлено в чёрный список')
                            bot.write_msg(vk, variables['id'], "Добавлен в чёрный список")

                    variables['fields'] = bot.processing_a_simple_message(vk, message_text, variables)


if __name__ == '__main__':
    main()
            