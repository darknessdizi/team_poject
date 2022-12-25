# В модуле реализованы  функции по созданию объекта сообщества и объекта пользователя
# для взаимодействия с сообщениями от пользователей

import vk_api
import requests
import os
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from random import randint
from token_vk import token_vk_community, token_vk
from vk_api.longpoll import VkLongPoll


def connection() -> tuple:
    """Создает объекты для работы с сообщениями в чат боте вконтакте,

    объект для работы пользователя с Api вконтакте и объект сообщества"""

    # Авторизуемся как сообщество
    authorize = vk_api.VkApi(token=token_vk_community)

    # Работа с сообщениями
    longpoll = VkLongPoll(authorize)

    user_session = vk_api.VkApi(token=token_vk)
    session = user_session.get_api()

    return longpoll, session, authorize


def user_support(event: object,
                 list_of_users: list, list_of_dicts: list) -> tuple:
    """Отслеживает переменные каждого пользователя работающего с ботом"""

    if event.user_id in list_of_users:
        for user in list_of_dicts:
            if event.user_id == user['id']:
                variables = user
                return variables, list_of_users, list_of_dicts
    else:
        first_variables = {'id': event.user_id, 'fields': {
            'count': 0,
            'start': False,
            'continue': False,
            'filtr_dict': {},
            'number': 0,
            'offset': 0,
            'end_list': False
        }}
        list_of_dicts.append(first_variables)
        list_of_users.append(event.user_id)
        variables = first_variables

    return variables, list_of_users, list_of_dicts


def write_msg(object_vk_api: object,
              sender_id: str, message: str, keyboard=None) -> None:
    """Отправляет сообщения и добавляет кнопки к сообщениям"""

    post = {
        'user_id': sender_id,
        'message': message,
        'random_id': randint(0, 10 ** 7)
    }

    if keyboard is not None:
        post['keyboard'] = keyboard.get_keyboard()
    else:
        post = post
        keyboard = VkKeyboard()
        post['keyboard'] = keyboard.get_empty_keyboard()

    object_vk_api.method('messages.send', post)


def send_photos(object_vk_api: object,
                sender_id: str, attachment: list) -> None:
    """Отправляет метод и его параметры в Api вконтакте

    для отправки сообщений в чат"""

    for element in attachment:
        object_vk_api.method('messages.send', {
            'user_id': sender_id,
            'attachment': element,
            'random_id': randint(0, 10 ** 7)
        })


def add_photos(object_vk_api: object, list_photos: list) -> list:
    """Загружает и добавляет фотографии в список на обновление сообщения"""

    attachment_list = []
    uploader = vk_api.VkUpload(object_vk_api)
    for element in list_photos:
        img = requests.get(element).content
        name = element.partition('?')[0].split('/')[-1]
        with open(f'{name}', 'wb') as f:
            f.write(img)
        img = uploader.photo_messages(f'{name}')
        media_id = str(img[0]['id'])
        owner_id = str(img[0]['owner_id'])
        attachment_list.append(f'photo{owner_id}_{media_id}')
        os.remove(f'{name}')
    return attachment_list


def create_buttons(number: int) -> VkKeyboard:
    """Создает объект с параметрами кнопок"""

    keyboard = VkKeyboard()
    buttons_colors = [VkKeyboardColor.PRIMARY, VkKeyboardColor.POSITIVE,
                      VkKeyboardColor.NEGATIVE, VkKeyboardColor.SECONDARY]
    if number == 1:
        keyboard.add_button('Следующий', buttons_colors[1])
    elif number == 2:
        keyboard.add_button('Сбросить', buttons_colors[0])
        keyboard.add_line()
        keyboard.add_button('Отменить', buttons_colors[-1])
    elif number == 4:
        buttons = [i.capitalize() for i in list_button]
        count = 0
        for btn, btn_color in zip(buttons, buttons_colors):
            if count == 2:
                keyboard.add_line()
            keyboard.add_button(btn, btn_color)
            count += 1
        keyboard.add_line()
        keyboard.add_button('Отменить', buttons_colors[0])
    return keyboard


def add_data_to_the_dictionary(object_vk_api: object,
                               index: int, sender_id: str, message_text: str, date: dict) -> tuple:
    """Добавляет ответы полученные от пользователя в словарь"""

    if index - 1 == 0:
        if '-' in message_text:
            text = message_text.replace(' ', '').split('-')
        else:
            text = message_text.strip()
            text_list = [text, text]
            text = text_list
        for element in text:
            if not element.isdigit():
                index = index - 1
                keyboard = create_buttons(2)
                write_msg(
                    object_vk_api, sender_id,
                    "Не правильно указан возраст!!! Повторите ввод.",
                    keyboard
                )
                return date, index
    elif index - 1 == 1:
        if not message_text.strip() in ('1', '2'):
            index = index - 1
            keyboard = create_buttons(2)
            write_msg(
                object_vk_api, sender_id,
                "Не правильно указан пол человека!!! Повторите ввод.",
                keyboard
            )
            return date, index
        else:
            text = message_text.strip()
    else:
        text = message_text.lower().replace('.', '')
    date.setdefault(categories_of_questions[index - 1], text)
    return date, index


def event_handling_start(
        object_vk_api: object, message_text: str, variables: dict) -> dict:
    """Обработка события СТАРТ. Бот задаёт вопросы и создает словарь"""

    sender_id = variables['id']
    variables = variables['fields']
    if message_text == 'сбросить':
        variables['count'] = 0
        keyboard = create_buttons(2)
        write_msg(
            object_vk_api, sender_id,
            bot_questions[variables['count']],
            keyboard
        )
        variables['filtr_dict'] = {}
        variables['count'] = 1
        variables['continue'] = True
        variables['number'] = 0
        return variables
    elif message_text == 'отменить':
        variables['count'] = 0
        variables['start'] = False
        write_msg(object_vk_api, sender_id, 'Ок')
        variables['continue'] = True
        variables['filtr_dict'] = {}
        variables['number'] = 0
        return variables

    variables['filtr_dict'], variables['count'] = add_data_to_the_dictionary(
        object_vk_api, variables['count'],
        sender_id, message_text, variables['filtr_dict']
    )
    if variables['count'] < len(bot_questions):
        keyboard = create_buttons(2)
        write_msg(
            object_vk_api, sender_id,
            bot_questions[variables['count']],
            keyboard
        )
        variables['count'] += 1
        variables['continue'] = True
        return variables
    else:
        variables['start'] = False
        variables['count'] = 0
        keyboard = create_buttons(4)
        write_msg(
            object_vk_api, sender_id,
            "Подождите. Сейчас загружаю фотографии. \U0001F609",
            keyboard
        )
    return variables


def processing_a_simple_message(
        object_vk_api: object, message_text: str, variables: dict) -> dict:
    """Обработка событий простых сообщений и нажатия кнопок"""

    sender_id = variables['id']
    variables = variables['fields']
    if message_text == "старт":
        keyboard = create_buttons(2)
        write_msg(
            object_vk_api, sender_id,
            bot_questions[variables['count']],
            keyboard
        )
        variables['count'] += 1
        variables['start'] = True
        variables['continue'] = True
        variables['filtr_dict'] = {}
        variables['number'] = 0
        variables['offset'] = 0
    elif message_text in list_button:
        if variables['end_list']:
            write_msg(object_vk_api, sender_id, "Выполнено \U00002705")
            variables['end_list'] = False
        else:
            keyboard = create_buttons(4)
            write_msg(object_vk_api, sender_id, "Выполнено \U00002705", keyboard)
    elif message_text in ['привет', 'отменить']:
        pass
    else:
        write_msg(
            object_vk_api, sender_id,
            "Не поняла вашего ответа... \U0001F937\U0001F92F\U0001F914\U0001F60A"
        )
    return variables


list_button = [
    'добавить в избранное',
    'следующий',
    'показать весь список',
    'добавить в черный список'
]

bot_questions = [
    "Укажите возраст людей по образцу\nПример: 25 или 20-30 \U0001F609",
    "Укажите пол (жен - 1 \U0001F483 или муж - 2 \U0001F57A ):",
    "Укажите город: \U0001F3E1"
]

categories_of_questions = ['age', 'sex', 'city']

if __name__ == '__main__':
    pass
