from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from handlers.users.mixins import mess_delete
from loader import bot
from utils.api import API


def filter_value_validation(func):
    """
    Декоратор проверяет существуют ли записи в бд, которые соотвествуют
    текущему набору значений фильтров.

    Если записи есть, последнее значение фильтра сохраняется к остальным.

    Если записей нет, тогда последний фильтр не сохраняется и пользователю
    предлагается выбрать другое значение для этого фильтра
    """

    async def wrapper(call: CallbackQuery, callback_data: dict, state: FSMContext):

        current_filter_data = get_current_filter_data(callback_data)
        initial_filter_data = await get_initial_filter_data(state)
        filter_data = initial_filter_data | current_filter_data
        print(filter_data)
        if API.get_by_query_string('item/', filter_data)['results']:
            await state.update_data(filter_params={**filter_data})
            await func(call, callback_data, state)
        else:
            mess = await bot.send_message(call.from_user.id,
                                          'По данным фильтрам ничего не найдено. '
                                          'Выберите другой вариант на предыдущем шаге'
                                          )
            await state.update_data(sent_messages=[mess.message_id])

    # ключ фильтра не может быть известен заранее. поэтому удаляем все лишние ключи,
    # оставляя лишь ключ и значение текущего фильтра
    def get_current_filter_data(callback_data):
        try:
            del callback_data['@']

            if callback_data['model']:
                callback_data[callback_data['model']] = callback_data['value']

            del callback_data['model']
            del callback_data['value']
        except KeyError:
            pass

        try:
            if callback_data.get('gender') == '0':
                del callback_data['gender']
        except KeyError:
            pass

        return callback_data

    async def get_initial_filter_data(state):
        initial_state_data = await state.get_data()

        try:
            initial_filter_data = initial_state_data['filter_params']
        except KeyError:
            initial_filter_data = {}

        return initial_filter_data

    return wrapper
