from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.callback_data import CallbackData

from handlers.users.mixins import get_model_markup, mess_delete, get_gender_markup
from keyboards.inline.store_buttons import quality_markup, quality_cd
from loader import dp, bot

gender_cd = CallbackData('filter_cd', 'quality', "gender")


@dp.message_handler(text='Подобрать одежду 🌐')
async def filter_start(message: types.Message, state: FSMContext):
    await mess_delete(state, message.from_user.id)
    mess = await bot.send_message(message.from_user.id, f'Выберите качество:', reply_markup=quality_markup)
    await state.update_data(sent_messages=[mess.message_id, mess.message_id - 1])


@dp.callback_query_handler(quality_cd.filter())
async def quality_filter(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await mess_delete(state, call.from_user.id)
    quality = callback_data.get('quality')
    markup = get_gender_markup(gender_cd, quality)
    mess = await bot.send_message(call.from_user.id, f'Выберите пол:', reply_markup=markup)
    await state.update_data(sent_messages=[mess.message_id])


@dp.callback_query_handler(gender_cd.filter())
async def gender_filter(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await mess_delete(state, call.from_user.id)
    callback = f"{callback_data.get('quality')}-{callback_data.get('gender')}"
    print(callback)
    markups = get_model_markup(callback, 'brand')
    mess = await bot.send_message(call.from_user.id, f'Выберите брэнд:', reply_markup=markups[0])
    await state.update_data(sent_messages=[mess.message_id])


@dp.callback_query_handler(text_contains='bran_page')
async def quality_page_filter(call: CallbackQuery, state: FSMContext):
    await mess_delete(state, call.from_user.id)
    data = call.data.split('=')
    callback = data[-1]
    page = int(data[1])
    markups = get_model_markup(callback, 'brand')

    mess = await bot.send_message(call.from_user.id, f'Выберите брэнд:', reply_markup=markups[page])

    await state.update_data(sent_messages=[mess.message_id])


"""callback типа model_page пишется без последней буквы в названии модели. Как: mode_page"""


@dp.callback_query_handler(text_contains='brand-')
async def category_filter(call: CallbackQuery, state: FSMContext):
    await mess_delete(state, call.from_user.id)
    callback = call.data.replace('brand-', '')
    markups = get_model_markup(callback, 'category')

    mess = await bot.send_message(call.from_user.id, f'Выберите категорию:', reply_markup=markups[0])
    await state.update_data(sent_messages=[mess.message_id])


@dp.callback_query_handler(text_contains='categor_page')
async def category_filter(call: CallbackQuery, state: FSMContext):
    await mess_delete(state, call.from_user.id)
    data = call.data.split('=')
    callback = data[-1]
    page = int(data[1])
    markups = get_model_markup(callback, 'category')

    mess = await bot.send_message(call.from_user.id, f'Выберите категорию:', reply_markup=markups[page])
    await state.update_data(sent_messages=[mess.message_id])
