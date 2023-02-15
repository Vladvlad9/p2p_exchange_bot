from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import BadRequest

from handlers.users.Cryptocurrency import Cryptocurrency
from loader import bot
from states.users.MainState import MainState

main_cb = CallbackData("main", "target", "action", "id", "editId")


class MainForm:
    @staticmethod
    async def back_ikb(user_id: int, target: str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Назад", callback_data=main_cb.new(target, 0, 0, user_id))
                ]
            ]
        )

    @staticmethod
    async def money_ikb(user_id: int, target: str) -> InlineKeyboardMarkup:
        data = {"50 BYN": {"target": "Pay", "action": "get_pay", "id": "50", "editid": user_id},
                "100 BYN": {"target": "Pay", "action": "get_pay", "id": "100", "editid": user_id},
                "200 BYN": {"target": "Pay", "action": "get_pay", "id": "200", "editid": user_id},
                }
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=name, callback_data=main_cb.new(items["target"],
                                                                              items["action"],
                                                                              items["id"],
                                                                              items["editid"]))
                    for name, items in data.items()
                ],
                [
                    InlineKeyboardButton(text="✍️ Ввести сумму", callback_data=main_cb.new(target, 0, 0, user_id))
                ],
                [
                    InlineKeyboardButton(text="◀️ Назад", callback_data=main_cb.new(target, 0, 0, user_id))
                ]
            ]
        )

    @staticmethod
    async def bue_ikb(user_id: int, target: str, count: float) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Купить", callback_data=main_cb.new("Buy", 0, count, user_id))
                ],
                [
                    InlineKeyboardButton(text="◀️ Назад", callback_data=main_cb.new(target, 0, 0, user_id))
                ]
            ]
        )

    @staticmethod
    async def wallet_ikb(user_id: int, target: str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Ввести кошелек", callback_data=main_cb.new("WalletEnter",
                                                                                          0, 0, user_id))
                ],
                [
                    InlineKeyboardButton(text="◀️ Назад", callback_data=main_cb.new(target, 0, 0, user_id))
                ]
            ]
        )

    @staticmethod
    async def start_ikb(user_id: int) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="💳 Купить BTC", callback_data=main_cb.new("BuyBTC", 0, 0, user_id))
                ],
                [
                    InlineKeyboardButton(text="💳 Продать BTC", callback_data=main_cb.new("SellBTC", 0, 0, user_id))
                ]
            ]
        )

    @staticmethod
    async def process_profile(callback: CallbackQuery = None, message: Message = None,
                              state: FSMContext = None) -> None:

        if callback:
            if callback.data.startswith('main'):
                data = main_cb.parse(callback_data=callback.data)
                if data.get("target") == "MainForm":
                    await callback.message.edit_text(text="Добро пожаловать\n"
                                                          "Выберите операцию",
                                                     reply_markup=await MainForm.start_ikb(
                                                         user_id=callback.from_user.id)
                                                     )

                elif data.get("target") == "BuyBTC":
                    price = await Cryptocurrency.get_Cryptocurrency()
                    await callback.message.edit_text(text="💳 Купить криптовалюту: BTC за BYN\n"
                                                          f"1 Bitcoin = {price} BYN\n\n"
                                                          f"<i>Мин. сумма: 50.0 BYN</i>",
                                                     reply_markup=await MainForm.money_ikb(
                                                         user_id=callback.from_user.id,
                                                         target="MainForm"),
                                                     parse_mode="HTML"
                                                     )

                elif data.get("target") == "Pay":
                    if data.get("action") == "get_pay":
                        price_BYN = int(data.get("id"))
                        price_BTC = await Cryptocurrency.get_Cryptocurrency()
                        bye = price_BYN / price_BTC

                        await callback.message.edit_text(text="💳 Купить криптовалюту: BTC за BYN\n"
                                                              f"1 Bitcoin = {price_BTC}\n\n"
                                                              f"{price_BYN} BYN = {bye} BTC",
                                                         reply_markup=await MainForm.bue_ikb(
                                                             user_id=callback.from_user.id,
                                                             count=bye,
                                                             target="BuyBTC")
                                                         )

                elif data.get("target") == "Buy":
                    bye = float(data.get("id"))
                    await callback.message.edit_text(text="Введите ваш кошелек, что бы купить\n"
                                                          f"{bye} BTC",
                                                     reply_markup=await MainForm.back_ikb(
                                                         user_id=callback.from_user.id,
                                                         target="BuyBTC")
                                                     )
                    await MainState.Wallet.set()

        if message:
            await message.delete()

            try:
                await bot.delete_message(
                    chat_id=message.from_user.id,
                    message_id=message.message_id - 1
                )
            except BadRequest:
                pass

            if state:
                if await state.get_state() == "MainState:Wallet":
                    await message.answer(text=f"Вы ввели кошелек {message.text}",
                                         reply_markup=await MainForm.back_ikb(user_id=message.from_user.id,
                                                                              target="Buy")
                                         )
