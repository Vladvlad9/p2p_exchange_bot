from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import BadRequest

from config import CONFIG
from crud import CRUDUsers, CRUDTransaction
from handlers.users.Cryptocurrency import Cryptocurrency
from loader import bot
from schemas import TransactionSchema
from states.users.MainState import MainState

admin_cb = CallbackData("main", "target", "action", "id", "editId")


class AdminForm:
    @staticmethod
    async def process_admin_profile(callback: CallbackQuery = None, message: Message = None,
                                    state: FSMContext = None) -> None:
        pass