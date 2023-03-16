from aiogram import types
from aiogram.utils.exceptions import ChatNotFound, BotBlocked
from keyboards.default.client_base import base_markup
from loader import bot
from utils.api import APIClient


class BaseChatHistory:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.messages = []

    def __repr__(self):
        return f'{self.__class__} chat {self.chat_id}'


class UserChatHistory(BaseChatHistory):
    pass


class BaseChatHistoryManager:
    chat_history = UserChatHistory

    @classmethod
    def get_chat_history(cls, chat_id, collection) -> BaseChatHistory:
        raise NotImplementedError()


class ChatHistoryManager(BaseChatHistoryManager):
    @classmethod
    def get_chat_history(cls, chat_id, collection: list):
        for obj in collection:
            print(obj)
            if obj.chat_id == chat_id:
                return obj

        return cls.chat_history(chat_id)


class BaseMessenger:
    Client = APIClient

    @classmethod
    def start_mailing(cls, message_templates: list, users: list):
        raise NotImplementedError()


class Messenger(BaseMessenger):
    base_headers = None
    history_manager = ChatHistoryManager

    @classmethod
    async def start_mailing(cls, message_templates, users):
        chat_histories = []
        for template in message_templates:
            chat_histories = await cls.mailing_dispatcher(
                users, template['text'],
                template.get('photos', []),
                chat_histories,
                template.get('markup', None),
            )

        return chat_histories

    @classmethod
    async def mailing_dispatcher(cls,
                                 users,
                                 message_text,
                                 media_file_ids,
                                 chat_histories,
                                 markup=None):

        """
        Функция отправляющее сообщениt всем пользователям в users
        Принимает users (list). В формате:
        [{'telegram_id': 11111}, ..., {'telegram_id': 2312551}]
        """

        for user in users:
            user_id = user['telegram_id']

            chat_history = cls.history_manager.get_chat_history(user_id, chat_histories)

            if not media_file_ids:
                mess_list = await cls.send_default_message(user_id, message_text, markup)

            elif len(media_file_ids) > 1:
                media_group = cls.get_media_group(media_file_ids)
                mess_list = await cls.send_media_group_message(
                    user_id, message_text, media_group, markup
                )

            else:
                mess_list = await cls.send_photo_message(
                    user_id, message_text, media_file_ids[0], markup
                )

            chat_history.messages += mess_list
            chat_histories.append(chat_history)

        return chat_histories

    @staticmethod
    def get_media_group(file_ids):
        media_group = types.MediaGroup()
        for _id in file_ids:
            try:
                media_group.attach({"media": _id, "type": "photo"})
            except ValueError:
                pass
        return media_group

    @staticmethod
    async def send_default_message(user_id, text, markup=None):
        try:
            mess = await bot.send_message(user_id, text, reply_markup=markup)
        except (ChatNotFound, BotBlocked):
            return

        return [mess.message_id]

    @staticmethod
    async def send_media_group_message(user_id, text, media_group, markup=None):
        try:
            mess_group = await bot.send_media_group(user_id, media_group)
            mess_group = [str(mess.message_id) for mess in mess_group]
            if markup:
                if markup.inline_keyboard[0][0].text == 'Удалить ❌':
                    markup.inline_keyboard[0][0].callback_data = markup.inline_keyboard[0][0].callback_data.replace('[]', ','.join(mess_group))
            else:
                markup = base_markup
            mess = await bot.send_message(user_id, text, reply_markup=markup)
        except (ChatNotFound, BotBlocked):
            return

        mess_group.append(mess.message_id)
        return mess_group

    @staticmethod
    async def send_photo_message(user_id, text, file_id, markup=None):
        try:
            photo_mess = await bot.send_photo(user_id, photo=file_id)
            photo_mess = str(photo_mess.message_id)

            if markup:
                if markup.inline_keyboard[0][0].text == 'Удалить ❌':
                    markup.inline_keyboard[0][0].callback_data = markup.inline_keyboard[0][0].callback_data.replace('[]', photo_mess)
            else:
                markup = base_markup
            mess = await bot.send_message(user_id, text=text, reply_markup=markup)
        except (ChatNotFound, BotBlocked):
            return

        return [photo_mess, mess.message_id]
