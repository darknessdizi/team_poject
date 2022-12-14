from vk_api import VkUpload
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from random import randint


def write_msg(object_vk_api: object, user_id: str, message: str, keyboard=None) -> None:

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

    object_vk_api.method('messages.send', post)


def send_photos(object_vk_api: object, user_id: str, attachment: list) -> None:

    '''Отправляет фотографии пользователю'''

    for element in attachment:
        object_vk_api.method('messages.send', {
            'user_id': user_id, 
            'attachment': element,
            'random_id': randint(0, 100000)
            })


def add_photos(object_vk_api: object, list_photos: list) -> list:

    '''Добавляет фотографии в список'''

    attachment_list = []
    uploader = VkUpload(object_vk_api)
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


def add_data_to_the_dictionary(object_vk_api: object, index: int, event: object, date: dict) -> dict:

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
                write_msg(object_vk_api, event.user_id, "Не правильно указан возраст!!! Повторите ввод.", keyboard)
                return date, index
    else:
        text = event.text.lower().replace('.', '')
    date.setdefault(categories_of_questions[index - 1], text)
    return date, index


def event_handling_start(object_vk_api: object, request, event, variables) -> dict:

    '''Обработка события СТАРТ. Бот задаёт вопросы и создает словарь'''

    if request == 'сбросить':
        variables['count'] = 0
    elif request == 'отменить':
        variables['count'] = 0
        variables['start'] = False
        write_msg(object_vk_api, event.user_id, 'Ок')
        variables['continue'] = True
        return variables

    variables['filtr_dict'], variables['count'] = add_data_to_the_dictionary(
        object_vk_api, variables['count'], event, variables['filtr_dict']
    )
    if variables['count'] < len(bot_questions):
        keyboard = create_buttons(2)
        write_msg(object_vk_api, event.user_id, bot_questions[variables['count']], keyboard)
        variables['count'] += 1
        variables['continue'] = True
        return variables
    else:
        variables['start'] = False
        variables['count'] = 0
        # Активируем цветные кнопки
        keyboard = create_buttons(4)
        write_msg(object_vk_api, event.user_id, "Ок", keyboard)
        # !!!!!!!!!!!!!! Для Маши - твой словарь здесь будет удален. Надо вызвать функцию поиска
        variables['filtr_dict'] = {} 
    return variables
                    

def processing_a_simple_message(object_vk_api: object, request, event, variables) -> dict:

    '''Обработка событий простых сообщений и нажатия кнопок'''

    if request == "привет":
        # write_msg(object_vk_api, event.user_id, "Хай")
        pass
    elif request == "фото": # это чисто тест загрузки фоток !!!
        my_list = ["test_photo\kot.jpg", "test_photo\kot2.jpg", 
                    "test_photo\kot3.jpg"]
        attachment = add_photos(object_vk_api, my_list)
        send_photos(object_vk_api, event.user_id, attachment)
    elif request == "старт":
        keyboard = create_buttons(2)
        write_msg(object_vk_api, event.user_id, bot_questions[variables['count']], keyboard)
        variables['count'] += 1
        variables['start'] = True
    elif request in dict_func:
        dict_func[request](**variables['sql'])
        keyboard = create_buttons(4)
        write_msg(object_vk_api, event.user_id, "Выполнено", keyboard)
    else:
        write_msg(object_vk_api, event.user_id, "Не поняла вашего ответа...")
    return variables


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

categories_of_questions = ['возраст', 'пол', 'город', 'статус'] 


if __name__ == '__main__':
    pass