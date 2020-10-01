import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import requests
from random import randrange
import time
import random
import psycopg2
import sqlalchemy as sq

class Bot(object):
    def __init__(self, token, token_search, group_id):
        self.group_id = group_id
        self.token_search = token_search
        self.token = token
        self.vk = vk_api.VkApi(token=self.token)
        self.longpoll = VkLongPoll(self.vk)
        self.headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Content-Encoding': 'utf-8'}

    def write_msg(self, user_id, message):
        self.vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7)})

    def get_member_info(self):   # получаем условия для подбора кандидатов
        # получаем участников группы
        params = {'access_token': self.token, 'group_id': self.group_id, 'sort': 'time_asc', 'v': 5.124}
        member_list = requests.get(f'https://api.vk.com/method/groups.getMembers', params=params).json()['response']['items']
        # для каждого участника выводим условия для подбора кандидатов
        for self.user_id in member_list:
            params_user = {'access_token': self.token, 'user_ids': self.user_id, 'fields': 'first_name,last_name,sex,bdate,relation,city', 'v': 5.124}
            member_info = requests.get(f'https://api.vk.com/method/users.get', params=params_user).json()['response'][0]
            self.first_name = member_info['first_name']
            self.last_name = member_info['last_name']

            member_sex = member_info['sex']
            if member_sex == 1:
                self.candidate_sex = 2
            else:
                self.candidate_sex = 1

            member_bdate = member_info['bdate']
            self.member_bdate1 = member_bdate.replace('.', ',')[5:]

            # знакомимся и запрашивем недостающие данные для подбора кандидатов
            for self.user_id in member_list:
                self.write_msg(self.user_id, 'Привет! Меня зовут Бот. Я готов помочь вам найти вторую половинку. Начнем? Да/Нет')
                for event in self.longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW:
                        if event.to_me:
                            request = event.text
                            if 'нет' in request or 'НЕТ' in request or 'Нет' in request or 'нЕТ' in request:
                                self.write_msg(event.user_id, 'Жаль... Если передумаете, обращайтесь!')
                            elif 'да' in request or 'ДА' in request or 'Да' in request or 'начнем' in request or 'Начнем' in request or 'Давай' in request or 'давай' in request:
                                if 'city' in member_info:
                                    member_city = member_info['city']['title']
                                    param_city = {'access_token': self.token_search, 'country_id': '1', 'q': member_city, 'count': '1', 'v': 5.124}
                                    self.candidate_city = requests.get(f'https://api.vk.com/method/database.getCities', params=param_city,
                                                                         headers=self.headers).json()['response']['items'][0]['id']
                                    if len(member_bdate) == 9:
                                        self.write_msg(event.user_id, 'Отлично! Отправляю фотографии подходящих кандидатов...')
                                        return self.member_bdate1, self.candidate_city, self.candidate_sex, self.user_id, self.first_name, self.last_name
                                    else:
                                        self.write_msg(event.user_id, 'Укажите год вашего рождения в формате 0000 ')
                                        for event in self.longpoll.listen():
                                            if event.type == VkEventType.MESSAGE_NEW:
                                                if event.to_me:
                                                    request = event.text
                                                    self.member_bdate1 = request
                                                    self.write_msg(event.user_id, 'Отлично! Отправляю фотографии подходящих кандидатов...')
                                                    return self.member_bdate1, self.candidate_city, self.candidate_sex, self.user_id, self.first_name, self.last_name
                                elif 'city' not in member_info:
                                    if len(member_bdate) == 9:
                                        self.write_msg(event.user_id, 'Укажите город, в котором проживаете ')
                                        for event in self.longpoll.listen():
                                            if event.type == VkEventType.MESSAGE_NEW:
                                                if event.to_me:
                                                    request = event.text
                                                    member_city = request
                                                    param_city = {'access_token': self.token_search, 'country_id': '1',
                                                                  'q': member_city, 'count': '1', 'v': 5.124}
                                                    self.candidate_city = requests.get(f'https://api.vk.com/method/database.getCities', params=param_city,
                                                                                         headers=self.headers).json()['response']['items'][0]['id']
                                                    self.write_msg(event.user_id, 'Отлично! Отправляю фотографии подходящих кандидатов...')
                                                    return self.member_bdate1, self.candidate_city, self.candidate_sex, self.user_id, self.first_name, self.last_name
                                    else:
                                        self.write_msg(event.user_id, 'Укажите город в котором проживаете ')
                                        for event in self.longpoll.listen():
                                            if event.type == VkEventType.MESSAGE_NEW:
                                                if event.to_me:
                                                    request = event.text
                                                    member_city = request
                                                    param_city = {'access_token': self.token_search, 'country_id': '1',
                                                                  'q': member_city, 'count': '1', 'v': 5.124}
                                                    self.candidate_city = requests.get(f'https://api.vk.com/method/database.getCities', params=param_city,
                                                                                         headers=self.headers).json()['response']['items'][0]['id']
                                                    self.write_msg(event.user_id, 'Укажите год вашего рождения в формате 0000 ')
                                                    for event in self.longpoll.listen():
                                                        if event.type == VkEventType.MESSAGE_NEW:
                                                            if event.to_me:
                                                                request = event.text
                                                                self.member_bdate1 = request
                                                                self.write_msg(event.user_id, 'Отлично! Отправляю фотографии подходящих кандидатов...')
                                                                return self.member_bdate1, self.candidate_city, self.candidate_sex, self.user_id, self.first_name, self.last_name


    def search_candidate(self):   # подбор кандидатов
        # вносим в таблицу инфо об участнике группы user_VK
        table_user = (self.user_id, self.first_name, self.last_name, self.member_bdate1, self.candidate_city)
        connection.execute(f"INSERT INTO user_VK (vk_id,first_name,second_name,birth_year,city) "
                           f"VALUES {table_user}")
        self.approved_candidate = []   # список утвержденных кандидатов
        self.black_list = []    # черный список
        offset = 0
        n = 1
        for y in range(0,1000):
            list_id = []

            # ищем кандидатов
            candidate_param = {'access_token': self.token_search, 'is_closed': 'False', 'has_photo': '1', 'city': self.candidate_city,
                                'sex': self.candidate_sex, 'status': '6', 'birth_year': self.member_bdate1, 'count': '10', 'offset': offset, 'v': 5.124}
            candidate_list = requests.get(f'https://api.vk.com/method/users.search', params=candidate_param, headers=self.headers).json()
            list_1 = candidate_list['response']['items']

            # оставляем кандидатов с открытой страницей
            for u in list_1:
                if u['is_closed'] is False:
                    list_id.append([u['id'], u['first_name'], u['last_name']])
            time.sleep(0.3)
            list_candidate = {}

            # по каждому найденному кандидату получаем топ 3 фото
            for candidate_id in list_id:
                photo_dict = {}
                photo_param = {'access_token': self.token_search, 'owner_id': candidate_id[0], 'album_id': 'profile', 'extended': '1', 'count': '20', 'photo_sizes': '0', 'v': 5.124}
                photo_list = requests.get(f'https://api.vk.com/method/photos.get', params=photo_param, headers=self.headers).json()['response']['items']
                time.sleep(0.5)
                for photo in photo_list:
                    photo_id = photo['id']
                    likes = photo['likes']['count']
                    link = photo['sizes'][-1]['url']
                    photo_dict[likes] = f'photo{candidate_id[0]}_{photo_id}', likes, link
                photo_dict = {l: photo_dict[l] for l in sorted(photo_dict, reverse=True)}
                if len(photo_dict) > 2:
                    list_candidate[candidate_id[0], candidate_id[1], candidate_id[2]] = list(photo_dict.values())[0:3]


            for number, candidate in enumerate(list(list_candidate.items()), n):
                link_url = {}
                # отправляем по 3 фото каждого кандидата нашему участнику группы
                for photo_name in candidate[1]:
                    link_url[photo_name[1]] = photo_name[2]

                    ph_param = {'access_token': self.token, 'user_id': self.user_id, 'message': f'Кандидат № {number} - {candidate[0][1]} {candidate[0][2]}',
                                'random_id': random.getrandbits(64), 'attachment': photo_name[0], 'v': 5.124}
                    response = requests.get(f'https://api.vk.com/method/messages.send', params=ph_param,
                                                 headers=self.headers).json()
                self.write_msg(self.user_id, f'Если вам понравился кандидат № {number}, то пришлите - 1. Иначе - 0')

                # выбираем с участником кандидатов, результаты вносим в таблицы
                for event in self.longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW:
                        if event.to_me:
                            request = event.text
                            if request == '1':
                                self.approved_candidate.append(f'{number}. {candidate[0][1]} {candidate[0][2]} - https://vk.com/id{candidate[0][0]}')

                                # вносим инфо о кандидатах в таблицу datinguser
                                table_datinguser = (candidate[0][0], candidate[0][1], candidate[0][2], self.member_bdate1, f'https://vk.com/id{candidate[0][0]}', self.user_id)
                                connection.execute(f"INSERT INTO datinguser (pair_vk_id,first_name,second_name,birth_year,link,id_User_VK) "
                                                   f"VALUES {table_datinguser}""")

                                # вносим данные о фото кандидатов в таблицу Photos
                                for likes_photo, link_photo1 in link_url.items():
                                    table_Photos = (candidate[0][0], likes_photo, link_photo1)
                                    connection.execute(f"INSERT INTO Photos (id_DatingUser,count_likes,link_photo) "
                                                       f"VALUES {table_Photos}")
                                self.write_msg(event.user_id, 'Отлично, сохраняю в списке подходящих кандидатов')
                                break
                            elif request == '0':
                                self.write_msg(event.user_id, 'Пропускаем')
                                self.black_list.append(candidate[0][0])
                                break
                            else:
                                self.write_msg(event.user_id, 'Вы ввели неверное значение. Попробуйте еще раз')
                                continue
                            self.write_msg(event.user_id, 'Вы ввели неверное значение. Попробуйте еще раз')
                            break

            self.write_msg(self.user_id, f'Направляю Вам список понравившихся кандидатов. \n')
            for item in self.approved_candidate:
                self.write_msg(self.user_id, item)
            self.write_msg(self.user_id, f'Если вы выбрали пару, пришлите - Да \n'
                                         f'Если же желаете посмотреть еще новых кандидатов, пришлите - 0 \n'
                                         f'Для удаления кандидатов из списка, пришлите - DEL \n')


            # в зависимости от ответа участника группы либо корректируем список кандидатов, либо продолжаем подбор, либо завершаем
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW:
                    if event.to_me:
                        request = event.text
                        if 'Да' in request or 'да' in request or 'ДА' in request or 'дА' in request:
                            self.write_msg(self.user_id, f'Поиск завершен. Поздравляю!')
                            return self.approved_candidate, self.black_list

                        # корретируем список кандидатов, вносим изменения в таблицы
                        elif request == 'DEL' or request == 'del' or request == 'Del':
                            self.write_msg(self.user_id, f'Пришлите номера кандидатов, которых необходимо удалить из списка, через запятую')
                            for event in self.longpoll.listen():
                                if event.type == VkEventType.MESSAGE_NEW:
                                    if event.to_me:
                                        request = event.text
                                        delete_list = list(request.replace(' ', '').replace(',', ''))
                                        for num in delete_list:
                                            for person in self.approved_candidate:
                                                if person[0] == num:
                                                    id_delete = person[person.index('d') + 1:]
                                                    connection.execute("""DELETE from Photos where id_DatingUser = %s;""", (id_delete,))
                                                    connection.execute("""DELETE from datinguser where pair_vk_id = %s;""", (id_delete,))
                                                    self.approved_candidate.remove(person)
                                                    self.black_list.append(id_delete)
                                        self.write_msg(self.user_id, f'Удалено. \n'
                                                                     f'Направляю Вам скорректированный список понравившихся кандидатов. \n')
                                        for item in self.approved_candidate:
                                            self.write_msg(self.user_id, item)
                                        self.write_msg(self.user_id, f'Если вы выбрали пару, пришлите - Да \n'
                                                                     f'Если же желаете посмотреть еще новых кандидатов, пришлите - 0 \n'
                                                                     f'Для удаления кандидатов из списка, пришлите - DEL')
                                        break
                        elif request == '0':
                            self.write_msg(self.user_id, f'Продолжаем подбор кандидатов...')
                            n += len(self.approved_candidate)
                            break
                        else:
                            self.write_msg(event.user_id, 'Вы ввели неверное значение. Попробуйте еще раз')
                            continue
            offset += 10
        # result = connection.execute("""SELECT u.first_name, u.second_name, d.first_name, d.second_name, link FROM User_VK u
        #                                 JOIN DatingUser d on d.id_User_VK = u.vk_id""").fetchall()
        # print(result)
        return self.approved_candidate, self.black_list

if __name__ == "__main__":
    login = 'postgres'
    kod = 'Shitko77'
    engine = sq.create_engine(f'postgresql+psycopg2://{login}:{kod}$@localhost:5432/dating_pair')
    connection = engine.connect()
    group_id = '198765605'
    token = '...'
    token_search = '...'
    bot = Bot(token, token_search, group_id)
    bot.get_member_info()
    print(bot.search_candidate())











