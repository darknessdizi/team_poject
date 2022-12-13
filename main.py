from token_vk import token_vk_community
from random import randint
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import psycopg2
import base
from login_sql import sql_authorization


class PostgreSQL:

    def __init__(self, **kwargs):
        self.connect = psycopg2.connect(
            dbname=kwargs['dbname'],
            user=kwargs['user'],
            password=kwargs['password']
        )
        self.connect.autocommit = True


def write_msg(user_id: str, message: str, keyboard=None) -> None:

    '''Отправляет сообщения и добавляет кнопки к сообщениям'''

    post = {
        'user_id': user_id, 
        'message': message, 
        'random_id': randint(0, 100000)
    }

    if keyboard != None:
        post['keyboard'] = keyboard.get_keyboard()
    else:
        post = post
        keyboard = VkKeyboard()
        post['keyboard'] = keyboard.get_empty_keyboard()

    vk.method('messages.send', post)


def send_photos(user_id: str, attachment: list) -> None:

    '''Отправляет фотографии пользователю'''

    for element in attachment:
        vk.method('messages.send', {
            'user_id': user_id, 
            'attachment': element,
            'random_id': randint(0, 100000)
            })


def add_photos(list_photos: list) -> list:

    '''Добавляет фотографии в список'''

    attachment_list = []
    uploader = vk_api.VkUpload(vk)
    for element in list_photos:
        img = uploader.photo_messages(element)
        media_id = str(img[0]['id'])
        owner_id = str(img[0]['owner_id'])
        attachment_list.append(f'photo{owner_id}_{media_id}')
    return attachment_list

def create_buttons(number: int) -> VkKeyboard:

    '''Создает цветные кнопки'''

    keyboard = VkKeyboard()
    buttons_colors = [VkKeyboardColor.PRIMARY, VkKeyboardColor.POSITIVE, 
                        VkKeyboardColor.NEGATIVE, VkKeyboardColor.SECONDARY]
    if number == 2:
        keyboard.add_button('Сбросить', buttons_colors[0])
        keyboard.add_line()
        keyboard.add_button('Отменить', buttons_colors[-1])
    elif number == 4:
        buttons = [i.capitalize() for i in dict_func]
        count = 0
        for btn, btn_color in zip(buttons, buttons_colors):
            if count == 2:
                keyboard.add_line()
            keyboard.add_button(btn, btn_color)
            count += 1
    return keyboard


def add_person_to_sql(*args, **kwargs):
    pass


def next_person(*args, **kwargs):
    pass


def show_the_full_list(*args, **kwargs):
    pass
    

def add_to_blacklist(*args, **kwargs):
    pass


def reset_filtr(*args, **kwargs):
    count = 0
    return count


def add_data_to_the_dictionary(index: int, event: object, date: dict) -> dict:

    '''Добавляет данные полученные от пользователя в словарь'''

    if index - 1 == 0:
        if '-' in event.text:
            text = event.text.replace(' ', '').split('-')
        else:
            text = event.text.strip()
        for element in text:
            if not element.isdigit():
                index = index - 1
                keyboard = create_buttons(2)
                write_msg(event.user_id, "Не правильно указан возраст!!! Повторите ввод.", keyboard)
                return date, index
    else:
        text = event.text.lower().replace('.', '')
    date.setdefault(categories_of_questions[index - 1], text)
    return date, index

def event_handling_start(request, event, variables):

    '''Обработка события СТАРТ. Бот задаёт вопросы и создает словарь'''

    if request == 'сбросить':
        variables['count'] = 0
    elif request == 'отменить':
        variables['count'] = 0
        variables['start'] = False
        write_msg(event.user_id, 'Ок')
        variables['continue'] = True
        return variables

    variables['filtr_dict'], variables['count'] = add_data_to_the_dictionary(
        variables['count'], event, variables['filtr_dict']
    )
    if variables['count'] < len(bot_questions):
        keyboard = create_buttons(2)
        write_msg(event.user_id, bot_questions[variables['count']], keyboard)
        variables['count'] += 1
        variables['continue'] = True
        return variables
    else:
        variables['start'] = False
        variables['count'] = 0
        # Активируем цветные кнопки
        keyboard = create_buttons(4)
        write_msg(event.user_id, "Ок", keyboard)
        # !!!!!!!!!!!!!! Для Маши - твой словарь здесь будет удален. Надо вызвать функцию поиска
        variables['filtr_dict'] = {} 
    return variables
                    

def processing_a_simple_message(request, event, variables):

    '''Обработка событий простых сообщений и нажатия кнопок'''

    if request == "привет":
        write_msg(event.user_id, "Хай")
    elif request == "фото": # это чисто тест загрузки фоток !!!
        my_list = ["test_photo\kot.jpg", "test_photo\kot2.jpg", 
                    "test_photo\kot3.jpg"]
        attachment = add_photos(my_list)
        send_photos(event.user_id, attachment)
    elif request == "старт":
        keyboard = create_buttons(2)
        write_msg(event.user_id, bot_questions[variables['count']], keyboard)
        variables['count'] += 1
        variables['start'] = True
    elif request in dict_func:
        dict_func[request](**variables['sql'])
        keyboard = create_buttons(4)
        write_msg(event.user_id, "Выполнено", keyboard)
    else:
        write_msg(event.user_id, "Не поняла вашего ответа...")
    return variables

    
def main():

    # Основной цикл
    variables = {'count': 0, 'start': False, 'continue': False, 'filtr_dict': {}, 'sql': {}}

    # Создание объекта для подключения к базе данных
    sql_cursor = PostgreSQL(**sql_authorization)
    # base.drop_table(sql_cursor.connect.cursor())
    base.create_db(sql_cursor.connect.cursor())


    for event in longpoll.listen():

        # Если пришло новое сообщение
        if event.type == VkEventType.MESSAGE_NEW:
        
            # Если оно имеет метку для меня(то есть бота)
            if event.to_me:

                request = event.text.lower().strip()
                if variables['start']:
                    # Активирована команда старт (поиск людей)
                    variables = event_handling_start(request, event, variables)
                    if variables['continue']:
                        variables['continue'] = False
                        continue
                else:
                    # Логика обычного ответа
                    variables = processing_a_simple_message(request, event, variables)
                    

# Авторизуемся как сообщество
vk = vk_api.VkApi(token=token_vk_community)

# Работа с сообщениями
longpoll = VkLongPoll(vk)

dict_func = {
    'добавить в избранное': add_person_to_sql,
    'следующий': next_person,
    'показать весь список': show_the_full_list,
    'добавить в черный список': add_to_blacklist
}

bot_questions = [
    "Укажите возраст людей по образцу\nПример: 25 или 20-30 ",
    "Укажите пол (муж или жен):",
    "Укажте город:",
    "Укажите семейное положение искомых людей:"
]

categories_of_questions = ['возраст', 'пол', 'город', 'семья'] 


if __name__ == '__main__':
    main()
            