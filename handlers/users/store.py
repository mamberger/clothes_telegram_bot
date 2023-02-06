from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import BadRequest

from data.config import API_CORE
from handlers.users.mixins import get_queryset, refactor_related_data, mess_delete, \
    get_item_card_markup, create_navigation_block
from keyboards.inline.callback_data import filter_cd
from loader import dp, bot

add_to_fav_cd = CallbackData('prefix', 'item_id', "previous_message")
remove_from_fav_cd = CallbackData('cd_prefix', 'item_id', "previous_message")

"""
 функция для отправки пользоватюлю карточки товара.
 поумолчанию привязка кнопок навигации отключена.
 для подключения навигации нужно передать navigation=True, i как порядковый номер товара в выборке
 next_url как url для получения следующей стр, previous_url url на прошлую
 query_len как len вышей выборки len(queryset)
"""


async def send_item_card(call, item, url, sent_messages, nav_and_fav=False,
                         i=None, next_url=None, previous_url=None, query_len=None):
    if not nav_and_fav:
        markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    try:
        item_card = f"{item['title']}\n\n" \
                    f"Артикул {item['id']}\n" \
                    f"Пол: {item['gender']}\n" \
                    f"Качество: {item['quality']}\n" \
                    f"Категория: {refactor_related_data(item['category'])}\n" \
                    f"Брэнд: {refactor_related_data(item['brand'])}\n\n" \
                    f"{item['description']}\n\n" \
                    f"{item['price']} ₽"
    except KeyError:
        return await bot.send_message(call.from_user.id, "Объект не найден")
    # формируем кнопку "добавить в избранное" или удаления из избранного
    # в зависимости от того, в каком контексте используется функция
    # если пользователь просматривает свои избранные, то в url будет фильтр subscribers
    if url.find('subscribers') >= 0:
        fav_button_title = 'Удалить ❌'
        fav_cd = remove_from_fav_cd
    else:
        fav_button_title = 'В избранное ⭐️'
        fav_cd = add_to_fav_cd
    # Вытаскиваем все фотографии товара
    # Запоминаем все отправленные сообщения из хендлера, дабы потом удалить их
    previous_messages = ''
    if item['media_group']:
        photos = []
        for photo in item['media_group']:
            photos.append(photo['file_id'])
        # Пытаемся создать из фотографий медиагруппу, если выйдет ошибка BadRequest от аиограм -
        # У нас 1 фото, тогда отсылаем только его.

        if len(photos) > 1:
            media_group = types.MediaGroup()
            for photo in photos:
                try:
                    media_group.attach({"media": photo, "type": "photo"})
                except ValueError:
                    print('value error')
                    # return await bot.send_photo(message.from_user.id, photo=photos[0], caption=text)
            mess_group = await bot.send_media_group(call.from_user.id, media_group)
            for mess in mess_group:
                sent_messages.append(mess.message_id)
                previous_messages += f"{mess.message_id},"
        if nav_and_fav:
            markup = get_item_card_markup(fav_button_title, fav_cd, item['id'],
                                          previous_messages[:-1])
        try:
            mess = await bot.send_photo(call.from_user.id, photo=photos[0],
                                        caption=item_card, reply_markup=markup)
            sent_messages.append(mess.message_id)
        except BadRequest:
            mess = await bot.send_message(call.from_user.id, item_card, reply_markup=markup)
            sent_messages.append(mess.message_id)
        if nav_and_fav:
            if i == query_len:
                await create_navigation_block(call, next_url, previous_url, sent_messages)
        return None
    if nav_and_fav:
        markup = get_item_card_markup(fav_button_title, fav_cd, item['id'],
                                      previous_messages)
    mess = await bot.send_message(call.from_user.id, item_card, reply_markup=markup)
    sent_messages.append(mess.message_id)
    if nav_and_fav:
        if i == query_len:
            await create_navigation_block(call, next_url, previous_url, sent_messages)


# хендлер отображения товаров
@dp.callback_query_handler(filter_cd.filter(model='category'))
async def store_view(call, state: FSMContext, url=None):
    print(await state.get_data())
    return 0
    # Удаляем предыдущее сообщение
    await mess_delete(state, call.from_user.id)
    sent_messages, chat_id = [], 0
    # Если юрл не передан, формируем его.
    if not url:
        #  Опеределяем передан набор фильтров для формирования url или уже готовый url
        if call.data.find('category-') >= 0:
            callback = call.data.replace('category-', '')
            url_filters = callback.split('-')
            url = API_CORE + f'item/?quality={url_filters[2]}&brand={url_filters[1]}&category={url_filters[0]}'
            if int(url_filters[-1]):
                url += f"&gender={url_filters[-1]}"
            print(url_filters)
        # в ином случае url для запроса уже сформирован в нашем callback, вытаскиваем его
        else:
            url = call.data.replace('pag=', API_CORE)
    data = get_queryset('item', custom_url=url)
    i = 0
    # Проверяем наличие товаров по нашим фильтрам, оповещаем об отсутствии товаров.
    if not data['results']:
        mess = await bot.send_message(call.from_user.id, 'По запросу ничего не найдено.')
        sent_messages.append(mess.message_id)
        await state.update_data(sent_messages=sent_messages)
        return 0
    # Формируем карточки товаров для каждого элемента выборки
    query_len = len(data['results'])
    for item in data['results']:
        i += 1
        await send_item_card(call, item, url, sent_messages,
                             True, i, data['next'], data['previous'], query_len)
    await state.update_data(sent_messages=sent_messages)


@dp.callback_query_handler(text_contains='pag=')
async def store_pagination(call: CallbackQuery, state: FSMContext):
    await mess_delete(state, call.from_user.id)
    await store_view(call, state)
