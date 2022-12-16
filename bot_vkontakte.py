import vk_api
import requests
import os
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from random import randint
from token_vk import token_vk_community, token_vk
from vk_api.longpoll import VkLongPoll


def connection():

    # Авторизуемся как сообщество
    authorize = vk_api.VkApi(token=token_vk_community)

    # Работа с сообщениями
    longpoll = VkLongPoll(authorize)

    user_session = vk_api.VkApi(token=token_vk)
    session = user_session.get_api()

    return longpoll, session, authorize


def user_support(event: object, list_of_users: list, list_of_dicts: list) -> tuple:

    '''Отслеживает переменные каждого пользователя работающего с ботом'''

    if event.user_id in list_of_users:
        for user in list_of_dicts:
            if event.user_id == user['id']:
                variables = user
                return variables, list_of_users, list_of_dicts
    else:
        first_variables = {'id': None, 'fields': {
                        'text': None,
                        'count': 0, 
                        'start': False, 
                        'continue': False, 
                        'filtr_dict': {}, 
                        'sql': {},
                        'start_request': False
                        }
                    }
        first_variables['id'] = event.user_id
        list_of_dicts.append(first_variables)
        list_of_users.append(event.user_id)
        variables = first_variables 
        
    return variables, list_of_users, list_of_dicts


def create_keyboard(response):

    """Создание клавиатуры"""

    keyboard = VkKeyboard(one_time=True)
    if response in ['Привет', 'привет', 'Поиск', 'поиск']:
        keyboard.add_button('Заполнить базу')
        keyboard.add_line()
        keyboard.add_button('Просмотреть список избранных',
                            color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Просмотреть данные пользователей',
                            color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Закончить')

    elif response in ['Заполнить базу']:
        keyboard.add_button('Просмотреть список избранных',
                            color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Просмотреть данные пользователей',
                            color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Закончить')

    elif response in ['Просмотреть список избранных']:
        keyboard.add_button('Просмотреть данные пользователей',
                            color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Закончить')

    elif response in ['Начать поиск', 'Просмотреть данные пользователей', 'Вернуться к поиску',
                       'Добавить в список избранных', 'Добавить в черный список', 'Продолжить поиск']:
        keyboard.add_button('Добавить в список избранных', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('Добавить в черный список', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button('Продолжить поиск')
        keyboard.add_line()
        keyboard.add_button('Закончить')

    elif response in ['Получить фото', 'Написать']:
        keyboard.add_button('Вернуться к поиску')
        keyboard.add_line()
        keyboard.add_button('Закончить')

    elif response in ['Получить фото', 'Написать']:
        keyboard.add_button('Получить фото', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('Написать', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Вернуться к поиску')

    elif response == 'Закончить':
        keyboard.add_button('Пока')
        keyboard.add_line()
        keyboard.add_button('Вернуться к поиску')

    elif response == 'Пока':
        keyboard.add_button('Привет')

    else:
        keyboard.add_button('Начать поиск', color=VkKeyboardColor.POSITIVE)

    keyboard = keyboard.get_keyboard()
    return keyboard



def write_msg(object_vk_api: object, sender_id: str, message: str, keyboard=None) -> None:

    '''Отправляет сообщения и добавляет кнопки к сообщениям'''

    post = {
        'user_id': sender_id, 
        'message': message, 
        'random_id': randint(0, 10 ** 7)
    }

    if keyboard != None:
        post['keyboard'] = keyboard.get_keyboard()
    else:
        post = post
        keyboard = VkKeyboard()
        post['keyboard'] = keyboard.get_empty_keyboard()

    object_vk_api.method('messages.send', post)


def send_photos(object_vk_api: object, sender_id: str, attachment: list) -> None:

    '''Отправляет фотографии пользователю'''

    for element in attachment:
        object_vk_api.method('messages.send', {
            'user_id': sender_id, 
            'attachment': element,
            'random_id': randint(0, 10 ** 7)
            })


def add_photos(object_vk_api: object, list_photos: list) -> list:

    '''Загружает и добавляет фотографии в список на обновление сообщения'''

    attachment_list = []
    uploader = vk_api.VkUpload(object_vk_api)
    for element in list_photos:
        img = requests.get(element).content
        name = element.partition('?')[0].split('/')[-1]
        with open(f'test_photo\\{name}', 'wb') as f:
            f.write(img)
        img = uploader.photo_messages(f'test_photo\\{name}')
        media_id = str(img[0]['id'])
        owner_id = str(img[0]['owner_id'])
        attachment_list.append(f'photo{owner_id}_{media_id}')
        os.remove(f'test_photo\\{name}')
    return attachment_list


# def create_buttons(number: int) -> VkKeyboard:
#
#     '''Создает цветные кнопки'''
#
#     keyboard = VkKeyboard()
#     buttons_colors = [VkKeyboardColor.PRIMARY, VkKeyboardColor.POSITIVE,
#                         VkKeyboardColor.NEGATIVE, VkKeyboardColor.SECONDARY]
#     if number == 2:
#         keyboard.add_button('Сбросить', buttons_colors[0])
#         keyboard.add_line()
#         keyboard.add_button('Отменить', buttons_colors[-1])
#     elif number == 4:
#         buttons = [i.capitalize() for i in dict_func]
#         count = 0
#         for btn, btn_color in zip(buttons, buttons_colors):
#             if count == 2:
#                 keyboard.add_line()
#             keyboard.add_button(btn, btn_color)
#             count += 1
#     return keyboard


def add_person_to_sql(*args, **kwargs):
    pass


def next_person(*args, **kwargs):
    pass


def show_the_full_list(*args, **kwargs):
    pass
    

def add_to_blacklist(*args, **kwargs):
    pass


def add_data_to_the_dictionary(object_vk_api: object, index: int,
                                sender_id: str, message_text: str, date: dict) -> dict:

    '''Добавляет данные полученные от пользователя в словарь'''

    if index - 1 == 0:
        if '-' in message_text:
            text = message_text.replace(' ', '').split('-')
        else:
            text = message_text.strip()
        for element in text:
            if not element.isdigit():
                index = index - 1
                keyboard = create_buttons(2)
                write_msg(object_vk_api, sender_id, "Не правильно указан возраст!!! Повторите ввод.", keyboard)
                return date, index
    elif index - 1 == 1:
        if not message_text.strip() in ('1', '2'):
            index = index - 1
            keyboard = create_buttons(2)
            write_msg(object_vk_api, sender_id, "Не правильно указан пол человека!!! Повторите ввод.", keyboard)
            return date, index
        else:
            text = message_text.strip()
    else:
        text = message_text.lower().replace('.', '')
    date.setdefault(categories_of_questions[index - 1], text)
    return date, index


def event_handling_start(object_vk_api: object, message_text: str, variables: dict) -> dict:

    '''Обработка события СТАРТ. Бот задаёт вопросы и создает словарь'''

    sender_id = variables['id']
    variables = variables['fields']
    if message_text == 'сбросить':
        variables['count'] = 0
    elif message_text == 'отменить':
        variables['count'] = 0
        variables['start'] = False
        write_msg(object_vk_api, sender_id, 'Ок')
        variables['continue'] = True
        return variables

    variables['filtr_dict'], variables['count'] = add_data_to_the_dictionary(
        object_vk_api, variables['count'], sender_id, message_text, variables['filtr_dict']
    )
    if variables['count'] < len(bot_questions):
        # бот продолжает задавать вопросы
        keyboard = create_buttons(2)
        write_msg(object_vk_api, sender_id, bot_questions[variables['count']], keyboard)
        variables['count'] += 1
        variables['continue'] = True
        return variables
    else:
        variables['start'] = False
        variables['count'] = 0
        # Активируем цветные кнопки
        keyboard = create_buttons(4)
        write_msg(object_vk_api, sender_id, "Подождите. Сейчас загружаю фотографии. \U0001F609", keyboard)
    return variables

#
# def processing_a_simple_message(object_vk_api: object, message_text: str, variables: dict) -> dict:
#
#     '''Обработка событий простых сообщений и нажатия кнопок'''
#
#     sender_id = variables['id']
#     variables = variables['fields']
#     if message_text == "привет":
#         pass
#     elif message_text == "фото":
#         pass
#     elif message_text == "старт":
#         keyboard = create_buttons(2)
#         write_msg(object_vk_api, sender_id, bot_questions[variables['count']], keyboard)
#         variables['count'] += 1
#         variables['start'] = True
#     elif message_text in dict_func:
#         dict_func[message_text](**variables['sql'])
#         keyboard = create_buttons(4)
#         write_msg(object_vk_api, sender_id, "Выполнено \U00002705", keyboard)
#     else:
#         write_msg(object_vk_api, sender_id, "Не поняла вашего ответа... \U0001F937\U0001F92F\U0001F914\U0001F60A")
#     return variables


dict_func = {
    'добавить в избранное': add_person_to_sql,
    'следующий': next_person,
    'показать весь список': show_the_full_list,
    'добавить в черный список': add_to_blacklist
}

bot_questions = [
    "Укажите возраст людей по образцу\nПример: 25 или 20-30 \U0001F609",
    "Укажите пол (муж -1 \U0001F57A или жен - 2 \U0001F483):",
    "Укажите город: \U0001F3E1"
    #"Семейное положение: \U0001F48F"
]

categories_of_questions = ['age', 'sex', 'city'] #, 'status'] 


if __name__ == '__main__':
    pass