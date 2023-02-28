from aiogram.dispatcher.filters.state import StatesGroup, State


class AdminState(StatesGroup):
    COMMISSION = State()
    REQUISITES = State()

    CheckNumber = State()
    UsersId = State()

    CAPTCHA = State()
    CAPTCHA_TWO = State()