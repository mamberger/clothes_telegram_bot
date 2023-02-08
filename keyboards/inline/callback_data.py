from aiogram.utils.callback_data import CallbackData

# FILTERS
another_page_cd = CallbackData('another_page', 'prefix', 'next', 'previous')
gender_cd = CallbackData('gender_cd', 'gender')
quality_cd = CallbackData('quality_cd', 'quality')
filter_cd = CallbackData('filter', 'model', 'value')

# CRUD
update_cd = CallbackData('prefix', 'field')

# FAVOURITES
add_to_fav_cd = CallbackData('prefix', 'item_id', "previous_message")
remove_from_fav_cd = CallbackData('cd_prefix', 'item_id', "previous_message")

# STORE NAVIGATION
store_nav_cd = CallbackData('store_nav', 'next', 'previous', 'favourite')
