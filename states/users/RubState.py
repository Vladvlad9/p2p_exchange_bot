from aiogram.dispatcher.filters.state import StatesGroup, State


class RubState(StatesGroup):
    UserCoin = State()
    UserPhoto = State()

