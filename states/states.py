from aiogram.dispatcher.filters.state import StatesGroup, State


class Create(StatesGroup):
    Title = State()
    CrudBrandTitle = State()
    CrudCategoryTitle = State()


class ItemCreate(StatesGroup):
    Title = State()
    Gender = State()
    Description = State()
    Price = State()
    Brand = State()
    Category = State()
    Media_group = State()
    Quality = State()


class Delete(StatesGroup):
    Item = State()
    Object = State()


class Update(StatesGroup):
    Id = State()
    Value = State()
    Text = State()


class ReadItem(StatesGroup):
    Id = State()


class Store(StatesGroup):
    Client = State()


class Team(StatesGroup):
    Add = State()
    Delete = State()
