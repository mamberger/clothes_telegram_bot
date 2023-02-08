import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from utils.api import APIClient as API
from data.config import API_CORE
from handlers.users.crud.read_item import find_item
from handlers.users.mixins import get_crud_menu, get_queryset
from loader import dp, bot
from states import states


# Круд меню для категории


@dp.callback_query_handler(text="CATEGORY")
async def category_crud_menu(call: CallbackQuery):
    await call.answer()
    await bot.send_message(call.from_user.id, f"Выберите операцию", reply_markup=get_crud_menu('CATEGORY'))


# Круд меню для брэнда
@dp.callback_query_handler(text="BRAND")
async def category_crud_menu(call: CallbackQuery):
    await call.answer()
    await bot.send_message(call.from_user.id, f"Выберите операцию", reply_markup=get_crud_menu('BRAND'))


# функция для осуществления READ операции для моделей brand и category
async def read(call, model):
    response = API.get(f'{model}/')
    qs = response['results']
    text = 'ID   Название\n'
    for element in qs:
        text += f"{element['id']}   {element['title']}\n"
    if len(text) > 4096:
        for x in range(0, len(text), 4096):
            await bot.send_message(call.from_user.id, text[x:x + 4096])
    else:
        await bot.send_message(call.from_user.id, text)


@dp.callback_query_handler(text_contains='_read')
async def object_read(call: CallbackQuery):
    await call.answer()
    split_callback = call.data.split('_')
    if not split_callback[0] == 'ITEM':
        await read(call, split_callback[0].lower())
    else:
        await find_item(call)


async def create(message: types.Message, state: FSMContext, model, title):
    url = API_CORE + f'{model}/'
    text = ''
    response = requests.post(url, data={'title': title})
    if response.status_code == 201:
        text = f'Объект успешно создан, он получил ID: {response.json()["id"]}'
    else:
        text = 'Не создан.'
    if response.content == b'{"title":["brand with this title already exists."]}':
        text = 'Не создан. Объект с таким названием уже существует.'
    await bot.send_message(message.from_user.id, text)
    try:
        await state.reset_state()
    except KeyError:
        pass


# хендлеры CREATE для category и brand
@dp.callback_query_handler(text='CATEGORY_create')
async def category_create(call: CallbackQuery):
    await call.answer()
    await bot.send_message(call.from_user.id, "Отправьте название нового объекта")
    await states.Create.CrudCategoryTitle.set()


@dp.message_handler(state=states.Create.CrudCategoryTitle)
async def category_create_title(message: types.Message, state: FSMContext):
    await create(message, state, 'category', message.text)


@dp.callback_query_handler(text='BRAND_create')
async def brand_create(call: CallbackQuery):
    await call.answer()
    await bot.send_message(call.from_user.id, "Отправьте название нового объекта")
    await states.Create.CrudBrandTitle.set()


@dp.message_handler(state=states.Create.CrudBrandTitle)
async def brand_create_title(message: types.Message, state: FSMContext):
    await create(message, state, 'brand', message.text)
