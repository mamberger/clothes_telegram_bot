from aiogram import types
from aiogram.dispatcher import FSMContext

import states.states
from data.config import API_CORE
from handlers.users.crud.update_object import execute_with_saving_state_data
from handlers.users.mixins import get_queryset
from handlers.users.store import send_item_card
from keyboards.inline.store_buttons import cancel_markup
from loader import bot, dp


async def find_item(call):
    await call.answer()
    await bot.send_message(call.from_user.id, f"Введите ID товара, который хотите просмотреть")
    await states.states.ReadItem.Id.set()


@dp.message_handler(state=states.states.ReadItem.Id)
async def show_item(message: types.Message, state: FSMContext):
    try:
        pk = int(message.text)
        url = API_CORE + f'item/{pk}/'
        data = get_queryset('item', custom_url=url)
        await send_item_card(message.from_user.id, data)
        await execute_with_saving_state_data(
            state.reset_state,
            state
        )
    except ValueError:
        return await bot.send_message(message.from_user.id, 'Неверный формат ID. Передайте число.',
                                      reply_markup=cancel_markup)


@dp.callback_query_handler(text='cancel', state=states.states.ReadItem)
async def cancel_read_item(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id, 'Вы успешно отменили процесс просмотра товара.')
    await execute_with_saving_state_data(state.reset_state, state)
