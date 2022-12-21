def get_ask_user_data(cur, user_id):
    '''достаем из базы данные пользователя'''
    cur.execute('''
        SELECT * FROM users
        WHERE id = %s;
        ''', (user_id,))
    return cur.fetchone()


def checking_list_favorites(cur, contact_id):

    '''Проверяем список избранных на наличие человека в базе'''

    cur.execute('''
        SELECT f.id FROM Favorites as f 
	        WHERE f.id = %s;
            ''', (contact_id,))
    return cur.fetchone()


def add_favourites(cur, contact_id, contact_name, bdate, sex, city, link):

    '''Добавляем пользователя в список избранных'''

    cur.execute('''
        INSERT INTO Favorites (id, name, bdate, sex, city, link)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;
        ''', (contact_id, contact_name, bdate, sex, city, link))
    return cur.fetchone()[0]


def add_a_human_user_relationship(cur, users_id, favorites_id, status):

    '''Создаем связь пользователя и избранного человека'''
    
    cur.execute('''
        INSERT INTO Users_Favorites (users_id, favorites_id, block_status)
                VALUES (%s, %s, %s);
        ''', (users_id, favorites_id, status))


def add_photos(cur, list_photos, favorites_id):

    '''Прикрепляем ссылки на фото в список избранных'''

    for link in list_photos:
        cur.execute('''
            INSERT INTO photos (link , favorites_id)
                VALUES (%s, %s);''', 
                (link, favorites_id))


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


def checking_the_human_user_connection(cur, user_id, favorites_id):

    cur.execute('''
        SELECT * FROM Users_Favorites
        WHERE users_id = %s AND favorites_id = %s;
        ''', (user_id, favorites_id))
    
    return cur.fetchall()


def add_block_list(cur, user_id, favorites_id):

    '''Добавляем к пользователю статус в черном списке'''

    cur.execute('''
        UPDATE Users_Favorites 
        SET block_status = TRUE 
        WHERE users_id = %s AND favorites_id = %s;
        ''', (user_id, favorites_id))


def del_block_list(cur, user_id, favorites_id):

    '''Добавляем к пользователю статус в черном списке'''

    cur.execute('''
        UPDATE Users_Favorites 
        SET block_status = FALSE 
        WHERE users_id = %s AND favorites_id = %s;
        ''', (user_id, favorites_id))



# def add_find_users(cur, f_user_id, user_id, f_user_name, user_url):
#     '''добавляем в базу данных всех найденных людей'''
#     cur.execute("""
#         INSERT INTO find_users(f_user_id, user_id, f_user_name, user_url, favourites)
#         VALUES (%s, %s, %s, %s, %s, %s);
#         """, (f_user_id, user_id, f_user_name, user_url, 0))
#     cur.execute('''
#         SELECT * FROM find_users
#         WHERE f_user_id = %s;
#         ''', (f_user_id,))
#     return cur.fetchone()


# def get_find_users(cur, user_id, iterator):
#     '''получаем данные из базы о найденных пользователях'''
#     cur.execute('''
#         SELECT f_user_id, f_user_name, user_url FROM find_users
#         WHERE user_id = %s AND favourites < 1 AND iterator = %s;
#     ''', (user_id, iterator))
#     return cur.fetchone()


# def get_photo(cur, f_user_id):
#     '''получаем фото из базы данных'''
#     cur.execute('''
#         SELECT photo_str FROM photos
#         WHERE f_user_ids = %s;
#     ''', (f_user_id,))
#     return cur.fetchall()


# def add_find_users_photos(cur, f_user_id, photo_str):
#     '''добавляем в таблицу фото найденных людей'''
#     cur.execute('''
#         INSERT INTO photos(f_user_ids, photo_str)
#         VALUES (%s, %s);
#         ''', (f_user_id, photo_str))
#     cur.execute('''
#         SELECT * FROM photos
#         WHERE f_user_ids = %s;
#         ''', (f_user_id,))
#     return cur.fetchone()


# def get_favourites(cur):

#     '''Выгружаем из базы данных список избранных'''
    
#     cur.execute('''
#         SELECT f.name, f.age, f.city 
#         FROM favorites as f
# 	    WHERE f.block_list = False ;
#         ''')
    
#     return cur.fetchall()



# def add_black_list(cur, iterator, flag):
#     '''добавляем в черный список'''
#     cur.execute('''
#         UPDATE find_users SET black_list = %s WHERE iterator = %s;
#     ''', (flag, iterator))
#     cur.execute('''
#         SELECT black_list FROM find_users
#         WHERE iterator = %s;
#     ''', (iterator,))
#     return cur.fetchone()


# def get_black_list(cur, user_id):
#     '''Выгружаем из базы данных черный список'''
#     cur.execute('''
#         SELECT f_user_id, f_user_name, user_url FROM find_users
#         WHERE user_id = %s AND black_list = %s;
#     ''', (user_id, 1))
#     return cur.fetchall()

# def add_block_list(cur, user_id):

#     '''Добавляем к пользователю статус в черном списке'''

#     cur.execute('''
#         UPDATE favorites 
#         SET block_list = TRUE 
#         WHERE id = %s;
#         ''', (user_id,))

# def del_block_list(cur, user_id):

#     '''Снимаем у пользователю статус в черном списке'''

#     cur.execute('''
#         UPDATE favorites 
#         SET block_list = False 
#         WHERE id = %s;
#         ''', (user_id,))
            
def drop_table(cur):
    cur.execute("""
        DROP TABLE Users_Favorites;
        DROP TABLE Photos;
        DROP TABLE Favorites;
        DROP TABLE Users;       
    """)

    return 'Таблицы очищены'


def create_db(cur):
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Users (
        id INTEGER UNIQUE PRIMARY KEY,
        user_name VARCHAR(40) NOT NULL,
        user_age VARCHAR(10) NOT NULL,
        user_city VARCHAR(20) NOT NULL,
        user_sex VARCHAR(20) NOT NULL
    );
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Favorites (
        id INTEGER UNIQUE PRIMARY KEY, 
        name VARCHAR(40),
        bdate VARCHAR(40),
        sex VARCHAR(40),
        city VARCHAR(40),
        link VARCHAR
    );
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS Users_Favorites (
	id SERIAL PRIMARY KEY,
	users_id INTEGER NOT NULL REFERENCES Users (id),
	favorites_id INTEGER NOT NULL REFERENCES Favorites (id),
    block_status BOOLEAN
    );
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Photos (
        id SERIAL PRIMARY KEY,
        link VARCHAR,
        favorites_id INTEGER REFERENCES Favorites (id)
    );
    ''')

    return 'БД создана'



if __name__ == '__main__':
    pass