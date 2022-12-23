from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Main admin menu
crud = InlineKeyboardButton(text='Объекты', callback_data='CRUD')
team = InlineKeyboardButton(text='Команда', callback_data='team')
texts = InlineKeyboardButton(text='Тексты', callback_data='texts')


lk_markup = InlineKeyboardMarkup()
lk_markup.row(crud).row(team).row(texts)

# CRUD menu
category = InlineKeyboardButton(text='Категория', callback_data='CATEGORY')
brand = InlineKeyboardButton(text='Брэнд', callback_data="BRAND")
item = InlineKeyboardButton(text='Товар', callback_data='ITEM')

crud_markup = InlineKeyboardMarkup()
crud_markup.row(category, brand).row(item)

# Team menu
add = InlineKeyboardButton(text='Добавить админа', callback_data='add_admin')
admin_list = InlineKeyboardButton(text='Список админов', callback_data='admin_list')
delete = InlineKeyboardButton(text='Удалить админа', callback_data='delete_admin')

team_markup = InlineKeyboardMarkup()
team_markup.row(add).row(admin_list).row(delete)