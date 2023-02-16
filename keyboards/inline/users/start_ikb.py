from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import BadRequest

from config import CONFIG
from crud import CRUDUsers
from handlers.users.Cryptocurrency import Cryptocurrency
from loader import bot
from states.users.MainState import MainState

main_cb = CallbackData("main", "target", "action", "id", "editId")


class MainForm:
    @staticmethod
    async def back_ikb(user_id: int, target: str) -> InlineKeyboardMarkup:
        """
        Общая клавиатура для перехода на один шаг назад
        :param user_id: id пользователя
        :param target: Параметр что бы указать куда переходить назад
        :return:
        """
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="◀️ Назад", callback_data=main_cb.new(target, 0, 0, user_id))
                ]
            ]
        )

    @staticmethod
    async def proof_ikb() -> InlineKeyboardMarkup:
        """
        Клавиатура для того что бы потвердить пользовательское соглашение когда заходит в самый первый раз
        :return:
        """
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="ПОДТВЕРДИТЬ 👍🏻", callback_data=main_cb.new("MainForm", 0, 0, 0))
                ]
            ]
        )

    @staticmethod
    async def user_paid_ikb() -> InlineKeyboardMarkup:
        """
        Клавиатура для потверждения оплаты банковским реквизитам
        :return:
        """
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Я ОПЛАТИЛ ✅", callback_data=main_cb.new("UserPaid", 0, 0, 0))
                ]
            ]
        )

    @staticmethod
    async def CheckOut_ikb() -> InlineKeyboardMarkup:
        """
        Клавиатура для того когда пользователь ввел не правильно кошелек, спросить дальнейшие действия
        :return:
        """
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Да 👌", callback_data=main_cb.new("Buy", 0, 0, 0)),
                    InlineKeyboardButton(text="Нет 👎", callback_data=main_cb.new("MainForm", 0, 0, 0))
                ]
            ]
        )

    @staticmethod
    async def money_ikb(user_id: int, target: str) -> InlineKeyboardMarkup:
        """
        Клавиатура при покупке валюты
        :param user_id: id пользователя
        :param target: Параметр что бы указать куда переходить назад
        :return:
        """
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
                    InlineKeyboardButton(text="✍️ Ввести сумму", callback_data=main_cb.new("Pay",
                                                                                           "EnterAmount", 0, user_id))
                ],
                [
                    InlineKeyboardButton(text="◀️ Назад", callback_data=main_cb.new(target, 0, 0, user_id))
                ]
            ]
        )

    @staticmethod
    async def bue_ikb(user_id: int, target: str, count: float) -> InlineKeyboardMarkup:
        """
        Клавиатура для потверждения действия при покупке
        :param user_id: id пользователя
        :param target: Параметр что бы указать куда переходить назад
        :param count: Сколько монет хочет купить пользователь
        :return:
        """
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Купить ✅", callback_data=main_cb.new("Buy", 0, count, user_id))
                ],
                [
                    InlineKeyboardButton(text="◀️ Назад", callback_data=main_cb.new(target, 0, 0, user_id))
                ]
            ]
        )

    @staticmethod
    async def wallet_ikb(user_id: int, target: str) -> InlineKeyboardMarkup:
        """
        Клавиатура для ввода BTC кошелька
        :param user_id: id пользователя
        :param target: Параметр что бы указать куда переходить назад
        :return:
        """
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
        """
        Клавиатура главного меню
        :param user_id: id пользователя
        :return:
        """
        data = {"💳 Купить BTC": {"target": "BuyBTC", "action": "get_BuyBTC", "id": 0, "editid": user_id},
                "💳 Продать BTC": {"target": "SellBTC", "action": "get_SellBTC", "id": 0, "editid": user_id},
                "💻 Профиль": {"target": "Profile", "action": "get_Profile", "id": 0, "editid": user_id},
                }
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=name, callback_data=main_cb.new(name_items["target"],
                                                                              name_items["action"],
                                                                              name_items["id"],
                                                                              name_items["editid"]))
                ] for name, name_items in data.items()
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

                elif data.get("target") == "Profile":
                    user = await CRUDUsers.get(user_id=callback.from_user.id)
                    text = f"Профиль\n\n" \
                           f"Регитрация в боте - {user.date_created.strftime('%Y.%m.%d')}\n" \
                           f"Совершено сделок - {user.transactions}"
                    await callback.message.edit_text(text=text,
                                                     reply_markup=await MainForm.back_ikb(user_id=callback.from_user.id,
                                                                                          target="MainForm")
                                                     )

                elif data.get("target") == "BuyBTC":
                    price = await Cryptocurrency.get_Cryptocurrency()

                    text = "💳 Купить криптовалюту: BTC за BYN\n"\
                           f"1 Bitcoin = {price} BYN\n\n"\
                           f"<i>Мин. сумма: 50.0 BYN</i>"

                    await callback.message.edit_text(text=text,
                                                     reply_markup=await MainForm.money_ikb(
                                                         user_id=callback.from_user.id,
                                                         target="MainForm"),
                                                     parse_mode="HTML"
                                                     )

                elif data.get("target") == "Pay":
                    if data.get("action") == "get_pay":
                        price_BYN = int(data.get("id"))
                        price_BTC = await Cryptocurrency.get_Cryptocurrency()
                        bye = round(price_BYN / price_BTC, 8)

                        text = "💳 Купить криптовалюту: BTC за BYN\n"\
                               f"1 Bitcoin = {price_BTC}\n\n" \
                               f"📢 Внимание!\n" \
                               f"Текущая цена покупки зафиксирована!\n" \
                               f"Нажав кнопку Купить ✅ " \
                               f"необходимо оплатить счет в течении ⏱60 минут!\n\n"\
                               f"{price_BYN} BYN = {bye} BTC"

                        await callback.message.edit_text(text=text,
                                                         reply_markup=await MainForm.bue_ikb(
                                                             user_id=callback.from_user.id,
                                                             count=bye,
                                                             target="BuyBTC")
                                                         )

                    elif data.get("action") == "EnterAmount":
                        await callback.message.edit_text(text="Введите сумму в BYN:",
                                                         reply_markup=await MainForm.back_ikb(
                                                             user_id=callback.from_user.id,
                                                             target="BuyBTC")
                                                         )
                        await MainState.UserCoin.set()

                elif data.get("target") == "Buy":
                    bye = float(data.get("id"))
                    await callback.message.edit_text(text="🔐 Введите ваш адрес Bitcoin - кошелька 🔐:\n\n"
                                                          f"Покупка - {bye} BTC",
                                                     reply_markup=await MainForm.back_ikb(
                                                         user_id=callback.from_user.id,
                                                         target="BuyBTC")
                                                     )
                    await MainState.Wallet.set()

                elif data.get("target") == "UserPaid":
                    await callback.message.edit_text(text="📸 Загрузите изображение подтверждающее оплату!\n"
                                                          "(до 2 Мб)")
                    await MainState.UserPhoto.set()

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
                    wallet = await Cryptocurrency.Check_Wallet(btc_address=message.text)
                    if wallet:
                        text = "🧾РЕКВИЗИТЫ ДЛЯ ОПЛАТЫ\n" \
                               "        🏧💳💵\n" \
                               "- СИСТЕМА ЕРИП ПЛАТЕЖИ\n" \
                               "1. ЕРИП\n" \
                               "2. БАНКОВСКИЕ ФИНАНСОВЫЕ \n" \
                               "УСЛУГИ\n" \
                               "3. БАНК НКФО\n" \
                               "4. МТБАНК\n" \
                               "5. ПОПОЛНЕНИЕ ДЕБЕТОВОЙ КАРТЫ\n" \
                               "6. Р/СЧЁТ       32271867\n" \
                               "7. ПОСЛЕ ПЕРЕВОДА СРЕДСТВ \n" \
                               "НАЖИМАЕМ КНОПКУ \n" \
                               "🏧🏧🏧Я Оплатил 🏧🏧🏧\n" \
                               "8. ПРИСЫЛАЕМ ЧЕК \n" \
                               "9. 🧾🧾  ЧЕК ОБЯЗАТЕЛЕН 🧾🧾\n"

                        await message.answer(text=f"Вы ввели кошелек <i>{message.text}</i>\n\n"
                                                  f"{text}",
                                             reply_markup=await MainForm.user_paid_ikb(),
                                             parse_mode="HTML"
                                             )
                    else:
                        await message.answer(text=f"Адрес кошелька <i>{message.text}</i> нету в blockchain\n\n"
                                                  f"Желаете еще раз ввести ваш адрес Bitcoin - кошелька",
                                             reply_markup=await MainForm.CheckOut_ikb(),
                                             parse_mode="HTML"
                                             )

                elif await state.get_state() == "MainState:UserPhoto":
                    if message.content_type == "photo":
                        if message.photo[0].file_size > 2000:
                            await message.answer(text="Картинка превышает 2 мб\n"
                                                      "Попробуйте загрузить еще раз")
                            await MainState.UserPhoto.set()
                        else:
                            photo = message.photo[0].file_id
                            for admin in CONFIG.BOT.ADMINS:
                                await bot.send_photo(chat_id=admin, photo=photo,
                                                     caption="Пользователь оплатил!")

                            await message.answer(text="Ваша заявка уже обрабатывается как только она будет "
                                                      "выполнена мы вам сообщим.\n\n"
                                                      "Спасибо что выбрали нас 🤗✌️\n\n"
                                                      "🚀 Желаем Вам отличного настроения!")
                            await state.finish()
                    else:
                        await message.answer(text="Загрузите картинку")
                        await MainState.UserPhoto.set()

                elif await state.get_state() == "MainState:UserCoin":
                    money = message.text.isdigit()
                    if money:
                        user_money = int(message.text)
                        if user_money < 50:
                            await message.answer(text="Минимальная сумма 50 BYN\n"
                                                      "Введите сумму в BYN")
                            await MainState.UserCoin.set()
                        else:
                            price_BTC = await Cryptocurrency.get_Cryptocurrency()
                            bye = round(int(user_money) / price_BTC, 8)
                            text = "💳 Купить криптовалюту: BTC за BYN\n" \
                                   f"1 Bitcoin = {price_BTC}\n\n" \
                                   f"📢 Внимание!\n" \
                                   f"Текущая цена покупки зафиксирована!\n" \
                                   f"Нажав кнопку Купить ✅ " \
                                   f"необходимо оплатить счет в течении ⏱60 минут!\n\n" \
                                   f"{user_money} BYN = {bye} BTC"

                            await message.answer(text=text,
                                                 reply_markup=await MainForm.bue_ikb(
                                                     user_id=message.from_user.id,
                                                     count=bye,
                                                     target="BuyBTC")
                                                 )
                    else:
                        await message.answer(text="Вы ввели некорректные данные\n"
                                                  "Доступен ввод только цифр")
                        await MainState.UserCoin.set()
