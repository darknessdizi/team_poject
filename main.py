import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import base
from token_vk import token_vk_community, token_vk_user, sql_authorization
import bot_vkontakte as bot
from requests_to_vk import RequestsVk
from datetime import date


def connection():
    # Авторизуемся как сообщество
    authorize = vk_api.VkApi(token=token_vk_community)

    # Работа с сообщениями
    longpoll = VkLongPoll(authorize)

    user_session = vk_api.VkApi(token=token_vk_user)
    session = user_session.get_api()
    return longpoll, session, authorize


def calculate_age(born):
    born = born.split(".")
    today = date.today()
    return today.year - int(born[2]) - ((today.month, today.day) < (int(born[1]), int(born[0])))


def data_conversion(db_source, cur):
    '''Преобразует данные из базы данных для бота '''
    users = list()
    for item in db_source:
        users.append({'id': item[0], 'name': f'{item[1]} {item[2]}', 'url': item[3]})
    return users


def main():

    # Основной цикл
    list_of_users = []
    list_of_dicts = []

    # Создание объекта для подключения к базе данных
    sql_cursor = base.PostgreSQL(**sql_authorization)
    cur = sql_cursor.connect.cursor()

    longpoll, session, vk = connection()
    print(base.drop_table(cur)) #если нужно сбросить БД
    print(base.create_db(cur))

    for event in longpoll.listen():

        # Если пришло новое сообщение
        if event.type == VkEventType.MESSAGE_NEW:
            
            if event.user_id in list_of_users:
                for user in list_of_dicts:
                    if event.user_id == user['id']:
                        variables = user
            else:
                first_variables = {'id': None, 'fields': {
                            'text': None,
                            'count': 0, 
                            'start': False, 
                            'continue': False, 
                            'filtr_dict': {}, 
                            'sql': {}
                            }
                        }
                first_variables['id'] = event.user_id
                list_of_dicts.append(first_variables)
                list_of_users.append(event.user_id)
                variables = first_variables            

            if not base.get_ask_user_data(cur, variables['id']):
                print('в базе отсутствует')
                response = RequestsVk(token_vk_user)
                user_info = response.get_user(variables['id'])               
                user_info['age'] = calculate_age(user_info['age'])
                if user_info['sex'] == 2:
                    user_info['gender'] = 'Мужской'
                elif user_info['sex'] == 1:
                    user_info['gender'] = 'Женский'
                else:
                    user_info['gender'] = 'Пол не указан'
                if base.add_ask_user(cur, variables['id'], user_info['user_name'],
                                   user_info['age'], user_info['city'],
                                   user_info['gender']):
                    # sql_cursor.commit()
                    print('пользователь добавлен в базу')
                else:
                    print('пользователь НЕ добавлен в базу')

            if event.text.lower().strip() == "привет":
                ask_user = base.get_ask_user_data(cur, variables['id'])
                print(f'Пользователь = {ask_user}')

                ask_user = base.get_ask_user_data(cur, variables['id'])
                bot.write_msg(vk, variables['id'], f"Здравствуйте, {ask_user[1]}!\n"
                                                    f"Ваши параметры:\nГород: {ask_user[3]}\n"
                                                    f"Пол: {ask_user[4]}\nВозраст: {ask_user[2]}\n"
                                                    f"(Введите: старт\фото\список)")

            elif event.text.lower().strip() in ['список']:
                if base.get_favourites(cur, variables['id']):
                    db_source = base.get_favourites(cur, variables['id'])
                    favourites = data_conversion(db_source, cur)
                    for item in favourites:
                        bot.write_msg(vk, variables['id'], f"{item['name']}\n{item['url']}")
                    bot.write_msg(vk, variables['id'], "Просмотреть данные")
                else:
                    bot.write_msg(vk, variables['id'], f"Список избранных пуст")
                    continue

            # Пользователь отправил сообщение или нажал кнопку для бота(бот вк)
            if event.to_me:
                print('1 точка')
                message_text = event.text.lower().strip()
                if variables['fields']['start']:
                    print('3 точка')
                    # Активирована команда старт (поиск людей)
                    variables['fields'] = bot.event_handling_start(vk, message_text, variables)
                    if variables['fields']['continue']:
                        print('4 точка')
                        variables['fields']['continue'] = False
                        continue
                else:
                    print('2 точка')
                    # Логика обычного ответа
                    variables['fields'] = bot.processing_a_simple_message(vk, message_text, variables)
            print('5 точка')


if __name__ == '__main__':
    main()
            