import base
import bot_vkontakte as bot
from token_vk import token_vk, sql_authorization
from vk_api.longpoll import VkEventType
from requests_to_vk import RequestsVk
from VKinder import VKinder, PostgreSQL


def main():

    # Основной цикл
    list_of_users = []
    list_of_dicts = []

    # Создание объекта для подключения к базе данных
    sql_cursor = PostgreSQL(**sql_authorization)
    cur = sql_cursor.connect.cursor()

    # Создание объекта для осуществления request запросов
    response = RequestsVk(token_vk)
    longpoll, session, community = bot.connection()
    object_vkinder = VKinder(longpoll, session)

    # print(base.drop_table(cur)) #если нужно сбросить БД
    print(base.create_db(cur))

    for event in longpoll.listen():

        # Если пришло новое сообщение
        if event.type == VkEventType.MESSAGE_NEW:

            # Выставляем параметры для пользователя написавшего сообщение
            result = bot.user_support(event, list_of_users, list_of_dicts) 
            variables = result[0] 
            list_of_users = result[1] 
            list_of_dicts = result[2] 
            object_vkinder.checking_the_user_in_the_database(
                cur, variables['id'], response
            )

            # Пользователь отправил сообщение или нажал кнопку для бота(бот вк)
            if event.to_me:
                message_text = event.text.lower().strip()
                if variables['fields']['start']:
                    # Активирована команда СТАРТ (поиск людей)
                    variables['fields'] = bot.event_handling_start(
                        community, message_text, variables
                    )
                    if variables['fields']['continue']: 
                        variables['fields']['continue'] = False
                        continue
                    else:
                        # Запросы на фото для пользователя
                        variables, respone, photos = bot.photo_requests_for_users(
                            community, response, cur, variables
                        )
                else:
                    # Логика обычного ответа
                    if message_text == 'привет':
                        object_vkinder.the_command_to_greet(
                            cur, variables['id'], community
                        )
                    
                    elif message_text in ['список', 'показать весь список']:
                        if object_vkinder.checking_the_favorites_list(
                            cur, variables['id'], community
                        ):
                            continue

                    elif message_text in ['следующий']:
                        keyboard = bot.create_buttons(4)
                        bot.write_msg(
                            community, variables['id'], 
                            "Подождите. Сейчас загружаю фотографии. \U0001F609", 
                            keyboard
                        )
                        variables['fields']['number'] += 1
                        if len(respone) == variables['fields']['number']:
                            variables, respone, photos = bot.updates_the_list_of_people(
                                variables, respone, community, response, cur
                            )
                            continue
                        else:                           
                            block_list = [i[4] for i in base.get_favourites(
                                cur, variables['id'], True
                                )
                            ]
                            while True:
                                if respone[variables['fields']['number']][0] in block_list:
                                    variables['fields']['number'] += 1
                                    if len(respone) == variables['fields']['number']:
                                        variables, respone, photos = bot.updates_the_list_of_people(
                                            variables, respone, community, response, cur
                                        )
                                        break
                                else:
                                    photos = response.get_users_photo(
                                        str(respone[variables['fields']['number']][0])
                                    )
                                    if photos is None:
                                        keyboard = bot.create_buttons(1)
                                        bot.write_msg(
                                            community, variables['id'], 
                                            "\n\U000026D4 \U0001F6AB У пользователя нет фотографий.\nНажмите следующий. \U0001F914",
                                            keyboard
                                        )
                                        continue
                                    
                                    text = respone[variables['fields']['number']][1]
                                    message = f"{text}\n https://vk.com/id{photos.get('owner_id')}"
                                    bot.write_msg(community, variables['id'], message) 
                                    attachment = bot.add_photos(community, photos.get('href'))
                                    bot.send_photos(community, variables['id'], attachment)
                                    break

                    elif message_text in ['добавить в избранное']:
                        id = bot.save_to_favorites(cur, photos, respone, variables)  
                        if not base.checking_the_human_user_connection(
                            cur, variables['id'], id
                        ):
                            base.add_a_human_user_relationship(
                                cur, variables['id'], id, False
                            ) 
                        else:
                            if base.checking_the_human_user_connection(
                                cur, variables['id'], id
                            )[0][-1] == True: 
                                base.del_block_list(cur, variables['id'], id)
                            else:
                                keyboard = bot.create_buttons(4)
                                bot.write_msg(
                                    community, variables['id'], 
                                    "Данный человек ранее был добавлен в список избранных \U0001F60D", 
                                    keyboard
                                )

                    elif message_text in ['добавить в черный список']:
                        id = bot.save_to_favorites(cur, photos, respone, variables)
                        if not base.checking_the_human_user_connection(
                            cur, variables['id'], id
                        ):
                            base.add_a_human_user_relationship(
                                cur, variables['id'], id, True
                            ) 
                        else:
                            if base.checking_the_human_user_connection(
                                cur, variables['id'], id
                            )[0][-1] == False:
                                base.add_block_list(cur, variables['id'], id)
                            else:
                                keyboard = bot.create_buttons(4)
                                bot.write_msg(
                                    community, variables['id'], 
                                    "Данный человек ранее был добавлен в черный список \U0001F628", 
                                    keyboard
                                )

                    elif message_text in ['отменить']:
                        variables = bot.cancel_button(community, variables)

                    variables['fields'] = bot.processing_a_simple_message(
                        community, message_text, variables
                    )


if __name__ == '__main__':
    main()
            