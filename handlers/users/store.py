from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from keyboards.default.client_base import base_markup
from utils.api import APIClient as API
from handlers.users.mixins import mess_delete, get_item_card_markup
from keyboards.inline.callback_data import store_nav_cd
from loader import dp, bot
from utils.store import send_item_card, send_store_navigation, get_favourite_markup_data, load_store_data_to_state


async def store_view(call: CallbackQuery,
                     state: FSMContext,
                     endpoint_response,
                     favourite):
    """
    Принимает словарь где по ключу 'results' расположен queryset.
    Выдает карточки элементов queryset пользователю.
    """

    await mess_delete(state, call.from_user.id)

    sent_messages = []
    queryset = endpoint_response['results']

    # Проверяем наличие товаров по нашим фильтрам, оповещаем об отсутствии товаров.
    if not queryset:
        mess = await bot.send_message(call.from_user.id, 'По запросу ничего не найдено.',
                                      reply_markup=base_markup)
        sent_messages.append(mess.message_id)
        await state.update_data(sent_messages=sent_messages)
        return

    fav_button_title, fav_cd = get_favourite_markup_data(favourite)

    for item in queryset:
        markup = get_item_card_markup(fav_button_title, fav_cd, item['id'])
        messages = await send_item_card(
            call.from_user.id, item, markup
        )
        sent_messages += messages

    # отправка сообщения с кнопками навигации и
    # добавления сообщения в список отправленных
    mess = await send_store_navigation(
        call.from_user.id, endpoint_response, favourite
    )
    sent_messages.append(mess.message_id) if mess else None

    store_data = {
        'state': state,
        'sent_messages': sent_messages,
        'endpoint_response': endpoint_response,
    }

    await load_store_data_to_state(store_data)


@dp.callback_query_handler(store_nav_cd.filter())
async def store_pagination(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await mess_delete(state, call.from_user.id)
    state_data = await state.get_data()

    if int(callback_data.get('next')):
        url = state_data['store_pagination']['next']
    else:
        url = state_data['store_pagination']['previous']

    favourite = int(callback_data.get('favourite'))
    response = API.get(url)

    await store_view(call, state, response, favourite)
