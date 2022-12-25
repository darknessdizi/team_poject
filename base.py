# В модуле реализованы функции по прямому обращению к БД для создания/удаления таблиц,
# создания/записи в список избранных/черный список  пользоватей, проверки статуса пользователя

import psycopg2


class PostgreSQL:

    '''Класс для подключения к базе данных.'''

    def __init__(self, **kwargs):
        self.connect = psycopg2.connect(
            dbname=kwargs['dbname'],
            user=kwargs['user'],
            password=kwargs['password']
        )
        self.connect.autocommit = True
        

def get_ask_user_data(cur: object, user_id: str) -> tuple:

    '''Достаем из базы данные пользователя.'''

    cur.execute('''
        SELECT * FROM users
        WHERE id = %s;
        ''', (user_id,))
    return cur.fetchone()

def checking_list_favorites(cur: object, contact_id: str) -> tuple:

    '''Проверяем список избранных на наличие человека в базе.'''

    cur.execute('''
        SELECT f.id FROM Favorites as f
        WHERE f.id = %s;
        ''', (contact_id,))
    return cur.fetchone()

def add_favourites(
    cur: object, contact_id: str, contact_name: str, 
    bdate: str, sex: str, city: str, link: str) -> int:

    '''Добавляем пользователя в список избранных.'''

    cur.execute('''
        INSERT INTO Favorites (id, name, bdate, sex, city, link)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;
        ''', (contact_id, contact_name, bdate, sex, city, link))
    return cur.fetchone()[0]

def add_a_human_user_relationship(
    cur: object, users_id: str, favorites_id: str, status: bool) -> None:

    '''Создаем связь пользователя и избранного человека.'''

    cur.execute('''
        INSERT INTO Users_Favorites (users_id, favorites_id, block_status)
                VALUES (%s, %s, %s);
        ''', (users_id, favorites_id, status))

def add_photos(cur: object, list_photos: list, favorites_id: str) -> None:

    '''Прикрепляем ссылки на фото в список избранных.'''

    for link in list_photos:
        cur.execute('''
            INSERT INTO photos (link , favorites_id)
                VALUES (%s, %s);''',
                    (link, favorites_id))

def add_ask_user(
    cur: object, user_id: str, user_name: str, 
    user_age: str, user_city: str, user_sex: str) -> tuple:

    '''Добавлем данные пользователя в базу данных 
    
    (запрашивающий пользователь).
    
    '''

    cur.execute("""
        INSERT INTO users(id, user_name, user_age, user_city, user_sex)
        VALUES (%s, %s, %s, %s, %s);
        """, (user_id, user_name, user_age, user_city, user_sex))
    cur.execute('''
        SELECT * FROM users
        WHERE id = %s;
        ''', (user_id,))
    return cur.fetchone()

def checking_the_human_user_connection(
    cur: object, user_id: str, favorites_id: str) -> tuple:

    '''Проверяет есть ли связь человека с подключенным пользоватеелем.'''

    cur.execute('''
        SELECT * FROM Users_Favorites
        WHERE users_id = %s AND favorites_id = %s;
        ''', (user_id, favorites_id))
    return cur.fetchall()

def add_block_list(cur: object, user_id: str, favorites_id: str) -> tuple:

    '''Добавляем к пользователю статус в черном списке.'''

    cur.execute('''
        UPDATE Users_Favorites 
        SET block_status = TRUE 
        WHERE users_id = %s AND favorites_id = %s;
        ''', (user_id, favorites_id))

def del_block_list(cur: object, user_id: str, favorites_id: str) -> None:

    '''Убираем у пользователя статус в черном списке.'''

    cur.execute('''
        UPDATE Users_Favorites 
        SET block_status = FALSE 
        WHERE users_id = %s AND favorites_id = %s;
        ''', (user_id, favorites_id))

def get_favourites(cur: object, users_id: str, status=False) -> tuple:

    '''Выгружаем из базы данных список избранных.'''

    cur.execute('''
        SELECT f.name, f.bdate, f.city, f.link, f.id FROM users_favorites AS uf
        JOIN favorites AS f ON uf.favorites_id = f.id
        WHERE uf.users_id = %s AND uf.block_status = %s;
        ''', (users_id, status))
    return cur.fetchall()

def drop_table(cur: object) -> str:

    '''Удаление всех таблиц.'''

    cur.execute('''
        DROP TABLE Users_Favorites;
        DROP TABLE Photos;
        DROP TABLE Favorites;
        DROP TABLE Users;       
    ''')
    return 'Таблицы очищены'

def create_db(cur: object) -> str:

    '''Создание таблиц для базы данных.'''

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
