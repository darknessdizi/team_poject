from token_vk import token_vk_community
from random import randint
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor


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
    if number == 1:
        keyboard.add_button('Сбросить', buttons_colors[0])
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
                write_msg(event.user_id, "Не правильно указан возраст!!! Повторите ввод.")
                return date, index
    else:
        text = event.text.lower().replace('.', '')
    date.setdefault(categories_of_questions[index - 1], text)
    return date, index


def main():

    # Основной цикл
    count = 0
    start = False
    filtr_dict = {}

    for event in longpoll.listen():

        # Если пришло новое сообщение
        if event.type == VkEventType.MESSAGE_NEW:
        
            # Если оно имеет метку для меня(то есть бота)
            if event.to_me:

                request = event.text.lower().strip()
                if start:
                    # Активирована команда старт (поиск людей)
                    if request == 'сбросить':
                        count = 0
                    filtr_dict, count = add_data_to_the_dictionary(count, event, filtr_dict)
                    if count < len(text):
                        write_msg(event.user_id, text[count])
                        count += 1
                        continue
                    else:
                        start = False
                        count = 0
                        # Активируем цветные кнопки
                        keyboard = create_buttons(4)
                        write_msg(event.user_id, "Ок", keyboard)
                        # !!!!!!!!!!!!!! Для Маши - твой словарь здесь будет удален. Надо вызвать функцию поиска
                        filtr_dict = {}      
                else:
                    # Логика обычного ответа
                    if request == "привет":
                        write_msg(event.user_id, "Хай")
                    elif request == "фото": # это чисто тест загрузки фоток !!!
                        my_list = ["test_photo\kot.jpg", "test_photo\kot2.jpg", 
                                    "test_photo\kot3.jpg"]
                        attachment = add_photos(my_list)
                        send_photos(event.user_id, attachment)
                    elif request == "старт":
                        keyboard = create_buttons(1)
                        write_msg(event.user_id, text[count], keyboard)
                        count += 1
                        start = True
                    elif request in dict_func:
                        dict_func[request]()
                        write_msg(event.user_id, "Выполнено")
                    else:
                        write_msg(event.user_id, "Не поняла вашего ответа...")


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

text = [
    "Укажите возраст людей по образцу\nПример: 25 или 20-30 ",
    "Укажите пол (муж или жен):",
    "Укажте город:",
    "Укажите семейное положение искомых людей:"
]

categories_of_questions = ['возраст', 'пол', 'город', 'семья'] 


if __name__ == '__main__':
    main()
            
            