from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from handlers.users.mixins import mess_delete, get_queryset
from keyboards.inline.callback_data import another_page_cd, filter_cd
from keyboards.inline.store_buttons import quality_markup, quality_cd, gender_markup, gender_cd
from loader import dp, bot
from utils.api import APIClient
from utils.decorators import filter_value_validation
from utils.markup_creator import APIModelMarkupCreator


@dp.callback_query_handler(another_page_cd.filter())
@filter_value_validation
async def another_buttons_page_view(call: CallbackQuery, callback_data: dict,
                                    state: FSMContext):
    # определяем прошлую или следующую страницу клавиатуры
    # хочет получить пользователь и достаем url
    state_data = await state.get_data()
    if int(callback_data.get('next')):
        url = state_data.get('next_page')
    else:
        url = state_data.get('previous_page')

    prefix = callback_data.get('prefix')
    endpoint_response = get_queryset(prefix, url)

    markup = await APIModelMarkupCreator(prefix, endpoint_response, state).get_markup()

    await bot.send_message(call.from_user.id, text='Выберите нужный элемент',
                           reply_markup=markup)


@dp.message_handler(text='Подобрать одежду 🌐')
async def filter_start(message: types.Message, state: FSMContext):
    await mess_delete(state, message.from_user.id)
    mess = await bot.send_message(message.from_user.id, f'Выберите качество:', reply_markup=quality_markup)
    await state.update_data(sent_messages=[mess.message_id, mess.message_id - 1])


@dp.callback_query_handler(quality_cd.filter())
@filter_value_validation
async def quality_filter(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await mess_delete(state, call.from_user.id)
    mess = await bot.send_message(call.from_user.id, f'Выберите пол:', reply_markup=gender_markup)
    await state.update_data(sent_messages=[mess.message_id])


@dp.callback_query_handler(gender_cd.filter())
@filter_value_validation
async def gender_filter(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await mess_delete(state, call.from_user.id)
    state_data = await state.get_data()

    endpoint_response = APIClient.get_by_query_string(
        'brand/', state_data['filter_params']
    )

    markup = await APIModelMarkupCreator('brand', endpoint_response, state).get_markup()

    mess = await bot.send_message(call.from_user.id, f'Выберите брэнд:', reply_markup=markup)
    await state.update_data(sent_messages=[mess.message_id])


@dp.callback_query_handler(filter_cd.filter(model='brand'))
@filter_value_validation
async def category_filter(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await mess_delete(state, call.from_user.id)
    state_data = await state.get_data()

    endpoint_response = APIClient.get_by_query_string(
        'category/', state_data['filter_params']
    )
    markup = await APIModelMarkupCreator('category', endpoint_response, state).get_markup()

    mess = await bot.send_message(call.from_user.id, f'Выберите категорию:', reply_markup=markup)
    await state.update_data(sent_messages=[mess.message_id])
