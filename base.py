import psycopg2
from datetime import date


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
        if not base.check_find_user(cur, i_user['id']):
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