from token_vk import token_vk_community
from random import randint
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import psycopg2
from VKinder import Base
from datetime import date



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



def add_to_database(cur, sender_id, result):
    '''запись полученных данных из поиска в базу данных'''
    for i_user in result:
        if not Base.check_find_user(cur, i_user['id']):
            if Base.add_find_users(cur, i_user['id'], sender_id, i_user['user_name'], i_user['url']):
                for item in i_user['attachment']:
                    Base.add_find_users_photos(cur, i_user['id'], item)
    return True

def get_from_database(cur, authorize, counter, sender_id):
    '''забрать данные о найденном пользователе из базы данных'''
    if counter < Base.count_db(cur)[0]:
        flag = True
        while flag and counter < Base.count_db(cur)[0]:
            db_source = Base.get_black_users(cur, sender_id, counter)
            if db_source:
                users = {'id': db_source[0],
                         'name': f'{db_source[1]} {db_source[2]}',
                         'url': db_source[3],
                         'attachment': add_data_to_the_dictionary(Base.get_photo(cur, db_source[0]))}
                write_msg(authorize, sender_id, f"{users['name']}\n{users['url']}",
                              users['attachment'])
                write_msg(authorize, sender_id, 'Смотреть дальше/ В список избранных/ В чёрный список)')
                flag = False
            counter += 1
    else:
        write_msg(authorize, sender_id, 'Смотреть дальше/В список избранных)')
        counter = 1
    return counter

def data_conversion(db_source, cur):
    '''Преобразует данные из базы данных для бота '''
    users = list()
    for item in db_source:
        users.append({'id': item[0], 'name': f'{item[1]} {item[2]}', 'url': item[3]})
    return users



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


def calculate_age(born):
    born = born.split(".")
    today = date.today()
    return today.year - int(born[2]) - ((today.month, today.day) < (int(born[1]), int(born[0])))


def connection():
    authorize = vk_api.VkApi(token=token_vk_community)
    longpoll = VkLongPoll(authorize)
    user_session = vk_api.VkApi(token=token_vk_community)
    session = user_session.get_api()
    return longpoll, session, authorize


def main():
    # Основной цикл
    variables = {'count': 0, 'start': False, 'continue': False, 'filtr_dict': {}, 'sql': {}}

    # Создание объекта для подключения к базе данных
    sql_cursor = PostgreSQL(**sql_authorization)
    # base.drop_table(sql_cursor.connect.cursor())
    Base.create_db(sql_cursor.connect.cursor())

    longpoll, session = connection()
    with sql_cursor.cursor() as cur:
        # print(DB.drop_table(cur)) #если нужно сбросить БД
        print(Base.create_db(cur))

    for event in longpoll.listen():

        # запрос данных пользователя
        if event.type == VkEventType.MESSAGE_NEW:
            sender_id = event.user_id
            message = event.text

            if not Base.get_ask_user_data(cur, sender_id):
                print('в базе отсутствует')
                user_info = session.account.getProfileInfo(user_id=sender_id)
                user_info['age'] = calculate_age(user_info['bdate'])
                if user_info['sex'] == 2:
                    user_info['gender'] = 'Мужской'
                elif user_info['sex'] == 1:
                    user_info['gender'] = 'Женский'
                else:
                    user_info['gender'] = 'Пол не указан'

                if Base.add_ask_user(cur, user_info['id'], user_info['user_name'],
                                   user_info['age'], user_info['city']['id'],
                                   user_info['gender']):
                    sql_cursor.commit()
                    print('пользователь добавлен в базу')
                else:
                    print('пользователь НЕ добавлен в базу')

            if message.lower() == "привет":
                print(f'Пользователь = {Base.get_ask_user_data(cur, sender_id)}')

                ask_user = Base.get_ask_user_data(cur, sender_id)
                message(sender_id, f"Здравствуйте, {ask_user[1]}!\n"
                                                    f"Ваши параметры:\nГород: {ask_user[4]}\n"
                                                    f"Пол: {ask_user[6]}\nВозраст: {ask_user[3]}\n"
                                                    f"(Начать поиск\Смотреть список избранных)")

            elif message.lower() in ['Смотреть список избранных']:
                if Base.get_favourites(cur, sender_id):
                    db_source = Base.get_favourites(cur, sender_id)
                    favourites = data_conversion(db_source, cur)
                    for item in favourites:
                        message(sender_id, f"{item['name']}\n{item['url']}")
                    message(sender_id, "Просмотреть данные")
                else:
                    message(sender_id, f"Список избранных пуст")


# Авторизуемся как сообщество
vk = vk_api.VkApi(token=token_vk_community)


if __name__ == '__main__':
    main()
