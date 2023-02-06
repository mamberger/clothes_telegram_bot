from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards.inline.callback_data import filter_cd, another_page_cd


class APIModelMarkupCreator:

    """
    Класс для создания клавиатур из моделей
    При создании экземпляра необходимо передать спагинированный ответ
    эндпоинта, где endpoint_response['next'] - следующая страница,
    endpoint_response['previous'] - прошлая страница,
    endpoint_response['results'] - список элементов выборки

    Названия кнопкам назначаются из значений ключа title
    каждого из элементов endpoint_response['results']

    Параметр state ожидает aiogram.dispatcher.FSMContext объект пользователя,
    для которого создается клавиатура.
    Поскольку в state записываются:
    endpoint_response['previous'], endpoint_response['next']

    prefix будет использован как префикс для callback_data
    """

    def __init__(self, model: str,
                 endpoint_response: dict,
                 state=None):
        self.models = endpoint_response.get('results')
        self.previous = endpoint_response.get('previous')
        self.next = endpoint_response.get('next')
        self.model = model
        self.state = state

        self.validate_data()

    async def get_markup(self):
        buttons = self.get_models_buttons()
        nav_buttons = await self.get_nav_buttons()

        if nav_buttons and self.state:
            await self.update_state()

        return types.InlineKeyboardMarkup(inline_keyboard=[buttons, nav_buttons])

    def get_models_buttons(self):
        buttons = []
        for model in self.models:
            button = types.InlineKeyboardButton(
                text=model['title'],
                callback_data=filter_cd.new(
                    model=self.model,
                    value=model['id']
                )
            )
            buttons.append(button)

        return buttons

    async def get_nav_buttons(self):
        nav_buttons = []
        if self.previous:
            previous_cd = another_page_cd.new(
                next=0,
                previous=1,
                prefix=self.model
            )

            button = types.InlineKeyboardButton(
                text='⬅️',
                callback_data=previous_cd
            )
            nav_buttons.append(button)

        if self.next:
            next_cd = another_page_cd.new(
                next=1,
                previous=0,
                prefix=self.model
            )

            button = types.InlineKeyboardButton(
                text='➡️',
                callback_data=next_cd
            )
            nav_buttons.append(button)

        return nav_buttons

    async def update_state(self):
        await self.state.update_data(
            next_page=self.next,
            previous_page=self.previous
        )

    def validate_data(self):
        if self.state and type(self.state) != FSMContext:
            raise TypeError(
                'state must be an instance of the class aiogram.dispatcher.FSMContext.'
            )

        if not self.models:
            self.models = [
                {'id': '', 'title': 'Пропустить'},
            ]
