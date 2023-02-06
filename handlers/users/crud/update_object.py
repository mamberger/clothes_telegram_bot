from aiogram import types
from aiogram.dispatcher import FSMContext

from handlers.users.mixins import get_model_fields_markup, update_cd
from keyboards.inline.store_buttons import cancel_markup
from loader import dp, bot
from states import states
from utils.api import API


async def execute_with_saving_state_data(func, state):
    state_data = await state.get_data()
    await func()
    await state.set_data(state_data)

    return state_data


@dp.callback_query_handler(text_contains='_update')
async def update_ask_id(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
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
    state_data = await execute_with_saving_state_data(
        state.reset_state, state
    )

    markup = get_model_fields_markup(message.text, state_data['model'])
    if not markup:
        return await bot.send_message(message.from_user.id, f"Ошибка. Проверьте правильность введенного ID.",
                                      reply_markup=cancel_markup)
    await bot.send_message(message.from_user.id, f"Выберите поле, которое хотите изменить:",
                           reply_markup=markup)


@dp.callback_query_handler(update_cd.filter())
async def update_ask_value(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await state.update_data(field=callback_data.get('field'))
    field = callback_data.get('field')

    if field == 'brand' or field == 'category':
        await bot.send_message(call.from_user.id, f"СПРАВКА\n"
                                                  f"При редактировании связующих полей(например брэнд или категория)"
                                                  f" в качестве значения передавайте ID"
                                                  f" нужных брендов или категорий.\n\n"
                                                  f"В таком случае, вам может понадобиться передать несколько значений."
                                                  f" Тогда <b>сначала</b> напечатайте !список!\n"
                                                  f" После чего введите значения через запятые.\n"
                                                  f"<b>Пример</b>: !список! 15, 6, 3")

    if field == 'media_group':
        await bot.send_message(call.from_user.id, f'Отправьте фотографии (не более 9шт).',
                               reply_markup=cancel_markup)
        await state.update_data(preview=False)
        await execute_with_saving_state_data(
            states.ItemCreate.Media_group.set,
            state
        )
    else:
        await bot.send_message(call.from_user.id, f"Введите новое значение для выбранного поля.",
                               reply_markup=cancel_markup)
        await execute_with_saving_state_data(
            states.Update.Value.set,
            state
        )


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

    data = await execute_with_saving_state_data(
        state.reset_state,
        state
    )

    if API.update_model(data):
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
    await execute_with_saving_state_data(state.reset_state, state)
