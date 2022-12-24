## Командный проект по курсу «Профессиональная работа с Python»

[Описание задания к проекту](https://github.com/netology-code/adpy-team-diplom/blob/main/README.md)

--------
 В данном проекте реализован чат бот знакомств для пользователей
социальной сети Вконтакте.

Программа чат бота позволяет пользователям искать 
людей по заданным ими параметрам поиска (город, пол, возраст).
Для запроса поиска пользователю необходимо зайти в сообщество 
Вконтакте и написать боту. Бот выдает имя пользователя, 
ссылку на его профиль в Вконтаке и до трех фотографий из 
размещенных в профиле и на стене, и имеющих 
максимальное количество лайков.

----------

Чтобы воспрользоваться программой чат бота необходимо:
- установить postgreSQL на компьютере и создать БД с названием
  team_project с пользователем postgres и паролем. 
- Зарегистрироваться в Вконтакте. На [странице разработчика](https://vk.com/apps?act=manage)
  создать приложение и получить токен пользователя согласно 
[инструкции](https://docs.google.com/document/d/1_xt16CMeaEir-tWLbUFyleZl6woEdJt-7eyva1coT3w/edit). 
- В своем аккаунте Вконтакте создать сообщество. На странице 
сообщества перейти в раздел "Управление", далее в раздел
"Работа с API" и нажать "Создать ключ". Далее подтвердить галочками
разрешение доступа приложения к сообществу и получить токен.
- Склонировать репозиторий проекта из GitHub на компьютер.
- Установить на компьютер Python 3.x с [официального сайта](https://www.python.org/downloads/) 
 и IDE для Python (PyCharm, VSC, etc.)
- В  IDE в директории проекта создать файл token_vk.py. 
 В этот файл записать данные для авторизации
 в БД и полученные токены приложения и сообщества.

```Python
    token_vk = "токен пользователя"  
    token_vk_community = "токен сообщества" 
    sql_authorization = {'dbname': 'team_project', 'user': 'postgres', 'password': 'ваш пароль'}
``` 
 - В виртуальное окружение проекта установить библиотеки, указанные в 
 файле requirements.txt
- Запустить main.py
 
