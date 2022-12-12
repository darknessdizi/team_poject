from token_vk import token_vk_community
from random import randint
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType


def write_msg(user_id: str, message: str) -> None:
    vk.method('messages.send', {
        'user_id': user_id, 
        'message': message, 
        'random_id': randint(0, 1000)
        })

def send_photo(user_id: str, attachment: list) -> None:
    for element in attachment:
        vk.method('messages.send', {
            'user_id': user_id, 
            'attachment': element,
            'random_id': randint(0, 1000)
            })

def add_photos(list_photos: list) -> list:
    attachment_list = []
    uploader = vk_api.VkUpload(vk)
    for element in list_photos:
        img = uploader.photo_messages(element)
        media_id = str(img[0]['id'])
        owner_id = str(img[0]['owner_id'])
        attachment_list.append(f'photo{owner_id}_{media_id}')
    return attachment_list

def main():
    # Основной цикл
    for event in longpoll.listen():

        # Если пришло новое сообщение
        if event.type == VkEventType.MESSAGE_NEW:
        
            # Если оно имеет метку для меня(то есть бота)
            if event.to_me:
            
                # Сообщение от пользователя
                request = event.text
                
                # Каменная логика ответа
                if request == "привет":
                    write_msg(event.user_id, "Хай")
                elif request == "пока":
                    write_msg(event.user_id, "Пока((")
                elif request == "как дела":
                    write_msg(event.user_id, "не плохо")
                elif request == "фото":
                    my_list = ['test_photo\kot.jpg', 'test_photo\kot2.jpg', 'test_photo\kot3.jpg']
                    attachment = add_photos(my_list)
                    send_photo(event.user_id, attachment)
                else:
                    write_msg(event.user_id, "Не поняла вашего ответа...")


# Авторизуемся как сообщество
vk = vk_api.VkApi(token=token_vk_community)

# Работа с сообщениями
longpoll = VkLongPoll(vk)


if __name__ == '__main__':
    main()
            
            