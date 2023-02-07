from aiogram import types
from aiogram.utils.exceptions import ChatNotFound, BotBlocked

from loader import bot
from utils.api import APIClient


class BaseMessenger:
    Client = APIClient

    def __init__(self, text, photos):
        self.message_text = text
        self.media_file_ids = photos

    def start_mailing(self):
        raise NotImplementedError()


class Messenger(BaseMessenger):
    base_headers = None

    async def start_mailing(self):
        response = self.Client.get('telegram-user/')
        return await self.mailing_dispatcher(response)

    async def mailing_dispatcher(self, data):
        """
        Функция отправляющее сообщения всем пользователям в data
        Принимает data (list). В формате:
        [{'telegram_id': 11111}, ..., {'telegram_id': 2312551}]
        """
        if not data:
            raise ValueError('Empty data param')

        if not self.media_file_ids:
            return await self.send_default_messages(data, self.message_text)

        if len(self.media_file_ids) > 1:
            media_group = self.get_media_group(self.media_file_ids)
            return await self.send_media_group_messages(
                data, self.message_text, media_group
            )

        return await self.send_photo_messages(
            data, self.message_text, self.media_file_ids[0]
        )

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
    async def send_default_messages(data, text):
        for user in data:
            user_id = user['telegram_id']

            try:
                await bot.send_message(user_id, text)
            except (ChatNotFound, BotBlocked):
                pass

        return True

    @staticmethod
    async def send_media_group_messages(data, text, media_group):
        for user in data:
            user_id = user['telegram_id']

            try:
                await bot.send_media_group(user_id, media_group)
                await bot.send_message(user_id, text)
            except (ChatNotFound, BotBlocked):
                pass

        return True

    @staticmethod
    async def send_photo_messages(data, text, file_id):
        for user in data:
            user_id = user['telegram_id']

            try:
                await bot.send_photo(user_id, photo=file_id, caption=text)
            except (ChatNotFound, BotBlocked):
                pass

        return True
