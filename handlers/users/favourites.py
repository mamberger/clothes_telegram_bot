import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageToDeleteNotFound, MessageCantBeDeleted

from data.config import API_CORE
from handlers.users.mixins import mess_delete
from handlers.users.store import store_view
from keyboards.inline.callback_data import remove_from_fav_cd, add_to_fav_cd
from loader import dp, bot
from utils.api import APIClient as API


@dp.message_handler(text='Избранное ⭐️')
async def show_favourites(message: types.Message, state: FSMContext):
    await message.delete()
    await mess_delete(state, message.from_user.id)
    pk = API.get_or_create_user(message.from_user.id)
    if pk:
        filter_params = {'subscribers': pk}
        response = API.get_by_query_string('item/', filter_params)
        await store_view(message, state, response, 0)


@dp.callback_query_handler(add_to_fav_cd.filter())
async def add_to_fav(call: types.CallbackQuery, callback_data: dict):
    if update_favourites(call.from_user.id, callback_data.get('item_id')):
        await call.answer('Товар добавлен в избранное', show_alert=False)


@dp.callback_query_handler(remove_from_fav_cd.filter())
async def remove_from_fav(call: types.CallbackQuery, callback_data: dict):
    if update_favourites(call.from_user.id, callback_data.get('item_id'), True):
        await call.answer('Товар удален из избранного', show_alert=False)
        try:
            messages = callback_data.get('previous_message').split(',')
            print(messages)
            messages.append(call.message.message_id)
            for mess in messages:
                try:
                    await bot.delete_message(call.from_user.id, int(mess))
                except (ValueError, MessageCantBeDeleted):
                    pass
        except MessageToDeleteNotFound:
            pass


# функция обновления списка избранных товаров
def update_favourites(telegram_id, item_id, delete=False):
    # получаем список людей уже подписанных на наш товар
    response = requests.get(url=API_CORE + f"item/{item_id}/")
    if response.status_code == 200:
        if response.json():
            current_subscribers = response.json()['subscribers']
        else:
            return 0
    else:
        return 0
    # получаем информацию о юзере, если юзера нет, то создаем его
    pk = API.get_or_create_user(telegram_id)
    if pk:
        # Обновляем список людей подписанных на наш товар (удаляем или добавляем текущего пользователя)
        if delete:
            if pk in current_subscribers:
                current_subscribers.remove(pk)
        else:
            if pk in current_subscribers:
                return 0
            current_subscribers.append(pk)
        response = requests.patch(url=API_CORE + f"item/{item_id}/",
                                  json={"subscribers": current_subscribers})
        if response.status_code == 200:
            if response.json()['subscribers'] == current_subscribers:
                return 1
    return