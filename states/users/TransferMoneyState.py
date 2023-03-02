from aiogram.dispatcher.filters.state import StatesGroup, State


class TransferMoneyState(StatesGroup):
    WalletRecipient = State()
    Money = State()
