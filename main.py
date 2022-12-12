from token_vk import token_vk_community
from random import randint
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor


def write_msg(user_id: str, message: str, keyboard=None) -> None:

    '''Отправляет сообщения и создает кнопки'''

    post = {
        'user_id': user_id, 
        'message': message, 
        'random_id': randint(0, 1000)
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
            'random_id': randint(0, 1000)
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

def create_buttons():
    keyboard = VkKeyboard()
    buttons = ['Добавить в избранное', 'Следующий', 'Показать весь список', 
                'Добавить в черный список']
    buttons_colors = [VkKeyboardColor.PRIMARY, VkKeyboardColor.POSITIVE, 
                        VkKeyboardColor.NEGATIVE, VkKeyboardColor.SECONDARY]
    count = 0
    for btn, btn_color in zip(buttons, buttons_colors):
        if count == 2:
            keyboard.add_line()
        keyboard.add_button(btn, btn_color)
        count += 1
    return keyboard


def add_person_to_sql():
    pass


def next_person():
    pass


def show_the_full_list():
    pass
    

def add_to_blacklist():
    pass


def main():
    # Основной цикл
    for event in longpoll.listen():

        # Если пришло новое сообщение
        if event.type == VkEventType.MESSAGE_NEW:
        
            # Если оно имеет метку для меня(то есть бота)
            if event.to_me:
            
                # Сообщение от пользователя
                request = event.text.lower().strip()
                
                # Логика ответа
                if request == "привет":
                    write_msg(event.user_id, "Хай")
                elif request == "фото":
                    my_list = ["test_photo\kot.jpg", "test_photo\kot2.jpg", 
                                "test_photo\kot3.jpg"]
                    attachment = add_photos(my_list)
                    send_photos(event.user_id, attachment)
                elif request == "start":
                    keyboard = create_buttons()
                    write_msg(event.user_id, "Ок", keyboard)
                elif request == 'добавить в избранное':
                    print("Здесь человек добавляется в базу данных")
                    add_person_to_sql()
                    write_msg(event.user_id, "Выполнено")
                elif request == 'следующий':
                    print("Здесь выдаются данные на следуюущего человека")
                    next_person()
                    write_msg(event.user_id, "Выполнено")
                elif request == 'показать весь список':
                    print("Здесь отправляется полный список избранных людей")
                    show_the_full_list()
                    write_msg(event.user_id, "Выполнено")
                elif request == 'добавить в черный список':
                    print("Человек заносится в черный список")
                    add_to_blacklist()
                    write_msg(event.user_id, "Выполнено")
                else:
                    write_msg(event.user_id, "Не поняла вашего ответа...")


# Авторизуемся как сообщество
vk = vk_api.VkApi(token=token_vk_community)

# Работа с сообщениями
longpoll = VkLongPoll(vk)


if __name__ == '__main__':
    main()
            
            