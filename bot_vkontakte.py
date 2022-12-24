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
    # format  event: <vk_api.longpoll.Event object at 0x0000025CC1FABA90>
    # format  list_of_users: [33579332]
    # format  list_of_dicts: [{'id': 33579332, 'fields': {...}}]

    '''Отслеживает переменные каждого пользователя работающего с ботом'''

    if event.user_id in list_of_users: # format event.user_id: 33579332
        for user in list_of_dicts:
            if event.user_id == user['id']:
                variables = user
                return variables, list_of_users, list_of_dicts
    else:
        first_variables = {'id': None, 'fields': {
                        'count': 0, 
                        'start': False, 
                        'continue': False, 
                        'filtr_dict': {}, 
                        'number': 0,
                        'offset': 0,
                        'end_list': False
                        }
                    }
        first_variables['id'] = event.user_id
        list_of_dicts.append(first_variables)
        list_of_users.append(event.user_id)
        variables = first_variables 
        
    return variables, list_of_users, list_of_dicts


# def create_keyboard(response):

#     """Создание клавиатуры"""

#     keyboard = VkKeyboard(one_time=True)
#     if response in ['Привет', 'привет', 'Поиск', 'поиск']:
#         keyboard.add_button('Заполнить базу')
#         keyboard.add_line()
#         keyboard.add_button('Список',
#                             color=VkKeyboardColor.POSITIVE)
#         keyboard.add_line()
#         keyboard.add_button('Смотреть данные',
#                             color=VkKeyboardColor.POSITIVE)
#         keyboard.add_line()
#         keyboard.add_button('Закончить')

#     elif response in ['Заполнить базу']:
#         keyboard.add_button('Просмотреть список избранных',
#                             color=VkKeyboardColor.POSITIVE)
#         keyboard.add_line()
#         keyboard.add_button('Просмотреть данные пользователей',
#                             color=VkKeyboardColor.POSITIVE)
#         keyboard.add_line()
#         keyboard.add_button('Закончить')

#     elif response in ['Просмотреть список избранных']:
#         keyboard.add_button('Просмотреть данные пользователей',
#                             color=VkKeyboardColor.POSITIVE)
#         keyboard.add_line()
#         keyboard.add_button('Закончить')

#     elif response in ['Начать поиск', 'Просмотреть данные пользователей', 'Вернуться к поиску',
#                        'Добавить в список избранных', 'Добавить в черный список', 'Продолжить поиск']:
#         keyboard.add_button('Добавить в список избранных',
#                             color=VkKeyboardColor.POSITIVE)
#         keyboard.add_button('Добавить в черный список',
#                             color=VkKeyboardColor.NEGATIVE)
#         keyboard.add_line()
#         keyboard.add_button('Продолжить поиск')
#         keyboard.add_line()
#         keyboard.add_button('Закончить')

#     elif response in ['Получить фото', 'Написать']:
#         keyboard.add_button('Вернуться к поиску')
#         keyboard.add_line()
#         keyboard.add_button('Закончить')

#     elif response in ['Получить фото', 'Написать']:
#         keyboard.add_button('Получить фото', color=VkKeyboardColor.POSITIVE)
#         keyboard.add_button('Написать', color=VkKeyboardColor.POSITIVE)
#         keyboard.add_line()
#         keyboard.add_button('Вернуться к поиску')

#     elif response == 'Закончить':
#         keyboard.add_button('Пока')
#         keyboard.add_line()
#         keyboard.add_button('Вернуться к поиску')

#     elif response == 'Пока':
#         keyboard.add_button('Привет')

#     else:
#         keyboard.add_button('Начать поиск', color=VkKeyboardColor.POSITIVE)

#     keyboard = keyboard.get_keyboard()
#     return keyboard



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
    # format object_vk_api: <vk_api.vk_api.VkApi object at 0x0000025CC1F43460>
    # format sender_id: 33579332
    # format attachment: ['photo-217703779_457239656', 'photo-217703779_457239657', 'photo-217703779_457239658']

    '''Отправляет фотографии пользователю'''

    for element in attachment:
        object_vk_api.method('messages.send', {
            'user_id': sender_id, 
            'attachment': element,
            'random_id': randint(0, 10 ** 7)
            })


def add_photos(object_vk_api: object, list_photos: list) -> list:
    # format object_vk_api: <vk_api.vk_api.VkApi object at 0x0000025CC1F43460>
    # format list_photos: ['https://sun1-89.user...type=album', 'https://sun9-64.user...type=album', 'https://sun9-1.usera...type=album']

    '''Загружает и добавляет фотографии в список на обновление сообщения'''

    attachment_list = []
    uploader = vk_api.VkUpload(object_vk_api)
    for element in list_photos:
        img = requests.get(element).content
        name = element.partition('?')[0].split('/')[-1] # format 'DL1exc5mS4U.jpg'
        with open(f'test_photo\\{name}', 'wb') as f:
            f.write(img)
        img = uploader.photo_messages(f'test_photo\\{name}') # format [{'album_id': -64, 'date': 1671370522, 'id': 457239656, 'owner_id': -217703779, 'access_key': 'a105e88cf606399239', 'sizes': [...], 'text': '', 'user_id': 100}]
        media_id = str(img[0]['id']) # format '457239656'
        owner_id = str(img[0]['owner_id']) # format '-217703779'
        attachment_list.append(f'photo{owner_id}_{media_id}')
        os.remove(f'test_photo\\{name}')
    return attachment_list


def create_buttons(number: int) -> VkKeyboard:

    '''Создает цветные кнопки'''

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

def add_data_to_the_dictionary(object_vk_api: object, index: int,
                                sender_id: str, message_text: str, date: dict) -> dict:

    '''Добавляет данные полученные от пользователя в словарь'''

    if index - 1 == 0:
        if '-' in message_text:
            text = message_text.replace(' ', '').split('-')
        else:
            text = message_text.strip()
            text_list = []
            text_list.append(text)
            text_list.append(text)
            text = text_list
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
    date.setdefault(categories_of_questions[index - 1], text) # формат {'age': ['34', '57'], 'sex': '1', 'city': 'новосибирск'}
    return date, index


def event_handling_start(object_vk_api: object, message_text: str, variables: dict) -> dict:

    '''Обработка события СТАРТ. Бот задаёт вопросы и создает словарь'''

    sender_id = variables['id']
    variables = variables['fields']
    if message_text == 'сбросить':
        variables['count'] = 0
        keyboard = create_buttons(2)
        write_msg(object_vk_api, sender_id, bot_questions[variables['count']], keyboard)
        variables['filtr_dict'] = {}
        variables['count'] = 1
        variables['continue'] = True
        variables['fields']['number'] = 0
        return variables   
    elif message_text == 'отменить':
        variables['count'] = 0
        variables['start'] = False
        write_msg(object_vk_api, sender_id, 'Ок')
        variables['continue'] = True
        variables['filtr_dict'] = {}
        variables['fields']['number'] = 0
        return variables

    variables['filtr_dict'], variables['count'] = add_data_to_the_dictionary(
        object_vk_api, variables['count'], sender_id, message_text, variables['filtr_dict']
    )   # формат {'text': None, 'count': 3, 'start': True, 'continue': False, 'filtr_dict': {'age': [...], 'sex': '1', 'city': 'новосибирск'}, 'sql': {}, 'start_request': False, 'number': 0}
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
    return variables # формат {'text': None, 'count': 0, 'start': False, 'continue': False, 'filtr_dict': {'age': [...], 'sex': '1', 'city': 'новосибирск'}, 'sql': {}, 'start_request': False, 'number': 0}


def processing_a_simple_message(object_vk_api: object, message_text: str, variables: dict) -> dict:

    '''Обработка событий простых сообщений и нажатия кнопок'''

    sender_id = variables['id']
    variables = variables['fields']
    if message_text == "старт":
        keyboard = create_buttons(2)
        write_msg(object_vk_api, sender_id, bot_questions[variables['count']], keyboard)
        variables['count'] += 1
        variables['start'] = True
        variables['continue'] = True
        variables['filtr_dict'] = {}
        variables['number'] = 0
        variables['offset'] = 0
    elif message_text in list_button:
        if variables['end_list'] == True:
            write_msg(object_vk_api, sender_id, "Выполнено \U00002705")
            variables['end_list'] = False
        else:
            keyboard = create_buttons(4)
            write_msg(object_vk_api, sender_id, "Выполнено \U00002705", keyboard)
    elif message_text in ['привет', 'отменить']:
        pass
    else:
        write_msg(object_vk_api, sender_id, "Не поняла вашего ответа... \U0001F937\U0001F92F\U0001F914\U0001F60A")
    return variables


list_button = ['добавить в избранное', 'следующий', 'показать весь список', 'добавить в черный список']

bot_questions = [
    "Укажите возраст людей по образцу\nПример: 25 или 20-30 \U0001F609",
    "Укажите пол (жен - 1 \U0001F483 или муж - 2 \U0001F57A ):",
    "Укажите город: \U0001F3E1"
]

categories_of_questions = ['age', 'sex', 'city'] 


if __name__ == '__main__':
    pass