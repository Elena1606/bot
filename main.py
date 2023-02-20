import vk_api
import requests
import datetime
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from database import insert_data_users, insert_data_seen_users, select
from config import user_token, comm_token, v
offset = 0
line = range(0, 1000)

def get_params(add_params: dict = None):
    params = {
        'access_token': user_token,
        'v': v
    }
    if add_params:
        params.update(add_params)
        pass
    return params

class VKBot:

    def __init__(self):
        print('Bot was created')
        self.age = 0
        self.city = 0
        self.searching_user_id = 0
        self.top_photos = ''
        self.offset = 0
        self.vk = vk_api.VkApi(token=comm_token)
        self.longpoll = VkLongPoll(self.vk)

    def write_msg(self, user_id, message, attachment=''):
        self.vk.method('messages.send', {'user_id': user_id,
                                         'message': message,
                                         'random_id': get_random_id(),
                                         'attachment': attachment})

    def get_name(self, user_id):
        response = requests.get('https://api.vk.com/method/users.get', get_params({'user_ids': user_id}))
        for user_info in response.json()['response']:
            self.username = user_info['first_name'] + ' ' + user_info['last_name']
        return self.username

    def get_sex(self, user_id):
        url = f'https://api.vk.com/method/users.get'
        params = {'access_token': user_token,
                  'user_ids': user_id,
                  'fields': 'sex',
                  'v': '5.131'}
        repl = requests.get(url, params=params)
        response = repl.json()
        try:
            information_list = response['response']
            for i in information_list:
                if i.get('sex') == 2:
                    find_sex = 1
                    return find_sex
                elif i.get('sex') == 1:
                    find_sex = 2
                    return find_sex
        except KeyError:
            self.write_msg(user_id, 'Ошибка  - пол не определён ')


    def get_age_at(self, user_id):
        url = f'https://api.vk.com/method/users.get'
        params = {'access_token': user_token,
                  'user_ids': user_id,
                  'fields': 'bdate',
                  'v': v}
        repl = requests.get(url, params=params)
        response = repl.json()
        try:
            information_list = response['response']
            for item in information_list:
                date = item.get('bdate')
            date_list = date.split('.')
            if len(date_list) == 3:
                year = int(date_list[2])
                year_now = int(datetime.date.today().year)
                return year_now - year
            elif len(date_list) == 2 or date not in information_list:
                for event in self.longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        age = event.text
                        return age
        except KeyError:
            self.write_msg(user_id, 'Ошибка получения нижней границы возраста')

    def get_age_to(self, user_id):

        url = f'https://api.vk.com/method/users.get'
        params = {'access_token': user_token,
                  'user_ids': user_id,
                  'fields': 'bdate',
                  'v': v}
        repl = requests.get(url, params=params)
        response = repl.json()
        try:
            information_list = response['response']
            for item in information_list:
                date = item.get('bdate')
            date_list = date.split('.')
            if len(date_list) == 3:
                year = int(date_list[2])
                year_now = int(datetime.date.today().year)
                return year_now - year
            elif len(date_list) == 2 or date not in information_list:
                for event in self.longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        age = event.text
                        return age
        except KeyError:
            self.write_msg(user_id, 'Ошибка получения верхней границы возраста')

    def cities(self, user_id, city_name):
        url = f'https://api.vk.com/method/database.getCities'
        params = {'access_token': user_token,
                  'country_id': 1,
                  'q': f'{city_name}',
                  'need_all': 0,
                  'count': 1000,
                  'v': v}
        repl = requests.get(url, params=params)
        response = repl.json()
        try:
            information_list = response['response']
            list_cities = information_list['items']
            for item in list_cities:
                found_city_name = item.get('title')
                if found_city_name == city_name:
                    found_city_id = item.get('id')
                    return int(found_city_id)
        except KeyError:
            self.write_msg(user_id, 'Ошибка получения id города')

    def find_city(self, user_id):
        url = f'https://api.vk.com/method/users.get'
        params = {'access_token': user_token,
                  'fields': 'city',
                  'user_ids': user_id,
                  'v': v}
        repl = requests.get(url, params=params)
        response = repl.json()
        try:
            information_dict = response['response']
            for item in information_dict:
                if 'city' in item:
                    city = item.get('city')
                    id = str(city.get('id'))
                    return id
                elif 'city' not in item:
                    self.write_msg(user_id, 'Введите название вашего города: ')
                    for event in self.longpoll.listen():
                        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                            city_name = event.text
                            id_city = self.cities(user_id, city_name)
                            if id_city != '' or id_city != None:
                                return str(id_city)
                            else:
                                break
        except KeyError:
            self.write_msg(user_id, 'Ошибка - город не определён')

    def find_user(self, user_id):
        url = f'https://api.vk.com/method/users.search'
        params = {'access_token': user_token,
                  'v': '5.131',
                  'sex': self.get_sex(user_id),
                  'age_from': self.get_age_at(user_id),
                  'age_to': self.get_age_to(user_id),
                  'city': self.find_city(user_id),
                  'fields': 'is_closed, id, first_name, last_name',
                  'relation': '1' or '8',
                  'count': 500}
        resp = requests.get(url, params=params)
        resp_json = resp.json()
        try:
            dict_1 = resp_json['response']
            list_1 = dict_1['items']
            for person_dict in list_1:
                if person_dict.get('is_closed') == False:
                    first_name = person_dict.get('first_name')
                    last_name = person_dict.get('last_name')
                    vk_id = str(person_dict.get('id'))
                    insert_data_users(first_name, last_name, vk_id)
                else:
                    continue
            return f'Поиск завершён'
        except KeyError:
            self.write_msg(user_id, 'Ошибка при поиске пары')

    def get_top_photos(self, user_id):
        photos = []
        response = requests.get(
            'https://api.vk.com/method/photos.get',
            get_params({'owner_id': user_id,
                        'album_id': 'profile',
                        'extended': 1}))
        try:
            sorted_response = sorted(response.json()['response']['items'],
                                     key=lambda x: x['likes']['count'], reverse=True)
            for photo_id in sorted_response:
                photos.append(f'''photo{user_id}_{photo_id['id']}''')
            self.top_photos = ','.join(photos[:3])
            return self.top_photos
        except KeyError:
            self.write_msg(user_id, 'Ошибка  - фото не загружается')

    def find_persons(self, user_id, offset):
        self.write_msg(user_id, self.found_person_info(user_id, offset), self.top_photos)
        self.person_id(offset)
        insert_data_seen_users(self.person_id(offset), offset)

    def found_person_info(self, user_id, offset):
        self.get_top_photos(user_id)
        tuple_person = select(offset)
        list_person = []
        for item in tuple_person:
            list_person.append(item)
        return f'Это же {list_person[0]} {list_person[1]} | https://vk.com/id{list_person[2]}'

    def person_id(self, offset):
        tuple_person = select(offset)
        list_person = []
        for item in tuple_person:
            list_person.append(item)
        return str(list_person[2])


bot = VKBot()