# adding photo to message
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline.store_buttons import cancel_button

photo_markup = InlineKeyboardMarkup(1)
skip_button = InlineKeyboardButton(text='Пропустить', callback_data='skip-photo')
photo_markup.insert(skip_button).insert(cancel_button)

send_markup = InlineKeyboardMarkup(1)
send_button = InlineKeyboardButton(text='Отправить', callback_data='send-message')
change_template_button = InlineKeyboardButton(text='Изменить', callback_data='mailing')

send_markup.insert(send_button).insert(change_template_button)
