from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

faq = KeyboardButton('FAQ 📑')
search = KeyboardButton('Подобрать одежду 🌐')
contact = KeyboardButton('Связь 📬')
favourites = KeyboardButton('Избранное ⭐️')

base_markup = ReplyKeyboardMarkup(resize_keyboard=True)
base_markup.row(search).row(faq, contact).row(favourites)
