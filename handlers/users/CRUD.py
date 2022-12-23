import markups as markups
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import CallbackQuery
from aiogram.utils.callback_data import CallbackData

from loader import dp, bot
from states import states

cd_create = CallbackData("crud", "title", "description",
                         "gender", "quality", "price",
                         "media_group", "category", "brand")


@dp.message_handler(Command('item'))
async def start_adding_item(message: types.Message):
    await bot.send_message(message.from_user.id, 'Введите название')
    await states.Create.Title.set()


@dp.message_handler(state=states.Create)
async def title_set(message: types.Message):
    text = 'Название: '
    markup = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text='Далее',
                                        callback_data=cd_create.new(title=message.text, quality=0,
                                                                    description=0, price=0,
                                                                    gender=0, media_group=0,
                                                                    category=0, brannd=0))],
            [types.InlineKeyboardButton(text='Отмена',
                                        callback_data=f'cancel')]
        ]
    )
    await bot.send_message(message.from_user.id, text + message.text, reply_markup=markup)


# @dp.callback_query_handler(cd_create.filter())
# async def description_entering(callback_data: dict):
#     title = callback_data.get("title")


@dp.callback_query_handler(text='cancel')
async def cancel_wo_state(state: FSMContext):
    await state.reset_state()


@dp.callback_query_handler(text='cancel', state=states.Create)
async def cancel_wo_state(state: FSMContext):
    await state.reset_state()
