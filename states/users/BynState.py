from aiogram.dispatcher.filters.state import StatesGroup, State


class BynState(StatesGroup):
    UserCoin = State()
    UserPhoto = State()

