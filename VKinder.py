class VKinder:

    def __init__(self, longpoll, session):
        self.longpoll = longpoll
        self.session = session

    def _search(self, user_param):
        '''первоначальный поиск'''
        if user_param[6] == 'Мужской':
            sex = 1
        elif user_param[6] == 'Женский':
            sex = 2
        else:
            sex = 0

        result = self.session.users.search(count=1000, blacklisted_by_me=0, fields=['photo_id', 'sex', 'bdate', 'city',
                                                                                  'is_closed'],
                                           city=user_param[5], sex=sex,
                                           age_from=user_param[3], age_to=user_param[3], has_photo=1,)['items']
        print('Выполнен первоначальный поиск')
        return result

    def _find_photo(self, user_id):
        '''подбираем фото'''
        get_photo = self.session.photos.get(owner_id=user_id, album_id='profile', extended=1, photo_sizes=1)['items']
        photo_list = sorted(get_photo, key=lambda k: k['likes']['count'], reverse=True)
        if len(photo_list) > 3:
            photo_list = photo_list[:3]
        attachment_list = list()
        for item in photo_list:
            attachment_list.append(f'photo{user_id}_{item["id"]}')
        return attachment_list

    def find_user(self, user_param):
        '''выборка по параметрам'''
        search_users_dict = self._search(user_param)
        find_users = list()
        print("Ищем фото, формируем данные")
        for black_user in search_users_dict:
            if not black_user['is_closed']:
                print('. ', end="")
                attachment = self._find_photo(black_user['id'])
                find_users.append({'user_name': black_user['user_name'],
                                   'url': f"https://vk.com/id{black_user['id']}",
                                   'attachment': attachment, 'id': black_user['id']})

        print("\nПоиск фото окончен, данные сформированы")
        return find_users