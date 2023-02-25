import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData

from data.config import API_CORE
from handlers.users.mixins import delete_model
from keyboards.inline.store_buttons import cancel_markup
from loader import dp, bot
from states import states

cd_delete = CallbackData("del_cd", "pk", "model")


@dp.callback_query_handler(text_contains="_delete")
async def delete_ask_pk(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    model = call.data.split('_')[0].lower()
    await bot.send_message(call.from_user.id, f'Отправьте ID Объекта, который хотите удалить.')
    await states.Delete.Object.set()
    await state.update_data(model=model)


@dp.message_handler(state=states.Delete.Object)
async def delete_check(message: types.Message, state: FSMContext):
    data = await state.get_data()
    try:
        pk = int(message.text)
    except ValueError:
        return await bot.send_message(message.from_user.id, f'Ошибка. Введите ID с помощью цифр.',
                                      reply_markup=cancel_markup)

    markup = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text='Удалить',
                                        callback_data=cd_delete.new(pk=pk,
                                                                    model=data['model']))],
            [types.InlineKeyboardButton(text='Отмена',
                                        callback_data=f'cancel')],
        ]
    )

    response = requests.get(API_CORE + f'{data["model"]}/{message.text}/')
    if response.status_code == 404:
        return await bot.send_message(message.from_user.id,
                                      f"Объект с таким ID не найден. Попробуйте ввести ID еще раз",
                                      reply_markup=cancel_markup)
    try:
        title = response.json()['title']
    except KeyError:
        await state.reset_state()
        return await bot.send_message(message.from_user.id, "Ошибка, проверьте правильность вводимых данных")
    await state.reset_state()
    await bot.send_message(message.from_user.id,
                           f'Вы действительно хотите удалить объект "{title}"?',
                           reply_markup=markup)


@dp.callback_query_handler(cd_delete.filter())
async def delete_object(call: types.CallbackQuery, callback_data: dict):
    await delete_model(call, callback_data.get('pk'), callback_data.get('model'))


@dp.callback_query_handler(text='cancel')
async def cancel_wo_state(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id, 'Вы успешно отменили процесс.')
    await state.reset_state()
