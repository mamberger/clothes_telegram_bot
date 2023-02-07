from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from handlers.users.crud.update_object import execute_with_saving_state_data
from utils.api import APIClient as API
from keyboards.inline.store_buttons import cancel_markup
from loader import dp, bot
from states import states


# Хендлеры создания нового админа
@dp.callback_query_handler(text='add_admin')
async def add_admin_ask_id(call: CallbackQuery):
    await call.answer()
    await bot.send_message(call.from_user.id, 'Отправь ID нового админа',
                           reply_markup=cancel_markup)
    await states.Team.Add.set()


@dp.message_handler(state=states.Team.Add)
async def add_admin(message: types.Message, state: FSMContext):
    try:
        new_admin = int(message.text)
    except ValueError:
        return await bot.send_message(message.from_user.id,
                                      'Неверный формат ID. Отправь ID нового админа, используя цифры',
                                      reply_markup=cancel_markup)

    await state.reset_state()

    if API.add_new_admin(new_admin):
        return await bot.send_message(message.from_user.id, f'Юзер {new_admin} наш новый админ.')
    return await bot.send_message(message.from_user.id, f'Неудалось добавить админа.')


# Хендлер показа списка всех админов
@dp.callback_query_handler(text='admin_list')
async def admin_list_view(call: CallbackQuery):
    await call.answer()
    text = API.get_admin_list_text()
    await bot.send_message(call.from_user.id, text)


# Хендлеры удаления админа
@dp.callback_query_handler(text='delete_admin')
async def delete_admin_ask_id(call: CallbackQuery):
    await call.answer()
    await bot.send_message(call.from_user.id, 'Введите ID админа, которого хотите лишить прав.',
                           reply_markup=cancel_markup)
    await states.Team.Delete.set()


@dp.message_handler(state=states.Team.Delete)
async def delete_admin_from_list(message: types.Message, state: FSMContext):
    try:
        int(message.text)
    except ValueError:
        return await bot.send_message(message.from_user.id,
                                      'Неверный формат ID. Отправь ID, используя цифры',
                                      reply_markup=cancel_markup)

    await state.reset_state()
    if API.delete_admin(message.text):
        return await bot.send_message(message.from_user.id, f'С нами больше не работает.')
    return await bot.send_message(message.from_user.id, f'Неудалось удалить администратора.')


@dp.callback_query_handler(text='cancel', state=states.Team)
async def cancel_wo_state(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id, 'Вы успешно отменили процесс увправления командой.')
    await execute_with_saving_state_data(state.reset_state, state)
