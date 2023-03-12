from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart, Command
from utils.api import APIClient as API
from handlers.users.mixins import mess_delete
from keyboards.default.client_base import base_markup
from loader import dp, bot
from handlers.users.mixins import get_telegram_text


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message, state: FSMContext):
    await mess_delete(state, message.from_user.id)
    text = get_telegram_text('start')
    mess = await bot.send_message(message.from_user.id, text, reply_markup=base_markup)
    await bot.pin_chat_message(chat_id=message.from_user.id, message_id=mess.message_id)
    if not await state.get_data():
        API.create_telegram_user(message.from_user.id)
    await state.update_data(sent_messages=[mess.message_id - 1])


@dp.message_handler(Command('menu'))
async def get_main_keyboard(message: types.Message, state: FSMContext):
    await mess_delete(state, message.from_user.id)

    mess = await bot.send_message(message.from_user.id,
                                  'Клавиатура выдана',
                                  reply_markup=base_markup)

    await state.update_data(sent_messages=[mess.message_id - 1])
