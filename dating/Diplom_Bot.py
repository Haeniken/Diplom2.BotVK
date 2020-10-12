import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import requests
from random import randrange
import time
import random
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from dating.sql_partners import User_VK, DatingUser, Photo, session


class Bot(object):
    def __init__(self, token, token_search, group_id):
        self.group_id = group_id
        self.token_search = token_search
        self.token = token
        self.vk = vk_api.VkApi(token=self.token)
        self.headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Content-Encoding': 'utf-8'}

    def write_msg(self, user_id, message, attachment=None, keyboard=None):
        """Функция по отправке сообщений участнику группы"""
        values = {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7)}
        if attachment:
            values['attachment'] = attachment
        if keyboard:
            values['keyboard'] = keyboard
        self.vk.method('messages.send', values)

    def start(self):
        """Функция, ожидающая первичного сообщения от участника группы, для его идентификации, получения ID."""
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                text = event.text.lower()
                keyboard = VkKeyboard(one_time= False)
                keyboard.add_button('Да', color=VkKeyboardColor.PRIMARY)
                keyboard.add_button('Позже', color=VkKeyboardColor.SECONDARY)
                keyboard = keyboard.get_keyboard()
                if event.from_user:
                    self.write_msg(event.user_id, f'{bot.get_fullname(event.user_id)[0]}, привет! \n'
                                                  f'Добро пожаловать в группу Встречи и знакомства! \n'
                                                  'Хочешь найти себе пару?', keyboard=keyboard)
                    for event in longpoll.listen():
                        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                            text = event.text.lower()
                            if text != 'да':
                                self.write_msg(event.user_id, 'Как будет подходящее время, напиши мне!')
                                return None
                            else:
                                self.write_msg(event.user_id, 'Отлично! Тогда начнем!')
                                break
                    return event.user_id

    def get_fullname(self, client_id):
        """Функция для получения Имени и Фамилии участника или кандидатов"""
        params_user = {'access_token': self.token_search, 'user_ids': client_id,
                       'fields': 'first_name,last_name', 'v': 5.124}
        info = requests.get(f'https://api.vk.com/method/users.get', params=params_user).json()['response'][0]
        self.first_name = info['first_name']
        self.last_name = info['last_name']
        return self.first_name, self.last_name

    def get_city(self, client_id):
        """Функция для получения города проживания"""
        params_user = {'access_token': self.token_search, 'user_ids': client_id,
                       'fields': 'city', 'v': 5.124}
        info = requests.get(f'https://api.vk.com/method/users.get', params=params_user).json()['response'][0]
        if 'city' in info:
            self.city = info['city']['title']
            return self.city
        elif 'city' not in info:
            self.write_msg(client_id, 'Укажи город, в котором ищешь партнера? Например, Москва')
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                    self.city = event.text
                    param_city = {'access_token': self.token_search, 'country_id': '1',
                                  'q': self.city, 'count': '1', 'v': 5.124}
                    city = requests.get(f'https://api.vk.com/method/database.getCities', params=param_city,
                                     headers=self.headers).json()['response']['items']
                    if len(city) != 0:
                        print(self.city)
                        return self.city
                    else:
                        self.write_msg(client_id, f'Не нашел города с названием {self.city}. \n'
                                                  f'Попробуй еще раз ввести название города. Например, Москва')
        return self.city

    def get_gender(self, client_id):
        """Функция для получения пола"""
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('Девушка 👩', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Парень 👨', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('Любого пола', color=VkKeyboardColor.SECONDARY)
        keyboard = keyboard.get_keyboard()
        self.write_msg(client_id, 'Партнера какого пола будем подбирать?', keyboard=keyboard)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                text = event.text
                if text == 'Девушка 👩':
                    self.gender = '1'
                    return self.gender
                elif text == 'Парень 👨':
                    self.gender = '2'
                    return self.gender
                elif text == 'Любого пола':
                    self.gender = '0'
                    return self.gender

    def get_birth_year(self, pair_id):
        """Функция для получения даты рождения"""
        params_user = {'access_token': self.token_search, 'user_ids': winner,
                       'fields': 'bdate,city', 'v': 5.124}
        info = requests.get(f'https://api.vk.com/method/users.get', params=params_user).json()['response'][0]
        if 'bdate' in info:
            self.bdate = info['bdate']
        else:
            self.bdate = '0'
        return self.bdate

    def get_age_from(self, client_id):
        """Функция для получения минимального возраста кандидата"""
        self.write_msg(client_id, 'Укажи минимальный возраст партнера в цифрах. Например, 25')
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                self.age_from = int(event.text)
                if 18 < self.age_from < 100:
                    return self.age_from
                else:
                    self.write_msg(client_id, 'К сожалению, ты указал недопустимый возраст. \n'
                                              'Попробуй еще раз. Например, 25')

    def get_age_to(self, client_id):
        """Функция для получения максимального возраста кандидата"""
        self.write_msg(client_id, 'Укажи максимальный возраст партнера в цифрах. Например, 30')
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                self.age_to = int(event.text)
                if self.age_to >= 100:
                    self.write_msg(client_id, 'К сожалению, ты указал недопустимый возраст. \n'
                                              'Попробуй еще раз. Например, 30')
                elif self.age_to >= self.age_from:
                    self.write_msg(client_id, 'Отлично!')
                    time.sleep(0.5)
                    self.write_msg(client_id, 'Минуточку..... \n'
                                              'Ищу кандидатов....')
                    return self.age_to
                else:
                    self.write_msg(client_id, f'Эта возраст меньше, чем указанный тобой минимальный возраст партнера.\n'
                                              f'Попробуй еще раз! Укажи возраст не меньше, чем {self.age_from}')

    def search_partners(self, client_id):
        """Функция для поиска кандидатов по полученным параметрам"""
        candidate_param = {'access_token': self.token_search, 'is_closed': 'False', 'has_photo': '1',
                         'sex': self.gender, 'status': '6', 'hometown': self.city, 'age_from': self.age_from,
                         'age_to': self.age_to, 'count': '20', 'v': 5.124}
        candidate_list = requests.get(f'https://api.vk.com/method/users.search',
                                      params=candidate_param, headers=self.headers).json()['response']['items']
        time.sleep(0.2)
        # создание списка ID кандидатов с открытыми страницами VK
        self.list_partner = []
        for partner in candidate_list:
            if partner['is_closed'] is False:
                self.list_partner.append(partner['id'])

        if len(self.list_partner) == 0:
            self.write_msg(client_id, 'К сожалению, я не нашел кандидатов по твоим критериям. '
                                      'Давай попробуем еще раз. \n'
                                      'Пришли мне любое сообщение, и мы начнем новый поиск. ')
        return self.list_partner

    def choose_3photo(self, partner_id):
        """Функция для поиска кандидатов по полученным параметрам"""
        photo_param = {'access_token': self.token_search, 'owner_id': partner_id, 'album_id': 'profile',
                       'extended': '1', 'count': '20', 'photo_sizes': '0', 'v': 5.124}
        photo_list = requests.get(f'https://api.vk.com/method/photos.get',
                                  params=photo_param, headers=self.headers).json()['response']
        time.sleep(0.5)
        # создание словаря для сортировки фото кандидатов по количеству лайков
        photo_dict = {}
        if photo_list['count'] >= 3:
            for photo in photo_list['items']:
                photo_id = photo['id']
                likes = photo['likes']['count']
                link = photo['sizes'][-1]['url']
                photo_dict[likes] = f'photo{partner_id}_{photo_id}'
        else:
            pass
        # сортировка по ключу (лайкам)
        photo_dict = {lks: photo_dict[lks] for lks in sorted(photo_dict, reverse=True)}
        # получение топ 3 фото в формате, удобном для отправки участнику группы
        self.photos = list(photo_dict.values())[0:3]
        return self.photos

    def get_photo_info(self, photo_id):
        """Функция для получения информации (количеству лайков и ссылки на фото) по ID фотографии"""
        photo_param = {'access_token': self.token_search, 'photos': photo_id, 'extended': '1', 'v': 5.124}
        photo_info = requests.get(f'https://api.vk.com/method/photos.getById',
                                  params=photo_param, headers=self.headers).json()['response']
        link = photo_info[0]['sizes'][-1]['url']
        likes = photo_info[0]['likes']['count']
        return link, likes

    def send_photo(self, client_id, partner_id):
        """Функция для отправки 3х фотографий участнику группы"""
        all_photo = ",".join(self.photos)
        time.sleep(0.5)
        full_name_partner = ' '.join(bot.get_fullname(partner_id))
        ph_param = {'access_token': self.token, 'user_id': client_id, 'message': f'{full_name_partner} ',
                    'random_id': random.getrandbits(64), 'attachment': all_photo, 'v': 5.124}
        response = requests.get(f'https://api.vk.com/method/messages.send',
                                params=ph_param, headers=self.headers).json()
        return response

    def choose_candidates(self, client_id, partner_id, partners_list, black_list):
        """Функция для коммуникации с участников с целью выбора понравившихся кандидатов"""
        numbers_candidates = {}
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('Нравится 👍', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Не нравится 👎', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button('Сделать выбор из понравившихся 👆', color=VkKeyboardColor.POSITIVE)
        keyboard = keyboard.get_keyboard()
        self.write_msg(client_id, 'Выбирай... ', keyboard=keyboard)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                text = event.text
                if text == 'Нравится 👍':
                    partners_list.append(partner_id)
                    break
                elif text == 'Не нравится 👎':
                    black_list.append(partner_id)
                    break
                elif text == 'Сделать выбор из понравившихся 👆':
                    for i, partner_id in enumerate(partners_list, 1):
                        self.write_msg(client_id, f'Кандидат №{i} {" ".join(bot.get_fullname(partner_id))}')
                        bot.choose_3photo(partner_id)
                        bot.send_photo(client_id, partner_id)
                        numbers_candidates[i] = partner_id
                    self.write_msg(client_id, 'Пора сделать выбор. Пришли номер выбранного кандидата')
                    for event in longpoll.listen():
                        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                            text = event.text
                            if int(text) not in list(numbers_candidates.keys()):
                                self.write_msg(client_id, f'Кандидат с номером {int(text)} отсутствует в нашем списке. '
                                                          f'Попробуй еще раз, введи номер кандидата цифрами.')
                            for number, self.partner in numbers_candidates.items():
                                if int(text) == number:
                                    full_name_pair = " ".join(bot.get_fullname(self.partner))
                                    link_pair = f'https://vk.com/id{self.partner}'
                                    self.write_msg(client_id, f'Поздравляю! {full_name_pair} - отличный выбор! \n'
                                                              f'Отправляю тебе ссылку на страницу партнера {link_pair}')
                                    winner_pair = self.partner
                                    partners_list.append(winner_pair)
                                    return self.partner

    def save_user(self, client_id):
        """Функция для сохранения информации об участнике группы в базе данных"""
        table_user = User_VK(client_id, self.first_name, self.last_name, self.city)
        session.add(table_user)
        session.commit()
        return table_user

    def save_partner(self, pair_id, client_id):
        """Функция для сохранения информации о выбранном кандидате в базе данных"""
        bot.get_birth_year(winner)
        table_datinguser = DatingUser(winner, self.first_name, self.last_name, self.bdate, client_id)
        session.add(table_datinguser)
        session.commit()
        return table_datinguser

    def save_photoslink(self, pair_id):
        """Функция для сохранения топ 3 фотографии выбранного кандидата в базе данных"""
        photo_top = bot.choose_3photo(winner)
        # получаем ID 3х фотографий
        photo_link = []
        for photo in photo_top:
            photo_link.append(photo[5:])
        # получаем количество лайков и ссылки на фотографии
        for photo_id in photo_link:
            photo_data = bot.get_photo_info(photo_id)
            likes_photo = photo_data[1]
            link_photo1 = photo_data[0]
            # созраняем полученную информацию в базе данных
            table_Photos = Photo(winner, likes_photo, link_photo1)
            session.add(table_Photos)
        session.commit()
        return 'Информация сохранена в базе данных'

if __name__ == "__main__":
    group_id = '198765605'
    token = '...'
    token_search = '...'
    vk = vk_api.VkApi(token=token)
    longpoll = VkLongPoll(vk)

    for event in longpoll.listen():
        bot = Bot(token, token_search, group_id)
        client_id = event.user_id
        bot.start()
        bot.get_fullname(client_id)
        bot.get_city(client_id)
        bot.get_gender(client_id)
        bot.get_age_from(client_id)
        bot.get_age_to(client_id)
        print(bot.save_user(client_id))
        # список понравившихся кандидатов
        partners_list = []
        # черный лист
        black_list = []
        for partner_id in bot.search_partners(client_id):
            if len(bot.choose_3photo(partner_id)) == 3:
                bot.send_photo(client_id, partner_id)
                if bot.choose_candidates(client_id, partner_id, partners_list, black_list) != None:
                    break
        print(f'Список ID понравившихся кандидатов: {partners_list}')
        print(f'ID кандидатов, попавших в черный лист: {black_list}')
        # получаем ID победителя
        winner = partners_list[-1]
        print(bot.save_partner(winner, client_id))
        print(bot.save_photoslink(winner))



