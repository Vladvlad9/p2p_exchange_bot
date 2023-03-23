from aiogram.dispatcher.filters.state import StatesGroup, State


class AdminState(StatesGroup):
    COMMISSION = State()
    REQUISITES = State()

    CheckNumber = State()
    UsersId = State()

    CAPTCHA = State()
    CAPTCHA_TWO = State()

    NewsletterText = State()
    NewsletterPhoto = State()

    Timer = State()

    Verification = State()

    FIRST_PAGE = State()
    MAIN_FORM = State()
    Requisites = State()

    MinBYN = State()
    MinRUB = State()