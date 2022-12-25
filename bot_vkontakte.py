import vk_api
import requests
import os
import base
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from random import randint
from token_vk import token_vk_community, token_vk
from vk_api.longpoll import VkLongPoll
from datetime import date


class BotVkontakte:

    '''Класс для работы пользователя с Api вконтакте'''

    def __init__(self, longpoll, session):
        self.longpoll = longpoll
        self.session = session


    def calculate_age(self, born: str) -> int:  

        '''Вычисляет возраст от даты рождения'''

        born = born.split(".")
        today = date.today()
        age = today.year - int(born[2]) - (
            (today.month, today.day) < (int(born[1]), int(born[0]))
        )
        return age


    def checking_the_user_in_the_database(self, 
        cur: object, sender_id: str, response: object) -> None: 

        '''Проверят подключившегося пользователя по базе данных, 
        
        если не находит, то добавляет в базу данных пользователя
        
        '''

        if not base.get_ask_user_data(cur, sender_id):
            print('В базе отсутствует')
            user_info = response.get_user(sender_id)
            user_info['age'] = self.calculate_age(user_info['age'])  
            if user_info['sex'] == 2:
                user_info['gender'] = 'Мужской'
            elif user_info['sex'] == 1:
                user_info['gender'] = 'Женский'
            else:
                user_info['gender'] = 'Пол не указан'
            if base.add_ask_user(cur, sender_id, user_info['user_name'],
                            user_info['age'], user_info['city'],
                            user_info['gender']):
                print('Пользователь добавлен в базу')
            else:
                print('Пользователь НЕ добавлен в базу')


    def the_command_to_greet(self, 
        cur: object, sender_id: str, object_vk_api: object) -> str:

        '''Функция отвечает на приветствие пользователя'''

        ask_user = base.get_ask_user_data(cur, sender_id)
        write_msg(
            object_vk_api, sender_id, 
            f"Здравствуйте, {ask_user[1]}!\n"
            f"Ваши параметры:\nГород: {ask_user[3]}\n"
            f"Пол: {ask_user[4]}\nВозраст: {ask_user[2]}\n"
            f"(Введите: старт\список) \U0001F60E"
        )
        return ask_user


    def checking_the_favorites_list(self, 
        cur: object, sender_id: str, object_vk_api: object) -> bool:

        '''Выводит в чат список избранных для указанного пользователя'''
        
        db_source = base.get_favourites(cur, sender_id) 
        if db_source:
            for item in db_source:
                age = self.calculate_age(item[1])
                city = item[2].upper()
                message_text = f'Имя: {item[0]}\nВозраст: {age}\nГород: {city}\n{item[3]}'
                write_msg(object_vk_api, sender_id, message_text)
        else:
            write_msg(object_vk_api, sender_id, f"Список избранных пуст")
        write_msg(object_vk_api, sender_id, "Выполнено \U00002705")
        return True



def connection() -> tuple:

    '''Создает объекты для работы с сообщениями в чат боте вконтакте,
    
    объект для работы пользователя с Api вконтакте и объект сообщества

    '''

    # Авторизуемся как сообщество
    authorize = vk_api.VkApi(token=token_vk_community)

    # Работа с сообщениями
    longpoll = VkLongPoll(authorize)

    user_session = vk_api.VkApi(token=token_vk)
    session = user_session.get_api()

    return longpoll, session, authorize


def user_support(event: object, 
    list_of_users: list, list_of_dicts: list) -> tuple:

    '''Отслеживает переменные каждого пользователя работающего с ботом'''

    if event.user_id in list_of_users: 
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


def write_msg(object_vk_api: object, 
    sender_id: str, message: str, keyboard=None) -> None:

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


def send_photos(object_vk_api: object, 
    sender_id: str, attachment: list) -> None:

    '''Отправляет метод и его параметры в Api вконтакте 
    
    для отправки сообщений в чат
    
    '''

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
        with open(f'{name}', 'wb') as f:
            f.write(img)
        img = uploader.photo_messages(f'{name}') 
        media_id = str(img[0]['id']) 
        owner_id = str(img[0]['owner_id']) 
        attachment_list.append(f'photo{owner_id}_{media_id}')
        os.remove(f'{name}')
    return attachment_list


def create_buttons(number: int) -> VkKeyboard:

    '''Создает объект с параметрами кнопок'''

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

    '''Добавляет ответы полученные от пользователя в словарь'''

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

    '''Обработка события СТАРТ. Бот задаёт вопросы и создает словарь'''

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

    '''Обработка событий простых сообщений и нажатия кнопок'''

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
        if variables['end_list'] == True:
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


def updates_the_list_of_people(
    variables: dict, respone: dict, object_vk_api: object, 
    response: object, cur: object) -> tuple:
    
    '''Обновляет список людей для вывода в чат бота'''

    variables['fields']['number'] = 0
    variables['fields']['offset'] += 1000
    variables, respone, photos = photo_requests_for_users(
        object_vk_api, response, cur, variables
    )
    return variables, respone, photos


def cancel_button(object_vk_api: object, variables: dict) -> dict:

    '''Обновление переменных при нажатии кнопки "Отменить"
    
    '''

    variables['count'] = 0
    variables['start'] = False
    variables['continue'] = False
    variables['filtr_dict'] = {}
    variables['fields']['number'] = 0
    variables['fields']['offset'] = 0
    write_msg(
        object_vk_api, variables['id'], 
        "Желаете найти кого-то другого? \U0001F914 Наберите команду старт. \U0001F920"
    )
    return variables


def save_to_favorites(cur: object, photos: list, 
    respone: list, variables: dict) -> str:

    '''Добавляет человека в список избранных'''

    id, name, bdate = respone[variables['fields']['number']] 
    if not base.checking_list_favorites(cur, id):
        sex = variables['fields']['filtr_dict'].get('sex')
        city = variables['fields']['filtr_dict'].get('city')
        link = f"https://vk.com/id{photos.get('owner_id')}"
        favorites_id = base.add_favourites(
            cur, id, name, bdate, sex, city, link
        )
        base.add_photos(cur, photos['href'], favorites_id)
    return id


def photo_requests_for_users(
    object_vk_api: object, response: object, 
    cur: object, variables: dict) -> tuple:

    '''Осуществляет запросы и поиск пользователей в Api вконтакте. 

    Проверяет их на наличие в базе данных. Выводит фотографии 
    
    в чат-бота
    
    '''

    respone = response.get_users(variables['fields']) 
    block_list = [i[4] for i in base.get_favourites(cur, variables['id'], True)]
    if respone is None:
        write_msg(
            object_vk_api, variables['id'], 
            "Ничего не найдено. Уточните параметры поиска"
        )
        variables['fields']['filtr_dict'] = {}
        photos = None
        return variables, respone, photos
    else:
        while True:
            if len(respone) == 0:
                # write_msg(object_vk_api, variables['id'], "Простите, людей не найдено")
                variables['fields']['offset'] += 1000 
                variables['fields']['number'] = 0
                respone = response.get_users(variables['fields'])
                continue
            elif respone[variables['fields']['number']][0] in block_list:
                variables['fields']['number'] += 1
                if len(respone) == variables['fields']['number']:
                    variables['fields']['number'] = 0
                    variables['fields']['offset'] += 1000
                    respone = response.get_users(variables['fields'])
                    continue
            else:
                photos = response.get_users_photo(
                    str(respone[variables['fields']['number']][0])
                )
                                    
                if photos is None:
                    keyboard = create_buttons(1)
                    write_msg(
                        object_vk_api, variables['id'], 
                        "\U000026D4 \U0001F6AB У пользователя нет фотографий.\nНажмите следующий. \U0001F914", 
                        keyboard
                    )
                    continue

                text = respone[variables['fields']['number']][1]         
                message = f"{text}\n https://vk.com/id{photos.get('owner_id')}"
                write_msg(object_vk_api, variables['id'], message) 

                attachment = add_photos(object_vk_api, photos.get('href')) 
                send_photos(object_vk_api, variables['id'], attachment)
                keyboard = create_buttons(4)
                write_msg(
                    object_vk_api, variables['id'], 
                    "Выполнено \U00002705", 
                    keyboard
                )
                return variables, respone, photos


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
