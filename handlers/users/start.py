import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart

from handlers.users.mixins import mess_delete, create_telegram_user
from keyboards.default.client_base import base_markup
from loader import dp, bot
from utils.markup_creator import APIModelMarkupCreator


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message, state: FSMContext):
    await mess_delete(state, message.from_user.id)
    mess = await bot.send_message(message.from_user.id, 'Перезапуск', reply_markup=base_markup)
    if not await state.get_data():
        create_telegram_user(message.from_user.id)
    await state.update_data(sent_messages=[mess.message_id, mess.message_id - 1])
