from aiogram.dispatcher.filters.state import StatesGroup, State


class ReloadState(StatesGroup):
    ReloadMoney = State()
    UserPhoto = State()
