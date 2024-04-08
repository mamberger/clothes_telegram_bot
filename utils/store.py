from aiogram import types

from data.config import API_CORE
from handlers.users.mixins import refactor_related_data
from keyboards.inline.callback_data import store_nav_cd, remove_from_fav_cd, add_to_fav_cd
from keyboards.inline.store_buttons import cancel_markup
from loader import bot
from utils.messenger import Messenger


async def send_store_navigation(user_id, endpoint_response, favourite):
    if endpoint_response['next'] or endpoint_response['previous']:
        nav_markup = get_store_navigation(
            endpoint_response['next'],
            endpoint_response['previous'],
            favourite
        )

        mess = await bot.send_message(
            user_id,
            'Используйте кнопки ниже для перемещения.',
            reply_markup=nav_markup
        )
        return mess


# Создание клавиатуры навигации. Переход к след. или пред. страницам выборки
def get_store_navigation(next_data, previous_data, favourite):
    navigation = []
    if next_data:
        next_data = next_data.replace(API_CORE, '')
    if previous_data:
        previous_data = previous_data.replace(API_CORE, '')

    if previous_data:
        navigation.append(types.InlineKeyboardButton(text=f'⬅️',
                                                     callback_data=store_nav_cd.new(
                                                         next=0,
                                                         previous=1,
                                                         favourite=favourite
                                                     )))
    if next_data:
        navigation.append(types.InlineKeyboardButton(text=f'➡️',
                                                     callback_data=store_nav_cd.new(
                                                         next=1,
                                                         previous=0,
                                                         favourite=favourite
                                                     )))

    return types.InlineKeyboardMarkup(inline_keyboard=[navigation])


async def get_item_card(user_id, item: dict):
    try:
        price = float(item['price'])
        price = '{0:,}0'.format(price).replace(',', ' ')

        item_card = f"{item['title']}\n\n" \
                    f"Артикул {item['id']}\n" \
                    f"Пол: {item['gender']}\n" \
                    f"Качество: {item['quality']}\n" \
                    f"Категория: {refactor_related_data(item['category'])}\n" \
                    f"Бренд: {refactor_related_data(item['brand'])}\n\n" \
                    f"{item['description']}\n\n" \
                    f"{price} ₽"
    except KeyError:
        return await bot.send_message(
            user_id, "Объект не найден",
            reply_markup=cancel_markup
        )

    return item_card


async def send_item_card(user_id, item, markup=None):
    item_card = await get_item_card(user_id, item)

    file_ids = []
    if item['media_group']:
        for photo in item['media_group']:
            file_ids.append(photo['file_id'])

    recipient = [
        {'telegram_id': user_id}
    ]
    message = [
        {
            'text': item_card,
            'photos': file_ids,
            'markup': markup
        }
    ]
    chat_histories = await Messenger.start_mailing(message, recipient)

    assert len(chat_histories) == 1, ('Объект мессенджера не отправил карточки товаров'
                                      ' или отправил их не тем пользователям')

    return chat_histories[0].messages


def get_favourite_markup_data(favourite):
    if not favourite:
        fav_button_title = 'Удалить ❌'
        fav_cd = remove_from_fav_cd
    else:
        fav_button_title = 'В избранное ⭐️'
        fav_cd = add_to_fav_cd

    return fav_button_title, fav_cd


async def load_store_data_to_state(data: dict):
    state = data['state']
    sent_messages = data['sent_messages']
    response = data['endpoint_response']
    await state.update_data(sent_messages=sent_messages)

    if response['next'] or response['previous']:

        _next = response['next']
        previous = response['previous']

        if response['next']:
            _next = response['next'].replace(API_CORE, '')
        if response['previous']:
            previous = response['previous'].replace(API_CORE, '')

        pagination_data = {
            'next': _next,
            'previous': previous
        }

        await state.update_data(store_pagination=pagination_data)
