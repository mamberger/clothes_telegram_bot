from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Main admin menu
crud = InlineKeyboardButton(text='Объекты', callback_data='CRUD')
team = InlineKeyboardButton(text='Команда', callback_data='team')
texts = InlineKeyboardButton(text='Тексты', callback_data='texts')
message = InlineKeyboardButton(text='Рассылка', callback_data='mailing')


lk_markup = InlineKeyboardMarkup()
lk_markup.row(crud).row(team, texts).row(message)

# CRUD menu
category = InlineKeyboardButton(text='Категория', callback_data='CATEGORY')
brand = InlineKeyboardButton(text='Брэнд', callback_data="BRAND")
item = InlineKeyboardButton(text='Товар', callback_data='ITEM')

crud_markup = InlineKeyboardMarkup()
crud_markup.row(item).row(category, brand)

# Team menu
add = InlineKeyboardButton(text='Добавить админа', callback_data='add_admin')
admin_list = InlineKeyboardButton(text='Список админов', callback_data='admin_list')
delete = InlineKeyboardButton(text='Удалить админа', callback_data='delete_admin')

team_markup = InlineKeyboardMarkup()
team_markup.row(add).row(admin_list).row(delete)

# CREATE ONE MORE ITEM
create = InlineKeyboardButton(text='Создать товар', callback_data='ITEM_create')

create_item_markup = InlineKeyboardMarkup()
create_item_markup.row(create)
