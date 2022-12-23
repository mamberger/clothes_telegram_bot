from aiogram import types
from aiogram.dispatcher import FSMContext

from handlers.users.mixins import get_model_fields_markup, update_cd, update_model
from keyboards.inline.store_buttons import cancel_markup
from loader import dp, bot
from states import states


@dp.callback_query_handler(text_contains='_update')
async def update_ask_id(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(model=call.data.split('_')[0].lower())
    await bot.send_message(call.from_user.id, f"Введите ID нужного объекта", reply_markup=cancel_markup)
    await states.Update.Id.set()


@dp.message_handler(state=states.Update.Id)
async def update_ask_field(message: types.Message, state: FSMContext):
    try:
        int(message.text)
    except ValueError:
        return await bot.send_message(message.from_user.id, f"Неверный формат ID. Введите ID с помощью цифр.",
                                      reply_markup=cancel_markup)
    await state.update_data(id=message.text)
    data = await state.get_data()
    markup = get_model_fields_markup(message.text, data['model'])
    if not markup:
        return await bot.send_message(message.from_user.id, f"Ошибка. Проверьте правильность введенного ID.",
                                      reply_markup=cancel_markup)
    await bot.send_message(message.from_user.id, f"Выберите поле, которое хотите изменить:",
                           reply_markup=markup)


@dp.callback_query_handler(update_cd.filter(), state=states.Update.Id)
async def update_ask_value(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await state.update_data(field=callback_data.get('field'))
    if callback_data.get('field') == 'media_group':
        await bot.send_message(call.from_user.id, f'Отправьте фотографии (не более 9шт).',
                               reply_markup=cancel_markup)
        await state.update_data(preview=False)
        await states.ItemCreate.Media_group.set()
    else:
        await bot.send_message(call.from_user.id, f"СПРАВКА\n"
                                                  f"При редактировании связующих полей(например брэнд или категория)"
                                                  f" в качестве значения передавайте ID"
                                                  f" нужных брендов или категорий.\n\n"
                                                  f"В таком случае, вам может понадобиться передать несколько значений."
                                                  f" Тогда <b>сначала</b> напечатайте !список!\n"
                                                  f" После чего введите значения через запятые.\n"
                                                  f"<b>Пример</b>: !список! 15, 6, 3")
        await bot.send_message(call.from_user.id, f"Введите новое значение для выбранного поля.",
                               reply_markup=cancel_markup)
        await states.Update.Value.set()


@dp.message_handler(state=states.Update.Value)
async def update_save_changes(message: types.Message, state: FSMContext, third_party_value=None):
    if third_party_value:
        value = third_party_value
    else:
        value = message.text
    try:
        if value.find('!список!') >= 0:
            value = value.replace(' ', '').replace('!список!', '').split(',')
            value = [int(item) for item in value]
    except AttributeError:
        pass
    await state.update_data(value=value)
    data = await state.get_data()
    await state.reset_state()
    if update_model(data):
        return await bot.send_message(message.from_user.id, f"Объект успешно изменен.")
    markup = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text='Начать заново',
                                        callback_data=f'{data["model"].upper()}_update')]
        ]
    )
    return await bot.send_message(message.from_user.id, f'Неудалось изменить объект. '
                                                        f'Попробуйте еще раз, внимательно проверьте '
                                                        f'правильность вводимых данных',
                                  reply_markup=markup)


@dp.callback_query_handler(text='cancel', state=states.Update)
async def cancel_wo_state(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id, 'Вы успешно отменили процесс редактирования Объекта.')
    await state.reset_state()
