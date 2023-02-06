from aiogram.utils.callback_data import CallbackData

another_page_cd = CallbackData('another_page', 'prefix', 'next', 'previous')
gender_cd = CallbackData('gender', 'value')
quality_cd = CallbackData('quality', 'value')
filter_cd = CallbackData('filter', 'model', 'value')
update_cd = CallbackData('prefix', 'field')

