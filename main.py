import base
import json
import bot_vkontakte as bot
from token_vk import token_vk, sql_authorization
from vk_api.longpoll import VkEventType
from requests_to_vk import RequestsVk
from VKinder import VKinder, PostgreSQL
import time


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

    #print(base.drop_table(cur)) #если нужно сбросить БД
    print(base.create_db(cur))

    for event in longpoll.listen():

        # Если пришло новое сообщение
        if event.type == VkEventType.MESSAGE_NEW:

            # Выставляем параметры для пользователя написавшего сообщение
            result = bot.user_support(event, list_of_users, list_of_dicts) # format ({'id': 33579332, 'fields': {...}}, [33579332], [{...}])           ---       {'id': 33579332, 'fields': {'text': None, 'count': 0, 'start': False, 'continue': False, 'filtr_dict': {...}, 'sql': {}, 'start_request': False, 'number': 0}}     ----         [33579332]      ---       [{'id': 33579332, 'fields': {...}}]  

            variables = result[0] # формат {'id': 33579332, 'fields': {'text': None, 'count': 3, 'start': True, 'continue': False, 'filtr_dict': {...}, 'sql': {}, 'start_request': False, 'number': 0}}
            list_of_users = result[1] # формат [33579332, 45686545]
            list_of_dicts = result[2] # формат [{'id': 33579332, 'fields': {...}}]

            small.checking_the_user_in_the_database(cur, variables['id'], response)

            # Пользователь отправил сообщение или нажал кнопку для бота(бот вк)
            if event.to_me:
                message_text = event.text.lower().strip()
                if variables['fields']['start']:
                    # Активирована команда старт (поиск людей)
                    variables['fields'] = bot.event_handling_start(vk, message_text, variables)
                    if variables['fields']['continue']: # формат {'id': 33579332, 'fields': {'text': None, 'count': 0, 'start': False, 'continue': False, 'filtr_dict': {...}, 'sql': {}, 'start_request': False, 'number': 0}}
                        variables['fields']['continue'] = False
                        continue
                    else:
                        # Запросы на фото для пользователя
                        number = 0
                        # список пользователей которые находим по параметрам
                        # список вида [int(id), str(user_name)]
                        # variables['fields']['filtr_dict'] = {'age': ['34', '57'], 'sex': '1', 'city': 'новосибирск'}

                        respone = response.get_users(variables['fields']['filtr_dict']) # формат [[488749963, 'Юлия Волкова'], [576362782, 'Katy Perry'], [574435155, 'Кристина Белова'], [400790625, 'Яна Гончарова'], [417877132, 'Ирина Родомакина'], [433476343, 'Кира Чудина'], [397419005, 'Tanya Aronovich']]
                        if respone is None:
                            bot.write_msg(vk, variables['id'], "Ничего не найдено. Уточните параметры поиска")
                            variables['fields']['filtr_dict'] = {}
                        elif len(respone) == 0:
                            bot.write_msg(vk, variables['id'], "Простите, людей не найдено")
                            variables['fields']['filtr_dict'] = {}
                        else:
                            # возвращает фото в словаре вида {'href': [], 'owner_id': ""}
                            photos = response.get_users_photo(str(respone[number][0])) # format {'href': ['https://sun1-89.user...type=album', 'https://sun9-64.user...type=album', 'https://sun9-1.usera...type=album'], 'owner_id': ''}
                            
                            if photos is None:
#### тут бот останавливается на передаче дальнейшей отправке. просмотр дальше будет если нажать на кнопку следующий/
#### значит тут какую то логику действия бота надо прикрутитьн, чтобы он переходил опять на строчку 86 кода
                                keyboard = bot.create_buttons(1)
                                bot.write_msg(vk, variables['id'], "\U000026D4 \U0001F6AB У пользователя нет фотографий.\nНажмите следующий. \U0001F914", keyboard)
                                continue
                            
                            message = f"{respone[number][1]}\n https://vk.com/id{photos.get('owner_id')}"
                            bot.write_msg(vk, variables['id'], message) # format 'Юлия Волкова\n https://vk.com/id'

                            attachment = bot.add_photos(vk, photos.get('href')) # format ['photo-217703779_457239656', 'photo-217703779_457239657', 'photo-217703779_457239658']
                            bot.send_photos(vk, variables['id'], attachment)
                            keyboard = bot.create_buttons(4)
                            bot.write_msg(vk, variables['id'], "Выполнено \U00002705", keyboard)
                else:
                    # Логика обычного ответа
                    if message_text == 'привет':
                        small.the_command_to_greet(cur, variables['id'], vk)
                    
                    elif message_text in ['список', 'показать весь список']:
                        if small.checking_the_favorites_list(cur, variables['id'], vk):
                            continue

                    elif message_text in ['следующий']:
                        keyboard = bot.create_buttons(4)
                        bot.write_msg(vk, variables['id'], "Подождите. Сейчас загружаю фотографии. \U0001F609", keyboard)
                        number += 1
                        if len(respone)-1 == number:
                            bot.write_msg(vk, variables['id'], "Больше никого нет. \U0001F605")
                            variables['fields']['filtr_dict'] = {}
                            continue
                        else:
                            # time.sleep(2)
                            photos = response.get_users_photo(str(respone[number][0]))
                            if photos is None:
#### тут бот останавливается на передаче дальнейшей отправке. просмотр дальше будет если нажать на кнопку следующий/
#### значит тут какую то логику действия бота надо прикрутитьн, чтобы он переходил опять на строчку 86 кода
                                keyboard = bot.create_buttons(1)
                                bot.write_msg(vk, variables['id'], "\n\U000026D4 \U0001F6AB У пользователя нет фотографий.\nНажмите следующий. \U0001F914", keyboard)
                                continue
                            
                            message = f"{respone[number][1]}\n https://vk.com/id{photos.get('owner_id')}"
                            bot.write_msg(vk, variables['id'], message) # format 'Юлия Волкова\n https://vk.com/id'
                            attachment = bot.add_photos(vk, photos.get('href'))
                            bot.send_photos(vk, variables['id'], attachment)

                    # elif message_text in ['поиск']:
                    #     VKinder.search_function(cur, variables['id'], vk, ask_user, session, longpoll)

                    # elif message_text in ['смотреть данные']:

                    #     if small.check_find_user(cur, ask_user[0]):   # здесь ошибка type object 'VKinder' has no attribute 'check_find_user'
                    #         counter = VKinder.add_to_database(cur, variables['id'], result)
                    #     else:
                    #         print('Данных нет')
                    #         bot.write_msg(vk, variables['id'], "Данных нет. Выполнить поиск")

                    elif message_text in ['добавить в избранное']:
                        favorites_id = base.add_favourites(
                                                cur, variables['id'], # format {'id': 33579332, 'fields': {'text': None, 'count': 0, 'start': False, 'continue': False, 'filtr_dict': {...}, 'sql': {}, 'start_request': False, 'number': 0}}
                                                *respone[number], # format [[488749963, 'Юлия Волкова'], [576362782, 'Katy Perry'], [574435155, 'Кристина Белова'], [400790625, 'Яна Гончарова'], [417877132, 'Ирина Родомакина'], [433476343, 'Кира Чудина'], [397419005, 'Tanya Aronovich']]
                                                variables['fields']['filtr_dict'].get('sex'), variables['fields']['filtr_dict'].get('city'))
                        base.add_photos(cur, photos['href'], favorites_id)                        

                    elif message_text in ['добавить в черный список']:
                        favorites_id = base.add_favourites(
                                                cur, variables['id'], 
                                                *respone[number], 
                                                variables['fields']['filtr_dict'].get('sex'), variables['fields']['filtr_dict'].get('city'))
                        base.add_photos(cur, photos['href'], favorites_id)
                        base.black_list(cur, favorites_id)

                    variables['fields'] = bot.processing_a_simple_message(vk, message_text, variables)


if __name__ == '__main__':
    main()
            