from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


# QUALITY MARKUP
from keyboards.inline.callback_data import quality_cd, gender_cd

top = InlineKeyboardButton(text='Top quality', callback_data=quality_cd.new(value=1))
high = InlineKeyboardButton(text='High quality - AAA+', callback_data=quality_cd.new(value=2))
one_to_one = InlineKeyboardButton(text='1:1🤩', callback_data=quality_cd.new(value=3))

quality_markup = InlineKeyboardMarkup()
quality_markup.insert(top).insert(one_to_one).insert(high)

# GENDER MARKUP
m = InlineKeyboardButton(text='Мужской', callback_data=gender_cd.new(value=1))
w = InlineKeyboardButton(text='Женский', callback_data=gender_cd.new(value=2))
all_genders = InlineKeyboardButton(text='Унисекс', callback_data=gender_cd.new(value=3))
skip = InlineKeyboardButton(text='Пропустить', callback_data=gender_cd.new(value=0))

gender_markup = InlineKeyboardMarkup()
gender_markup.insert(m).insert(w).insert(all_genders).insert(skip)

# CANCEL
cancel_markup = InlineKeyboardMarkup(1)
cancel_button = InlineKeyboardButton(text='Отмена', callback_data='cancel')
cancel_markup.insert(cancel_button)

send = InlineKeyboardButton(text='Сохранить', callback_data='send_to_api')

template_markup = InlineKeyboardMarkup()
template_markup.insert(send).insert(cancel_button)
