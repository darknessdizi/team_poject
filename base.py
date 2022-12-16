import psycopg2
from datetime import date
import bot_vkontakte as bot
from VKinder import VKinder


class PostgreSQL:

    def __init__(self, **kwargs):
        self.connect = psycopg2.connect(
            dbname=kwargs['dbname'],
            user=kwargs['user'],
            password=kwargs['password']
        )
        self.connect.autocommit = True


def drop_table(cur):
    cur.execute("""
        DROP TABLE photos;
        DROP TABLE find_users;
        DROP TABLE ask_user;       
    """)

    return 'Таблицы очищены'


def create_db(cur):
    cur.execute('''
        CREATE TABLE IF NOT EXISTS ask_user (
        user_id INTEGER UNIQUE PRIMARY KEY,
        user_name VARCHAR(40) NOT NULL,
        user_age VARCHAR(10) NOT NULL,
        user_city VARCHAR(20) NOT NULL,
        user_sex VARCHAR(20) NOT NULL
    );
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS find_users (
        f_user_id INTEGER UNIQUE PRIMARY KEY,
        user_id INTEGER REFERENCES ask_user(user_id),
        f_user_name VARCHAR(40) NOT NULL,
        user_url VARCHAR(40) NOT NULL UNIQUE,
        favourites INTEGER,
        iterator SERIAL
    );
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS photos (
        id SERIAL PRIMARY KEY,
        f_user_ids INTEGER REFERENCES find_users(f_user_id),
        photo_str VARCHAR(40)
    );
    ''')
    return 'БД создана'


def add_ask_user(cur, user_id, user_name, user_age, user_city, user_sex):
    '''добавлем данные пользователя в базу данных (запрашивающий пользователь)'''
    cur.execute("""
        INSERT INTO ask_user(user_id, user_name, user_age, user_city, user_sex)
        VALUES (%s, %s, %s, %s, %s);
        """, (user_id, user_name, user_age, user_city, user_sex))
    cur.execute('''
        SELECT * FROM ask_user
        WHERE user_id = %s;
        ''', (user_id,))

    return cur.fetchone()


def get_ask_user_data(cur, user_id):
    '''достаем из базы данные пользователя'''
    cur.execute('''
        SELECT * FROM ask_user
        WHERE user_id = %s;
        ''', (user_id,))
    return cur.fetchone()


def add_find_users(cur, f_user_id, user_id, f_user_name, user_url):
    '''добавляем в базу данных всех найденных людей'''
    cur.execute("""
        INSERT INTO find_users(f_user_id, user_id, f_user_name, user_url, favourites)
        VALUES (%s, %s, %s, %s, %s, %s);
        """, (f_user_id, user_id, f_user_name, user_url, 0))
    cur.execute('''
        SELECT * FROM find_users
        WHERE f_user_id = %s;
        ''', (f_user_id,))
    return cur.fetchone()




def get_find_users(cur, user_id, iterator):
    '''получаем данные из базы о найденных пользователях'''
    cur.execute('''
        SELECT f_user_id, f_user_name, user_url FROM find_users
        WHERE user_id = %s AND favourites < 1 AND iterator = %s;
    ''', (user_id, iterator))
    return cur.fetchone()


def get_photo(cur, f_user_id):
    '''получаем фото из базы данных'''
    cur.execute('''
        SELECT photo_str FROM photos
        WHERE f_user_ids = %s;
    ''', (f_user_id,))
    return cur.fetchall()


def add_find_users_photos(cur, f_user_id, photo_str):
    '''добавляем в таблицу фото найденных людей'''
    cur.execute('''
        INSERT INTO photos(f_user_ids, photo_str)
        VALUES (%s, %s);
        ''', (f_user_id, photo_str))
    cur.execute('''
        SELECT * FROM photos
        WHERE f_user_ids = %s;
        ''', (f_user_id,))
    return cur.fetchone()


def add_favourites(cur, iterator, flag):
    '''добавляем в список избранных'''
    cur.execute('''
        UPDATE find_users SET favourites = %s WHERE iterator = %s;
    ''', (flag, iterator))
    cur.execute('''
        SELECT favourites FROM find_users
        WHERE iterator = %s;
    ''', (iterator,))
    return cur.fetchone()


def get_favourites(cur, user_id):
    '''Выгружаем из базы данных список избранных'''
    cur.execute('''
        SELECT f_user_id, f_user_name, user_url FROM find_users
        WHERE user_id = %s AND favourites = %s;
    ''', (user_id, 1))
    return cur.fetchall()


def add_blacklist(cur, iterator, flag):
    '''добавляем в черный список'''
    cur.execute('''
        UPDATE find_users SET blacklist = %s WHERE iterator = %s;
    ''', (flag, iterator))
    cur.execute('''
        SELECT blacklist FROM find_users
        WHERE iterator = %s;
    ''', (iterator,))
    return cur.fetchone()


def get_blacklist(cur, user_id):
    '''Выгружаем из базы данных черный список'''
    cur.execute('''
        SELECT f_user_id, f_user_name, user_url FROM find_users
        WHERE user_id = %s AND blacklist = %s;
    ''', (user_id, 1))
    return cur.fetchall()


def calculate_age(born):
    born = born.split(".")
    today = date.today()
    return today.year - int(born[2]) - ((today.month, today.day) < (int(born[1]), int(born[0])))


def add_to_database(cur, sender_id, result):
    '''Пишет полученные данные из поиска в базу данных'''
    for i_user in result:
        if not check_find_user(cur, i_user['id']):  # Где эта функция ?????????
            if add_find_users(cur, i_user['id'], sender_id, i_user['user_name'], i_user['url']):
                for item in i_user['attachment']:
                    add_find_users_photos(cur, i_user['id'], item)
    return True


def checking_the_user_in_the_database(cur, sender_id, response):

    if not get_ask_user_data(cur, sender_id):
        print('в базе отсутствует')
        user_info = response.get_user(sender_id)               
        user_info['age'] = calculate_age(user_info['age'])
        if user_info['sex'] == 2:
            user_info['gender'] = 'Мужской'
        elif user_info['sex'] == 1:
            user_info['gender'] = 'Женский'
        else:
            user_info['gender'] = 'Пол не указан'
        if add_ask_user(cur, sender_id, user_info['user_name'],
                                user_info['age'], user_info['city'],
                                user_info['gender']):
            print('пользователь добавлен в базу')
        else:
            print('пользователь НЕ добавлен в базу')


def the_command_to_greet(cur, sender_id: str, object_vk_api: object):

    '''Функция отвечает на приветствие пользователя'''

    ask_user = get_ask_user_data(cur, sender_id)
    print(f'Пользователь = {ask_user}')

    ask_user = get_ask_user_data(cur, sender_id)
    bot.write_msg(object_vk_api, sender_id, f"Здравствуйте, {ask_user[1]}!\n"
                                            f"Ваши параметры:\nГород: {ask_user[3]}\n"
                                            f"Пол: {ask_user[4]}\nВозраст: {ask_user[2]}\n"
                                            f"(Введите: старт\список) \U0001F60E")
    return ask_user


def data_conversion(db_source):
    '''Преобразует данные из базы данных для бота '''
    users = list()
    for item in db_source:
        users.append({'id': item[0], 'name': f'{item[1]} {item[2]}', 'url': item[3]})
    return users
    

def checking_the_favorites_list(cur, sender_id: str, object_vk_api: object):
    if get_favourites(cur, sender_id):
        db_source = get_favourites(cur, sender_id)
        favourites = data_conversion(db_source)
        for item in favourites:
            bot.write_msg(object_vk_api, sender_id, f"{item['name']}\n{item['url']}")
            bot.write_msg(object_vk_api, sender_id, "Просмотреть данные")
    else:
        bot.write_msg(object_vk_api, sender_id, f"Список избранных пуст")
        return True 
    return False


def search_function(cur, sender_id: str, object_vk_api: object, ask_user, session, longpoll):
    if get_favourites(cur, sender_id):
        bot.write_msg(object_vk_api, sender_id, f"Поиск...")

        v_kinder = VKinder(longpoll, session)
        result = v_kinder.find_user(ask_user)

        if add_to_database(cur, ask_user[0], result):
            print('Добавлено в базу')
            # sql_cursor.commit()
            bot.write_msg(object_vk_api, sender_id, "Данные записаны в базу")
        else:
            print('Ошибка')
    else:
        bot.write_msg(object_vk_api, sender_id, "Смотреть данные")


if __name__ == '__main__':
    pass