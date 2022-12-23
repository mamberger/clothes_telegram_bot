from aiogram.dispatcher.filters import Command
from aiogram.types import CallbackQuery

from handlers.users.mixins import admin_auth
from keyboards.inline.admin_buttons import lk_markup, crud_markup, team_markup
from loader import dp, bot


# Открытие панели администратора, проверка прав
@dp.message_handler(Command('lk'))
async def open_lk(call: CallbackQuery):
    if admin_auth(call.from_user.id):
        await bot.send_message(call.from_user.id, "Доступ получен.", reply_markup=lk_markup)


# Открытие меню CRUD в панели администратора
@dp.callback_query_handler(text='CRUD')
async def open_crud_menu(call: CallbackQuery):
    await bot.send_message(call.from_user.id, f"С чем будем работать, шеф?", reply_markup=crud_markup)


# Открытие меню Команда в панели администратора
@dp.callback_query_handler(text='team')
async def open_crud_menu(call: CallbackQuery):
    await bot.send_message(call.from_user.id, f"Меню управления командой", reply_markup=team_markup)
