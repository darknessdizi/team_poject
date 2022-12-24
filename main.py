import base
import bot_vkontakte as bot
from token_vk import token_vk, sql_authorization
from vk_api.longpoll import VkEventType
from requests_to_vk import RequestsVk
from VKinder import VKinder, PostgreSQL


def photo_requests_for_users(vk, response, cur, variables):

    respone = response.get_users(variables['fields']) # формат respone [[488749963, 'Юлия Волкова', '20.11.1999'], [576362782, 'Katy Perry'], [574435155, 'Кристина Белова'], [400790625, 'Яна Гончарова'], [417877132, 'Ирина Родомакина'], [433476343, 'Кира Чудина'], [397419005, 'Tanya Aronovich']]
    block_list = [i[4] for i in base.get_favourites(cur, variables['id'], True)]
    if respone is None:
        bot.write_msg(vk, variables['id'], "Ничего не найдено. Уточните параметры поиска")
        variables['fields']['filtr_dict'] = {}
        photos = None
        return variables, respone, photos
    elif len(respone) == 0:
        bot.write_msg(vk, variables['id'], "Простите, людей не найдено")
        variables['fields']['offset'] += 3
        photos = None
        return variables, respone, photos
    else:
        # возвращает фото в словаре вида {'href': [], 'owner_id': ""}
        while True:
            if respone[variables['fields']['number']][0] in block_list:
                variables['fields']['number'] += 1
                if len(respone) == variables['fields']['number']:
                    bot.write_msg(vk, variables['id'], "\U000026D4 Обновляю список обнаруженных людей. \U0001F605")
                    variables['fields']['number'] = 0
                    variables['fields']['offset'] += 3
                    ################################################
                    respone = response.get_users(variables['fields'])
                    keyboard = bot.create_buttons(4)
                    bot.write_msg(vk, variables['id'], "Подождите. Сейчас загружаю фотографии. \U0001F609", keyboard)
                    continue
            else:
                photos = response.get_users_photo(str(respone[variables['fields']['number']][0])) # format {'href': ['https://sun1-89.user...type=album', 'https://sun9-64.user...type=album', 'https://sun9-1.usera...type=album'], 'owner_id': ''}
                                    
                if photos is None:
                    keyboard = bot.create_buttons(1)
                    bot.write_msg(vk, variables['id'], "\U000026D4 \U0001F6AB У пользователя нет фотографий.\nНажмите следующий. \U0001F914", keyboard)
                    continue
                                    
                message = f"{respone[variables['fields']['number']][1]}\n https://vk.com/id{photos.get('owner_id')}"
                bot.write_msg(vk, variables['id'], message) # format 'Юлия Волкова\n https://vk.com/id'

                attachment = bot.add_photos(vk, photos.get('href')) # format ['photo-217703779_457239656', 'photo-217703779_457239657', 'photo-217703779_457239658']
                bot.send_photos(vk, variables['id'], attachment)
                keyboard = bot.create_buttons(4)
                bot.write_msg(vk, variables['id'], "Выполнено \U00002705", keyboard)
                return variables, respone, photos


def checking_the_length_of_the_list(variables, respone, vk, response, cur):

    bot.write_msg(vk, variables['id'], "\U000026D4 Обновляю список обнаруженных людей. \U0001F605")
    variables['fields']['number'] = 0
    variables['fields']['offset'] += 3
    variables, respone, photos = photo_requests_for_users(vk, response, cur, variables)
    return variables, respone, photos
    

def cancel_button(vk, variables):

    variables['count'] = 0
    variables['start'] = False
    variables['continue'] = False
    variables['filtr_dict'] = {}
    variables['fields']['number'] = 0
    variables['fields']['offset'] = 0
    bot.write_msg(vk, variables['id'], "Желаете найти кого-то другого? \U0001F914 Наберите команду старт. \U0001F920")
    return variables


def save_to_favorites(cur, photos, respone, variables):

    id, name, bdate = respone[variables['fields']['number']] # format respone [[488749963, 'Юлия Волкова', '20.11.1999'], [576362782, 'Katy Perry'], [574435155, 'Кристина Белова'], [400790625, 'Яна Гончарова'], [417877132, 'Ирина Родомакина'], [433476343, 'Кира Чудина'], [397419005, 'Tanya Aronovich']]
    if not base.checking_list_favorites(cur, id):
        sex = variables['fields']['filtr_dict'].get('sex')
        city = variables['fields']['filtr_dict'].get('city')
        link = f"https://vk.com/id{photos.get('owner_id')}"
        favorites_id = base.add_favourites(cur, id, name, bdate, 
                                            sex, city, link)
        base.add_photos(cur, photos['href'], favorites_id)
    return id


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

    object_vkinder = VKinder(longpoll, session)

    # print(base.drop_table(cur)) #если нужно сбросить БД
    print(base.create_db(cur))

    for event in longpoll.listen():

        # Если пришло новое сообщение
        if event.type == VkEventType.MESSAGE_NEW:

            # Выставляем параметры для пользователя написавшего сообщение
            result = bot.user_support(event, list_of_users, list_of_dicts) # format ({'id': 33579332, 'fields': {...}}, [33579332], [{...}])           ---       {'id': 33579332, 'fields': {'text': None, 'count': 0, 'start': False, 'continue': False, 'filtr_dict': {...}, 'sql': {}, 'start_request': False, 'number': 0}}     ----         [33579332]      ---       [{'id': 33579332, 'fields': {...}}]  

            variables = result[0] # формат {'id': 33579332, 'fields': {'link': None, 'count': 3, 'start': True, 'continue': False, 'filtr_dict': {...}, 'sql': {}, 'start_request': False, 'number': 0}}
            list_of_users = result[1] # формат [33579332, 45686545]
            list_of_dicts = result[2] # формат [{'id': 33579332, 'fields': {...}}]

            object_vkinder.checking_the_user_in_the_database(cur, variables['id'], response)

            # Пользователь отправил сообщение или нажал кнопку для бота(бот вк)
            if event.to_me:
                message_text = event.text.lower().strip()
                if variables['fields']['start']:
                    # Активирована команда СТАРТ (поиск людей)
                    variables['fields'] = bot.event_handling_start(vk, message_text, variables)
                    if variables['fields']['continue']: # формат {'id': 33579332, 'fields': {'text': None, 'count': 0, 'start': False, 'continue': False, 'filtr_dict': {...}, 'sql': {}, 'start_request': False, 'number': 0}}
                        variables['fields']['continue'] = False
                        continue
                    else:
                        # Запросы на фото для пользователя
                        variables, respone, photos = photo_requests_for_users(vk, response, cur, variables)
                else:
                    # Логика обычного ответа
                    if message_text == 'привет':
                        object_vkinder.the_command_to_greet(cur, variables['id'], vk)
                    
                    elif message_text in ['список', 'показать весь список']:
                        if object_vkinder.checking_the_favorites_list(cur, variables['id'], vk):
                            continue

                    elif message_text in ['следующий']:
                        keyboard = bot.create_buttons(4)
                        bot.write_msg(vk, variables['id'], "Подождите. Сейчас загружаю фотографии. \U0001F609", keyboard)
                        variables['fields']['number'] += 1
                        if len(respone) == variables['fields']['number']:
                            variables, respone, photos = checking_the_length_of_the_list(variables, respone, vk, response, cur)
                            continue
                        else:                           
                            block_list = [i[4] for i in base.get_favourites(cur, variables['id'], True)]
                            while True:
                                if respone[variables['fields']['number']][0] in block_list:
                                    variables['fields']['number'] += 1
                                    if len(respone) == variables['fields']['number']:
                                        variables, respone, photos = checking_the_length_of_the_list(variables, respone, vk, response, cur)
                                        break
                                else:
                                    photos = response.get_users_photo(str(respone[variables['fields']['number']][0]))
                                    if photos is None:
                                        keyboard = bot.create_buttons(1)
                                        bot.write_msg(vk, variables['id'], "\n\U000026D4 \U0001F6AB У пользователя нет фотографий.\nНажмите следующий. \U0001F914", keyboard)
                                        continue
                                    
                                    message = f"{respone[variables['fields']['number']][1]}\n https://vk.com/id{photos.get('owner_id')}"
                                    bot.write_msg(vk, variables['id'], message) # format 'Юлия Волкова\n https://vk.com/id'
                                    attachment = bot.add_photos(vk, photos.get('href'))
                                    bot.send_photos(vk, variables['id'], attachment)
                                    break

                    elif message_text in ['добавить в избранное']:
                        id = save_to_favorites(cur, photos, respone, variables)  
                        if not base.checking_the_human_user_connection(cur, variables['id'], id):
                            base.add_a_human_user_relationship(cur, variables['id'], id, False) 
                        else:
                            if base.checking_the_human_user_connection(cur, variables['id'], id)[0][-1] == True: # format [(1, 33579332, 711644755, False)]
                                base.del_block_list(cur, variables['id'], id)
                            else:
                                keyboard = bot.create_buttons(4)
                                bot.write_msg(vk, variables['id'], "Данный человек ранее был добавлен в список избранных \U0001F60D", keyboard)

                    elif message_text in ['добавить в черный список']:
                        id = save_to_favorites(cur, photos, respone, variables)
                        if not base.checking_the_human_user_connection(cur, variables['id'], id):
                            base.add_a_human_user_relationship(cur, variables['id'], id, True) 
                        else:
                            if base.checking_the_human_user_connection(cur, variables['id'], id)[0][-1] == False:
                                base.add_block_list(cur, variables['id'], id)
                            else:
                                keyboard = bot.create_buttons(4)
                                bot.write_msg(vk, variables['id'], "Данный человек ранее был добавлен в черный список \U0001F628", keyboard)

                    elif message_text in ['отменить']:
                        variables = cancel_button(vk, variables)

                    variables['fields'] = bot.processing_a_simple_message(vk, message_text, variables)



if __name__ == '__main__':
    main()
            