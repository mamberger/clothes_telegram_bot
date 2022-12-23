from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData

import states.states
from handlers.users.mixins import mess_delete, get_telegram_text, update_telegram_text
from keyboards.inline.store_buttons import cancel_markup
from loader import dp, bot

texts_cd = CallbackData('texts_cd', 'text')


@dp.message_handler(text='FAQ 📑')
async def get_faq_text(message: types.Message, state: FSMContext):
    await mess_delete(state, message.from_user.id)
    sent_messages = [message.message_id]
    text = get_telegram_text('faq')
    if text:
        mess = await bot.send_message(message.from_user.id, text)
        sent_messages.append(mess.message_id)
    await state.update_data(sent_messages=sent_messages)


@dp.message_handler(text='Связь 📬')
async def get_contacts_text(message: types.Message, state: FSMContext):
    await mess_delete(state, message.from_user.id)
    sent_messages = [message.message_id]
    text = get_telegram_text('contacts')
    if text:
        mess = await bot.send_message(message.from_user.id, text)
        sent_messages.append(mess.message_id)
    await state.update_data(sent_messages=sent_messages)


# Управление текстами (из админского кабинета)
@dp.callback_query_handler(text='texts')
async def texts_menu(call: types.CallbackQuery):
    await call.answer()
    markup = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text='FAQ',
                                        callback_data=texts_cd.new(text='faq'))],
            [types.InlineKeyboardButton(text='Связь',
                                        callback_data=texts_cd.new(text='contacts'))]
        ]
    )
    await bot.send_message(call.from_user.id, 'Это меню редактирования текстов.', reply_markup=markup)


@dp.callback_query_handler(texts_cd.filter())
async def texts_update_ask(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer()
    await state.update_data(text_name=callback_data.get('text'))
    await bot.send_message(call.from_user.id, f"Отправьте новый текст", reply_markup=cancel_markup)
    await states.states.Update.Text.set()


@dp.message_handler(state=states.states.Update.Text)
async def texts_update_save(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.reset_state()
    if update_telegram_text(data['text_name'], message.text):
        return await bot.send_message(message.from_user.id, f'Текст успешно изменен.')
    return await bot.send_message(message.from_user.id, f'Неудалось изменить текст')
