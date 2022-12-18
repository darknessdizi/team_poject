def get_ask_user_data(cur, user_id):
    '''достаем из базы данные пользователя'''
    cur.execute('''
        SELECT * FROM users
        WHERE id = %s;
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










def add_favourites(cur, id_user, contact_id, contact_name, age, sex, city):
    # format  id: 33579332
    # format  user_name: 'Юлия Волкова'
    # format  age: ['34', '57']
    # format  sex: '1'
    # format  city: 'новосибирск'

    '''Добавляем пользователя в список избранных'''

    cur.execute('''
        INSERT INTO favorites (id, user_id , name, age, sex, city)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;''',  
            (contact_id, id_user, contact_name, age, sex, city))
    return cur.fetchone()[0]

def add_photos(cur, list_photos, favorites_id):

    '''Прикрепляем ссылки на фото в список избранных'''

    for link in list_photos:
        cur.execute('''
            INSERT INTO photos (link , favorites_id)
                VALUES (%s, %s);''', 
                (link, favorites_id))

def black_list(cur, favorites_id):

    '''Добавляем к пользователю статус в черном списке'''

    print('black_list', cur.execute('''
        INSERT INTO black_list (favorites_id)
            VALUES (%s);''', 
            (favorites_id,)))
    # cur.execute('''
    #     INSERT INTO black_list (favorites_id)
    #         VALUES (%s);''', 
    #         (favorites_id,))

def get_favourites(cur, user_id):

    '''Выгружаем из базы данных список избранных'''
    
    cur.execute('''
        SELECT user_id, name, age, sex, city FROM favorites as f
        JOIN black_list as bl ON bl.favorites_id = f.id
        WHERE f.user_id = %s AND f.id != bl.favorites_id;
    ''', (user_id,))
    return cur.fetchall()

def add_ask_user(cur, user_id, user_name, user_age, user_city, user_sex):

    '''добавлем данные пользователя в базу данных (запрашивающий пользователь)'''

    cur.execute("""
        INSERT INTO users(id, user_name, user_age, user_city, user_sex)
        VALUES (%s, %s, %s, %s, %s);
        """, (user_id, user_name, user_age, user_city, user_sex))
    cur.execute('''
        SELECT * FROM users
        WHERE id = %s;
        ''', (user_id,))

    return cur.fetchone()


def drop_table(cur):
    cur.execute("""
        DROP TABLE black_list;
        DROP TABLE photos;
        DROP TABLE favorites;
        DROP TABLE users;       
    """)

    return 'Таблицы очищены'


def create_db(cur):
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
        id INTEGER UNIQUE PRIMARY KEY,
        user_name VARCHAR(40) NOT NULL,
        user_age VARCHAR(10) NOT NULL,
        user_city VARCHAR(20) NOT NULL,
        user_sex VARCHAR(20) NOT NULL
    );
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
        id INTEGER UNIQUE PRIMARY KEY, 
        user_id INTEGER REFERENCES users (id),
        name VARCHAR(40),
        age VARCHAR(40),
        sex VARCHAR(40),
        city VARCHAR(40)
    );
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS photos (
        id SERIAL PRIMARY KEY,
        link VARCHAR,
        favorites_id INTEGER REFERENCES favorites (id)
    );
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS black_list (
        id SERIAL PRIMARY KEY,
        favorites_id INTEGER REFERENCES favorites (id)
    );
    ''')

    return 'БД создана'



if __name__ == '__main__':
    pass