import requests
from aiogram.dispatcher import FSMContext

from aiogram.utils.exceptions import MessageToDeleteNotFound

from data.config import API_CORE, user, password
from keyboards.inline.callback_data import update_cd
from loader import bot
import asyncio
from typing import Union
from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import CancelHandler


# для принёма альбома фотографий в одном хендлере
class AlbumMiddleware(BaseMiddleware):
    album_data: dict = {}

    def __init__(self, latency: Union[int, float] = 0.01):
        self.latency = latency
        super().__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        if not message.media_group_id:
            return

        try:
            self.album_data[message.media_group_id].append(message)
            raise CancelHandler()
        except KeyError:
            self.album_data[message.media_group_id] = [message]
            await asyncio.sleep(self.latency)

            message.conf["is_last"] = True
            data["album"] = self.album_data[message.media_group_id]

    async def on_post_process_message(self, message: types.Message, result: dict, data: dict):
        if message.media_group_id and message.conf.get("is_last"):
            del self.album_data[message.media_group_id]


# Запрос выборки по модели или конкретному url
def get_queryset(model=None, custom_url=False):
    url = API_CORE
    if model:
        url = API_CORE + f'{model}/'
    if custom_url:
        url = custom_url
    print(url)
    response = requests.get(url=url)
    data = response.json()
    return data


def refactor_related_data(data):
    res, i = '', 0
    for obj in data:
        i += 1
        if i == len(data):
            res += f'{obj["title"]}'
        else:
            res += f'{obj["title"]},'
    return res


# Создание клавиатуры навигации. Переход к след. или пред. страницам выборки
def create_store_navigation(next_data, previous_data):
    navigation = []
    if previous_data:
        previous_data = previous_data.replace(API_CORE, 'pag=')
        navigation.append(types.InlineKeyboardButton(text=f'⬅️',
                                                     callback_data=previous_data))
    if next_data:
        next_data = next_data.replace(API_CORE, 'pag=')
        navigation.append(types.InlineKeyboardButton(text=f'➡️',
                                                     callback_data=next_data))
    return types.InlineKeyboardMarkup(inline_keyboard=[navigation])


# Функция изъятия данных о предыдущих сообщениях из state
async def get_previous_message_data(state: FSMContext):
    data = await state.get_data()
    try:
        return data['sent_messages']
    except KeyError:
        return 0


# Удаление сообщений
async def mess_delete(state: FSMContext, chat_id):
    messages = await get_previous_message_data(state)
    if not messages:
        return 0
    for message_id in messages:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=message_id)
        except MessageToDeleteNotFound:
            pass
    await state.update_data(sent_messages=None)


# Выдает клавиатуру для выбора одной из CRUD операций с моделью
def get_crud_menu(prefix):
    read_title = "Просмотреть все"
    if prefix == "ITEM":
        read_title = "Найти товар"
    markup = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text='Создать',
                                        callback_data=f'{prefix}_create')],
            [types.InlineKeyboardButton(text=read_title,
                                        callback_data=f'{prefix}_read')],
            [types.InlineKeyboardButton(text='Изменить',
                                        callback_data=f'{prefix}_update')],
            [types.InlineKeyboardButton(text='Удалить',
                                        callback_data=f'{prefix}_delete')]
        ]
    )

    return markup


# Преобразование id в строку из названий соотвествующих экземпляров моделей
def refactor_list_of_tuples_to_string(data, model: str):
    res = ''
    for element in data:
        url = API_CORE + f'{model}/{element}/'
        qs = get_queryset(model, url)
        try:
            res += qs['title'] + ', '
        except KeyError:
            return 0
    return res[:-2]


# Создает текст превью карточки товара, который создает юзер
async def get_preview_data(state):
    data = await state.get_data()
    quality = ''
    if data['quality'] == 1:
        quality = 'Top quality'
    if data['quality'] == 2:
        quality = 'High quality - AAA +'
    if data['quality'] == 3:
        quality = '1: 1🤩'
    gender = ''
    if data['gender'] == 1:
        gender = 'М'
    if data['gender'] == 2:
        gender = 'Ж'
    if data['gender'] == 3:
        gender = 'Унисекс'

    categories_string = refactor_list_of_tuples_to_string(data['categories'], 'category')
    brands_string = refactor_list_of_tuples_to_string(data['brands'], 'brand')
    if not categories_string or not brands_string:
        return 0, 0
    template = f"{data['title']}\n\n" \
               f"Пол: {gender}\n" \
               f"Качество: {quality}\n" \
               f"Категория: {categories_string}\n" \
               f"Брэнд: {brands_string}\n\n" \
               f"{data['description']}\n\n" \
               f"{data['price']} ₽"

    return data['photos'], template


def create_media_group(file_id_list):
    ids = []
    for file_id in file_id_list:
        response = requests.post(url=API_CORE + 'media_group/', data={'file_id': file_id})
        if response.status_code == 201:
            ids.append(response.json()['id'])
    return ids


# Перенос шаблона товара в api
async def send_template_to_api(state: FSMContext):
    data = await state.get_data()
    print(data)
    photos = create_media_group(data['photos'])
    data = {
        "title": data['title'],
        "description": data['description'],
        "gender": data['gender'],
        "quality": data['quality'],
        "price": data['price'],
        "category": data['categories'],
        "brand": data['brands'],
        "media_group": photos
    }
    response = requests.post(url=API_CORE + 'item/', data=data)
    if response.status_code == 201:
        return response.json()['id']
    return False


# Функция удаления объектов
async def delete_model(call, pk, model):
    response = requests.delete(API_CORE + f'{model}/{pk}/')
    if response.status_code == 204:
        return await bot.send_message(call.from_user.id, 'Объкт удален.')
    else:
        return await bot.send_message(call.from_user.id, 'Ошибка. Объект не был удален')


def get_auth_token():
    data = {
        "username": user,
        "password": password
    }
    response = requests.post(url=API_CORE + 'auth/', data=data)
    result = 0
    if response.status_code == 200:
        result = response.json()['token']
    return result


def add_new_admin(telegram_id):
    token = get_auth_token()
    headers = {"Authorization": f"Token {token}"}
    if token:
        response = requests.get(url=API_CORE + f"telegram-user/?telegram_id={telegram_id}",
                                headers=headers)
        pk = 0
        if response.status_code == 200:
            if response.json():
                pk = response.json()[0]['id']
        if not pk:
            response = requests.post(url=API_CORE + 'telegram-user/', headers=headers,
                                     data={'telegram_id': telegram_id, "is_staff": True})
            if response.status_code == 201:
                return 1
        else:
            response = requests.patch(url=API_CORE + f"telegram-user/{pk}/",
                                      headers=headers, data={"is_staff": True})
            if response.status_code == 200:
                if response.json()['is_staff']:
                    return 1
    return 0


def get_model_fields_markup(pk, model):
    response = requests.get(url=API_CORE + f"{model}/{pk}/")
    if not response.status_code == 200:
        return 0
    if not response.json():
        return 0
    buttons = []
    print(response.json())
    for field, value in response.json().items():
        if field == 'id' or field == 'subscribers':
            continue
        buttons.append([types.InlineKeyboardButton(text=f'{field}',
                                                   callback_data=update_cd.new(field=field))])

    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def get_admin_list_text():
    token = get_auth_token()
    if token:
        response = requests.get(url=API_CORE + 'telegram-user/?is_staff=1', headers={"Authorization": f"Token {token}"})
        if response.status_code == 200:
            data = response.json()
            text = 'Список Админов\nID'
            for admin in data:
                text += f"\n{admin['telegram_id']}"
            return text
    return 0


# аутентификация администратора
def admin_auth(telegram_id):
    token = get_auth_token()
    response = requests.get(url=API_CORE + f'telegram-user/?telegram_id={telegram_id}&is_staff=1',
                            headers={"Authorization": f"Token {token}"})
    if response.status_code == 200:
        return response.json()
    return 0


def delete_admin(telegram_id):
    token = get_auth_token()
    response = requests.get(url=API_CORE + f'telegram-user/?telegram_id={telegram_id}&is_staff=1',
                            headers={"Authorization": f"Token {token}"})
    if response.status_code == 200:
        if not response.json():
            return 0
        pk = response.json()[0]['id']
        response = requests.patch(url=API_CORE + f'telegram-user/{pk}/',
                                  headers={"Authorization": f"Token {token}"},
                                  data={'is_staff': False})
        if response.status_code == 200:
            if not response.json()['is_staff']:
                return 1
    return 0


def create_telegram_user(telegram_id):
    token = get_auth_token()
    response = requests.post(API_CORE + "telegram-user/", headers={"Authorization": f"Token {token}"},
                             data={"telegram_id": telegram_id})
    if response.status_code == 201:
        return response.json()['id']
    return 0


def get_or_create_user(telegram_id):
    headers = {"Authorization": f"Token {get_auth_token()}"}
    response = requests.get(url=API_CORE + f"telegram-user/?telegram_id={telegram_id}",
                            headers=headers)
    if response.status_code == 200:
        if response.json():
            pk = response.json()[0]['id']
        else:
            pk = create_telegram_user(telegram_id)
            if not pk:
                return 0
    else:
        return 0
    return pk


def get_item_card_markup(fav_button_title, fav_cd,
                         item_id: int, previous_message):
    favourites_button = [types.InlineKeyboardButton(text=fav_button_title,
                                                    callback_data=fav_cd.new(
                                                        item_id=item_id,
                                                        previous_message=previous_message
                                                    ))]

    markup = types.InlineKeyboardMarkup(inline_keyboard=[favourites_button])
    return markup


async def create_navigation_block(call, next_url, previous_url, sent_messages):
    nav_markup = create_store_navigation(next_url, previous_url)
    if nav_markup['inline_keyboard'][0]:
        mess = await bot.send_message(call.from_user.id, f"Используйте стрелки для перехода по страницам",
                                      reply_markup=nav_markup)
        sent_messages.append(mess.message_id)


def get_telegram_text(name):
    url = API_CORE + f'telegram-text/?name={name}'
    response = requests.get(url)
    if response.status_code != 200:
        return 0
    if response.json():
        text = response.json()[0]['body']
        if len(text) > 0:
            return text
        return 0
    return 0


def update_telegram_text(name, content):
    url = API_CORE + f'telegram-text/?name={name}'
    response = requests.get(url)
    if response.status_code != 200:
        return 0
    if response.json():
        pk = response.json()[0]['id']
        response = requests.patch(url=API_CORE + f"telegram-text/{pk}/", json={'body': content})
        if response.status_code == 200:
            if response.json()['body'] == content:
                return 1
        return 0
    else:
        response = requests.post(API_CORE + f"telegram-text/", json={"body": content, "name": name})
        if response.status_code == 201:
            return 1
    return 0
