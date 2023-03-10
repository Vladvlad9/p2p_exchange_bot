from aiogram.dispatcher.filters.state import StatesGroup, State


class MainState(StatesGroup):
    Wallet = State()
    UserPhoto = State()
    UserCoin = State()

    WalletRecipient = State()
    Money = State()
    ByeBTC = State()
