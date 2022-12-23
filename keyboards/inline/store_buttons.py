from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

quality_cd = CallbackData('filter_cd', 'quality')

top = InlineKeyboardButton(text='Top quality', callback_data=quality_cd.new(quality=1))
high = InlineKeyboardButton(text='High quality - AAA+', callback_data=quality_cd.new(quality=2))
one_to_one = InlineKeyboardButton(text='1:1🤩', callback_data=quality_cd.new(quality=3))

quality_markup = InlineKeyboardMarkup()
quality_markup.insert(top).insert(one_to_one).insert(high)

# CANCEL
cancel_markup = InlineKeyboardMarkup(1)
cancel_button = InlineKeyboardButton(text='Отмена', callback_data='cancel')
cancel_markup.insert(cancel_button)

send = InlineKeyboardButton(text='Сохранить', callback_data='send_to_api')

template_markup = InlineKeyboardMarkup()
template_markup.insert(send).insert(cancel_button)
