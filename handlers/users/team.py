from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from handlers.users.mixins import add_new_admin, get_admin_list_text, delete_admin
from loader import dp, bot
from states import states


# Хендлеры создания нового админа
@dp.callback_query_handler(text='add_admin')
async def add_admin_ask_id(call: CallbackQuery):
    await call.answer()
    await bot.send_message(call.from_user.id, 'Отправь ID нового админа')
    await states.Team.Add.set()


@dp.message_handler(state=states.Team.Add)
async def add_admin(message: types.Message, state: FSMContext):
    try:
        new_admin = int(message.text)
    except ValueError:
        return await bot.send_message(message.from_user.id,
                                      'Неверный формат ID. Отправь ID нового админа, используя цифры')

    await state.reset_state()

    if add_new_admin(new_admin):
        return await bot.send_message(message.from_user.id, f'Юзер {new_admin} наш новый админ.')
    return await bot.send_message(message.from_user.id, f'Неудалось добавить админа.')


# Хендлер показа списка всех админов
@dp.callback_query_handler(text='admin_list')
async def admin_list_view(call: CallbackQuery):
    await call.answer()
    text = get_admin_list_text()
    await bot.send_message(call.from_user.id, text)


# Хендлеры удаления админа
@dp.callback_query_handler(text='delete_admin')
async def delete_admin_ask_id(call: CallbackQuery):
    await call.answer()
    await bot.send_message(call.from_user.id, 'Введите ID админа, которого хотите лишить прав.')
    await states.Team.Delete.set()


@dp.message_handler(state=states.Team.Delete)
async def delete_admin_from_list(message: types.Message, state: FSMContext):
    try:
        int(message.text)
    except ValueError:
        return await bot.send_message(message.from_user.id,
                                      'Неверный формат ID. Отправь ID, используя цифры')

    await state.reset_state()
    if delete_admin(message.text):
        return await bot.send_message(message.from_user.id, f'С нами больше не работает.')
    return await bot.send_message(message.from_user.id, f'Неудалось удалить администратора.')
