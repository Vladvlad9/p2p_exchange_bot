from aiogram.dispatcher.filters.state import StatesGroup, State


class BTCState(StatesGroup):
    UserCoin = State()
    UserPhoto = State()

