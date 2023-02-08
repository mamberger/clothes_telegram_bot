from aiogram import types
from aiogram.dispatcher import FSMContext

from aiogram.utils.callback_data import CallbackData
from handlers.users.crud.brand_and_category_crud import read
from handlers.users.crud.update_object import update_save_changes
from handlers.users.mixins import get_crud_menu, get_preview_data, send_template_to_api, create_media_group
from keyboards.inline.admin_buttons import create_item_markup
from keyboards.inline.store_buttons import cancel_markup, template_markup
from loader import dp, bot
from states import states

cd_create_item = CallbackData("cd_create_item", "data")


# выбрасывает crud клавиатуру для модели item
# позволяет просмотреть, удалить, создать, редактировать айтемы
@dp.callback_query_handler(text='ITEM')
async def open_item_crud_menu(call: types.CallbackQuery):
    await call.answer()
    await bot.send_message(call.from_user.id, f'Выберите операцию', reply_markup=get_crud_menu('ITEM'))


@dp.callback_query_handler(text='ITEM_create')
async def item_create_title(call: types.CallbackQuery):
    await call.answer()
    await bot.send_message(call.from_user.id, 'Отправьте название товара', reply_markup=cancel_markup)
    await states.ItemCreate.Title.set()


@dp.message_handler(state=states.ItemCreate.Title)
async def item_create_title_check(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await bot.send_message(message.from_user.id, f'Отправьте описание товара', reply_markup=cancel_markup)
    await states.ItemCreate.Description.set()


@dp.message_handler(state=states.ItemCreate.Description)
async def item_create_description_check(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await bot.send_message(message.from_user.id, f'ID Пол\n'
                                                 f'1  М\n'
                                                 f'2  Ж\n'
                                                 f'3  Унисекс\n')
    await bot.send_message(message.from_user.id, f'Отправьте ID пола', reply_markup=cancel_markup)
    await states.ItemCreate.Gender.set()


@dp.message_handler(state=states.ItemCreate.Gender)
async def item_create_gender(message: types.Message, state: FSMContext):
    try:
        gender = int(message.text)
        if gender < 1 or gender > 3:
            raise ValueError()
        await state.update_data(gender=gender)
        await bot.send_message(message.from_user.id, f'ID Пол\n'
                                                     f'1  Top quality\n'
                                                     f'2  High quality - AAA +\n'
                                                     f'3  1: 1🤩\n')
        await bot.send_message(message.from_user.id, f'Отправьте ID нужного типа качества', reply_markup=cancel_markup)
        await states.ItemCreate.Quality.set()
    except ValueError:
        await bot.send_message(message.from_user.id, f'ID Пол\n'
                                                     f'1  М\n'
                                                     f'2  Ж\n'
                                                     f'3  Унисекс\n')
        await bot.send_message(message.from_user.id, 'Должно быть передано число. Отправьте ID Нужного пола.',
                               reply_markup=cancel_markup)


@dp.message_handler(state=states.ItemCreate.Quality)
async def item_create_quality(message: types.Message, state: FSMContext):
    try:
        quality = int(message.text)
        if quality < 1 or quality > 3:
            raise ValueError()
        await state.update_data(quality=quality)
        await bot.send_message(message.from_user.id, 'Отправьте цену товара', reply_markup=cancel_markup)
        await states.ItemCreate.Price.set()
    except ValueError:
        await bot.send_message(message.from_user.id, f'ID Тип качества\n'
                                                     f'1  Top quality\n'
                                                     f'2  High quality - AAA +\n'
                                                     f'3  1: 1🤩\n')
        await bot.send_message(message.from_user.id, 'Должно быть передано число. '
                                                     'Отправьте ID нужного типа качества', reply_markup=cancel_markup)


@dp.message_handler(state=states.ItemCreate.Price)
async def item_create_category(message: types.Message, state: FSMContext):
    try:
        int(message.text)
        await state.update_data(price=message.text)
        await read(message, 'category')
        await bot.send_message(message.from_user.id,
                               f'Отправьте ID нужной категории.\n'
                               f'Для ввода нескольких категорий разделите из запятыми'
                               f'Например: 1,2,3',
                               reply_markup=cancel_markup)
        await states.ItemCreate.Category.set()
    except ValueError:
        await bot.send_message(message.from_user.id, 'Должно быть передано число. Отправьте цену.',
                               reply_markup=cancel_markup)


@dp.message_handler(state=states.ItemCreate.Category)
async def item_create_brand(message: types.Message, state: FSMContext):
    try:
        categories = int(message.text)
        categories = [categories]
    except ValueError:
        try:
            if message.text.find(',') < 0:
                raise (ValueError('ID категорий должны быть переданы через запятую'))
            categories = message.text.replace(' ', '').split(',')
            for cat in categories:
                int(cat)
        except ValueError:
            await read(message, 'category')
            return await bot.send_message(message.from_user.id,
                                          'Должно быть передано число. '
                                          'Отправьте ID одним числом или через запятые.'
                                          ' Например: 1,2,3.\n',
                                          reply_markup=cancel_markup)

    await state.update_data(categories=categories)
    await read(message, 'brand')
    await bot.send_message(message.from_user.id, f'Отправьте ID нужного брэнда', reply_markup=cancel_markup)
    await states.ItemCreate.Brand.set()


@dp.message_handler(state=states.ItemCreate.Brand)
async def item_create_media_group(message: types.Message, state: FSMContext):
    try:
        brands = int(message.text)
        brands = [brands]
    except ValueError:
        try:
            if message.text.find(',') < 0:
                raise (ValueError('ID брэндов должны быть переданы через запятую'))
            brands = message.text.replace(' ', '').split(',')
            for brand in brands:
                int(brand)
        except ValueError:
            await read(message, 'brand')
            return await bot.send_message(message.from_user.id,
                                          'Должно быть передано число. '
                                          'Отправьте ID одним числом или через запятые.'
                                          ' Например: 1,2,3.\n',
                                          reply_markup=cancel_markup)

    await state.update_data(brands=brands)
    await bot.send_message(message.from_user.id, f'Отправьте фотографии (не более 9шт).', reply_markup=cancel_markup)
    await states.ItemCreate.Media_group.set()


@dp.message_handler(state=states.ItemCreate.Media_group, content_types=types.ContentType.ANY)
async def handle_albums(message: types.Message, state: FSMContext, album=None):
    markup = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text='Начать заново',
                                        callback_data=f'ITEM_create')]
        ]
    )
    data = await state.get_data()
    try:
        preview = data['preview']
    except KeyError:
        preview = True
    values = []
    content_type = 0
    if album:
        for obj in album:
            if obj.photo:
                file_id = obj.photo[-1].file_id
            else:
                file_id = obj[obj.content_type].file_id
            content_type = obj.content_type
            try:
                values.append(file_id)
            except ValueError:
                return await message.answer("Формат файла не поддерживается")
    else:
        values.append(message.photo[0].file_id)
    await state.update_data(photos=values)
    if not preview:
        result = create_media_group(values)
        if not result:
            await state.reset_state()
            return await bot.send_message(message.from_user.id, f"Ошибка")
        await update_save_changes(message, state, result)

    else:
        photos, text = await get_preview_data(state)
        if not photos and not text:
            await state.reset_state()
            return await bot.send_message(message.from_user.id,
                                          'Невозможно сформировать предпоказ карточки товара. '
                                          'Возможно, вы указали неверный ID категории или брэнда. '
                                          'Повторите процесс создания, будьте внимательны при указании этих пареметров.',
                                          reply_markup=markup)

        if not len(photos) == 1:
            media_group = types.MediaGroup()
            for photo in photos:
                try:
                    media_group.attach({"media": photo, "type": content_type})
                except ValueError:
                    pass
            await bot.send_media_group(message.from_user.id, media_group)
        await bot.send_photo(message.from_user.id, photo=photos[0],
                             caption=text, reply_markup=template_markup)


@dp.callback_query_handler(text='send_to_api', state=states.ItemCreate.Media_group)
async def save_template(call: types.CallbackQuery, state: FSMContext):
    res = await send_template_to_api(state)
    await state.reset_state()
    if res:
        return await bot.send_message(
            call.from_user.id, f"Товар успешно добавлен в базу под ID {res}",
            reply_markup=create_item_markup
        )

    await bot.send_message(
        call.from_user.id, f"Ошибка. Товар не был сохранен.",
        reply_markup=create_item_markup
    )


@dp.callback_query_handler(text='cancel', state=states.ItemCreate)
async def cancel_wo_state(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id, 'Вы успешно отменили процесс работы с Товаром.')
    await state.reset_state()
