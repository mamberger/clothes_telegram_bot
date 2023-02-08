from aiogram import types
from aiogram.dispatcher import FSMContext
from utils.api import APIClient as API
from handlers.users.mixins import AlbumManager
from keyboards.inline.message_creation import photo_markup, send_markup
from keyboards.inline.store_buttons import cancel_markup
from states import states
from loader import dp, bot
from utils.messenger import Messenger


@dp.callback_query_handler(text='mailing')
async def ask_photos(call: types.CallbackQuery):
    await bot.send_message(
        call.from_user.id, 'Прикрепите фото или пропустите, нажав на кнопку ниже.',
        reply_markup=photo_markup
    )
    await states.Mailing.SetPhotos.set()


@dp.message_handler(state=states.Mailing.SetPhotos, content_types=types.ContentType.ANY)
async def handle_albums(message: types.Message, state: FSMContext, album=None):
    file_ids = []

    if album:
        file_ids = AlbumManager.get_file_ids(album)
    elif message.photo:
        file_ids.append(message.photo[0].file_id)

    if not file_ids:
        return await bot.send_message(
            message.from_user.id, 'Ошибка загрузки изображений. Попробуйте снова.\n'
                                  'Возможно, вы загружаете файлы неверного формата.',
            reply_markup=cancel_markup
        )

    await ask_text(message, state)
    await state.update_data(message_template={'photos': file_ids})


@dp.callback_query_handler(text='skip-photo', state=states.Mailing)
async def ask_text(message: types.Message, state: FSMContext):
    await bot.send_message(
        message.from_user.id,
        'Отправьте текст сообщения.',
        reply_markup=cancel_markup
    )

    await states.Mailing.SetText.set()
    await state.update_data(message_template={})


@dp.message_handler(state=states.Mailing.SetText)
async def set_text(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    state_data['message_template']['text'] = message.text

    recipient = [{'telegram_id': message.from_user.id}]

    await Messenger.start_mailing(
        [state_data['message_template']], recipient
    )

    await bot.send_message(
        message.from_user.id, 'Сообщения выше - шаблон вашей рассылки.'
                              '\nОтправить её пользователям?',
        reply_markup=send_markup
    )

    await state.reset_state()
    await state.set_data(state_data)


@dp.callback_query_handler(text='send-message')
async def send_message_handler(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    state_data = state_data['message_template']

    response = API.get('telegram-user/')
    result = await Messenger.start_mailing([state_data], response)

    if result:
        return await bot.send_message(message.from_user.id, 'Рассылка успешно отправлена.')


@dp.callback_query_handler(text='cancel', state=states.Mailing)
async def cancel_wo_state(message: types.Message, state: FSMContext):
    await bot.send_message(
        message.from_user.id,
        'Вы успешно отменили процесс создания рассылки.'
    )
    await state.reset_state()
