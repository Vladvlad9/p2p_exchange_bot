import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from aiogram.utils.exceptions import BadRequest
from loguru import logger

from config import CONFIG
from config.config import CONFIGTEXT
from crud import CRUDUsers, CRUDTransaction, CRUDCurrency
from crud.referralCRUD import CRUDReferral
from crud.verificationCRUD import CRUDVerification
from crud.walCRUD import CRUDWallet
from handlers.users.AllCallbacks import money_cb, main_cb
from handlers.users.CreateWallet import CreateWallet
from handlers.users.Cryptocurrency import Cryptocurrency
from loader import bot
from schemas import TransactionSchema, WalletSchema, VerificationSchema
from states.users.MainState import MainState

from decimal import Decimal
logger.add("debug.log", format="{time} {level} {message}", level="DEBUG", serialize=True)


class MainForm:

    @staticmethod
    async def send_timer_message(chat_id: int, state):
        await state.finish()
        await bot.send_message(chat_id=chat_id,
                               text='Время вышло!\n'
                                    f'{CONFIGTEXT.MAIN_FORM.TEXT}',
                               reply_markup=await MainForm.start_ikb(chat_id))

    @staticmethod
    async def confirmation_timer(message):
        await asyncio.sleep(10)
        await message.answer(text="Ваша заявка уже обрабатывается как только она будет "
                                  "выполнена мы вам сообщим.\n\n"
                                  "Если вам не сообщили в течение 15 мин. Обратитесь к оператору. "
                                  "Он быстро все решит.\n\n"
                                  "Спасибо что выбрали нас 🤗✌️\n\n"
                                  "🚀 Желаем Вам отличного настроения!")

    @staticmethod
    async def isfloat(value: str):
        try:
            float(value)
            return True
        except ValueError:
            return False

    @staticmethod
    async def buying_currency(money: int, currency: str, limit: int, message: types.Message, state):
        """
        Функция которая предоставляет проверку покупки валюты BYN или RUB
        :param money: ввод пользователем колличество денег
        :param currency: валюта BYN или RUB
        :param limit: минимальная кол-во денег для ввода
        :param message: message: Message
        :param state: state: FSMContext
        :return:
        """

        user_money = int(money)
        if user_money < limit:
            await message.answer(text=f"Минимальная сумма {limit} {currency}\n"
                                      f"Введите сумму в {currency}")
            await MainState.UserCoin.set()
        else:
            price_BTC = await Cryptocurrency.get_update_currency(currency)
            bye = round(int(user_money) / price_BTC, 8)

            currency = await CRUDCurrency.get(currency_name=currency)

            percent = round((Decimal(bye) / Decimal(100) * Decimal(CONFIG.COMMISSION.COMMISSION_BOT)), 8)
            percent_referral = round((Decimal(bye) / Decimal(100) * Decimal(CONFIG.COMMISSION.COMMISSION_REFERRAL)), 8)

            get_referral = await CRUDReferral.get(referral_id=message.from_user.id)

            if get_referral:
                current_bye = round(Decimal(bye) - Decimal(percent) - Decimal(percent_referral), 8)
                #f"{CONFIG.COMMISSION.COMMISSION_REFERRAL}% от {bye} составит = {percent_referral} BTC\n"
                referral_txt = f"➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                               f"Вы получите BTC: {current_bye}\n" \
                               f"➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                               f"ПЕРЕЙТИ К ОПЛАТЕ?"
            else:
                current_bye = round(Decimal(bye) - Decimal(percent), 8)
                referral_txt = f"➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                               f"Вы получите BTC: {current_bye}\n" \
                               f"➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                               f"ПЕРЕЙТИ К ОПЛАТЕ?"
            # f"{CONFIG.COMMISSION.COMMISSION_BOT}% от {bye} составит = {percent} BTC\n"
            text = f"💳 Купить криптовалюту: BTC за {currency.name}\n" \
                   f"1 Bitcoin = {round(price_BTC)} {currency.name}\n\n" \
                   f"📢 Внимание!\n" \
                   f"Текущая цена покупки зафиксирована!\n" \
                   f"Нажав кнопку Купить ✅ " \
                   f"необходимо оплатить счет в течении ⏱{CONFIG.PAYMENT_TIMER / 60} минут!\n\n" \
                   f"Вы должны заплатить {user_money} {currency.name}\n" \
                   f"{referral_txt}\n" \

            await message.answer(text=text,
                                 reply_markup=await MainForm.bue_ikb(
                                     user_id=message.from_user.id,
                                     count=bye,
                                     target="MainForm")
                                 )

            await state.update_data(currency_id=currency.id)
            await state.update_data(sale=user_money)
            await state.update_data(exchange_rate=price_BTC)
            await state.update_data(buy_BTC=current_bye)
            await state.update_data(percent=percent)

            await asyncio.sleep(int(CONFIG.PAYMENT_TIMER))
            await MainForm.send_timer_message(chat_id=message.from_user.id, state=state)

    @staticmethod
    async def buying_BTC(user_money, message, state):
        price_BYN = await Cryptocurrency.get_byn()
        #price_RUB = await Cryptocurrency.get_rub()
        price_RUB = await Cryptocurrency.get_CryptocurrencyBTC(currency="RUB")
        if price_RUB is None:
            count = 0
            while price_RUB is None:
                if count == 10:
                    break
                else:
                    count += 1
                    price_RUB = await Cryptocurrency.get_CryptocurrencyBTC(currency="RUB")

        price_BTC = await Cryptocurrency.get_Cryptocurrency(currency="USD")
        if price_BTC is None:
            count = 0
            while price_BTC is None:
                if count == 10:  # Что бы не войти в бесконечный цикл
                    break
                else:
                    count += 1
                    price_BTC = await Cryptocurrency.get_Cryptocurrency("USD")

        bye_byn = round(Decimal(user_money) * Decimal(price_BTC) * Decimal(price_BYN), 2)
        #bye_rub = round(Decimal(user_money) * Decimal(price_BTC) * Decimal(price_RUB), 2)
        bye_rub = round(Decimal(price_RUB) * Decimal(user_money), 2)
        text = f"📈 Текущая цена Bitcoin: {round(price_BTC)}$\n" \
               f"📢 Внимание! Текущая цена покупки зафиксирована!\n" \
               f"Нажав кнопку ОПЛАТИТЬ✅ необходимо " \
               f"оплатить счет в течении ⏱{CONFIG.PAYMENT_TIMER / 60} минут!\n\n" \
               f"🧾 Сумма к оплате: 🇧🇾 {bye_byn} BYN\n\n" \
               f"🧾 Сумма к оплате: 🇷🇺 {bye_rub} RUB\n\n" \
               f"➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
               f"Вы получите BTC: {user_money}\n" \
               f"➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
               f"ПЕРЕЙТИ К ОПЛАТЕ?"

        #await state.update_data(exchange_RUB=float(Decimal(price_BTC) * Decimal(price_RUB)))
        await state.update_data(exchange_RUB=float(price_RUB))
        await state.update_data(exchange_BYN=float(Decimal(price_BTC) * Decimal(price_BYN)))

        await state.update_data(price_RUB=bye_rub)
        await state.update_data(price_BYN=bye_byn)

        await state.update_data(buy_BTC=user_money)

        await message.answer(text=text,
                             reply_markup=await MainForm.currency_ikb(
                                 user_id=message.from_user.id,
                                 target="MainForm",
                                 actionBack="get_MainForm")
                             )

    @staticmethod
    async def next_ikb() -> InlineKeyboardMarkup:
        """
        Клавиатура необходима, что бы пользователь запомнил секретную фразу и перешел к завершению создании кошелька
        :return:
        """
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Продолжить ➡️", callback_data=main_cb.new("Profile", "get_NextWallet",
                                                                                         0, 0)
                                         )
                ]
            ]
        )

    @staticmethod
    async def back_ikb(user_id: int, target: str, page: int = 0, action: str = None) -> InlineKeyboardMarkup:
        """
        Общая клавиатура для перехода на один шаг назад
        :param page: Необходим для того когда переходит пользователь назад в профиле на определенную страницу
        :param action: Не обязательный параметр, он необходим если в callback_data есть подзапрос для вкладки
        :param user_id: id пользователя
        :param target: Параметр что бы указать куда переходить назад
        :return:
        """
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="◀️ Назад", callback_data=main_cb.new(target, action, page, user_id))
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
                    InlineKeyboardButton(text="ПОДТВЕРДИТЬ 👍🏻",
                                         callback_data=main_cb.new("Profile", "get_NextWallet", 0, 0))
                ]
            ]
        )

    @staticmethod
    async def continue_ikb() -> InlineKeyboardMarkup:
        """
        Клавиатура для того что бы потвердить пользовательское соглашение когда заходит в самый первый раз
        :return:
        """
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Продолжить ➡️",
                                         callback_data=main_cb.new("Profile", "get_continue", 0, 0))
                ],
                [
                    InlineKeyboardButton(text="⬅️ Назад",
                                         callback_data=main_cb.new("Profile", "get_Profile", 0, 0))
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
                ],
                [
                    InlineKeyboardButton(text="◀️ Назад", callback_data=main_cb.new("MainForm", "get_MainForm", 0, 0))
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
    async def CheckOut_wallet_ikb() -> InlineKeyboardMarkup:
        """
        Клавиатура для того когда пользователь ввел не правильно кошелек, спросить дальнейшие действия
        :return:
        """
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Верно 👌", callback_data=main_cb.new("Buy", "get_requisites", 0, 0)),
                    InlineKeyboardButton(text="Нет ⛔️", callback_data=main_cb.new("MainForm", "get_MainForm", 0, 0))
                ]
            ]
        )

    @staticmethod
    async def get_currency_ikb(user_id: int, target: str) -> InlineKeyboardMarkup:
        """
        Клавиатура при покупке валюты
        :param user_id: id пользователя
        :param target: Параметр что бы указать куда переходить назад
        :return:
        """
        return InlineKeyboardMarkup(
            inline_keyboard=[
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
    async def currency_ikb(user_id: int, target: str, actionBack: str) -> InlineKeyboardMarkup:
        """
                Клавиатура при покупке валюты
                :param user_id: id пользователя
                :param target: Параметр что бы указать куда переходить назад
                :return:
                """
        data = {
            "ОПЛАТИТЬ BYN 🇧🇾": {"target": "Buy", "action": "SelectUserWallet", "id": "BYN", "editid": user_id},
            "ОПЛАТИТЬ RUB 🇷🇺": {"target": "Buy", "action": "SelectUserWallet", "id": "RUB", "editid": user_id},
        }
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=name, callback_data=main_cb.new(name_items["target"],
                                                                              name_items["action"],
                                                                              name_items["id"],
                                                                              name_items["editid"]))
                    for name, name_items in data.items()
                ],
                [
                    InlineKeyboardButton(text="◀️ Назад", callback_data=main_cb.new(target, actionBack, 0, user_id))
                ]
            ]
        )

    @staticmethod
    async def money_entry_ikb(user_id: int, target: str, currency: str) -> InlineKeyboardMarkup:
        """
                Клавиатура при покупке валюты
                :param currency:
                :param user_id: id пользователя
                :param target: Параметр что бы указать куда переходить назад
                :return:
                """
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="✍️ Ввести сумму", callback_data=main_cb.new("Pay",
                                                                                           "EnterAmount", currency,
                                                                                           user_id)
                                         )
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
                    InlineKeyboardButton(text="Купить ✅", callback_data=main_cb.new("Buy", "SelectUserWalletBTC", count, user_id))
                ],
                [
                    InlineKeyboardButton(text="◀️ Назад", callback_data=main_cb.new(target, "get_MainForm", 0, user_id))
                ]
            ]
        )

    @staticmethod
    async def wallet_ikb(user_id: int, target: str, action: str) -> InlineKeyboardMarkup:
        """
        Клавиатура для ввода BTC кошелька
        :param user_id: id пользователя
        :param target: Параметр что бы указать куда переходить назад
        :return:
        """
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Использовать внутрений кошелек",
                                         callback_data=main_cb.new("Buy",
                                                                   action, 0, user_id))
                ],
                [
                    InlineKeyboardButton(text="◀️ Назад", callback_data=main_cb.new(target, 0, 0, user_id))
                ]
            ]
        )

    @staticmethod
    async def wallet_user_ikb(user_id: int,
                              target: str, action_back: str, wallet_exists: bool) -> InlineKeyboardMarkup:
        """
        Клавиатура для ввода BTC кошелька
        :param target:
        :param wallet_exists: Проверка на существование кошелька, если есть выводить клавиатуру только с кнопкой назад,
        если не существует тогда выводить клавиатуру с кнопкой создать
        :param action_back: Параметр что бы указать куда переходить назад
        :param user_id: id пользователя
        :return:
        """

        data = {
            "➕ Создать": {"target": "Profile", "action": "get_createWallet", "id": 0, "editid": user_id},
            "◀️ Назад": {"target": target, "action": action_back, "id": 0, "editid": user_id},
        }
        user = await CRUDUsers.get(user_id=user_id)
        verification = await CRUDVerification.get(user_id=user.id)
        if verification:
            confirm = 1 if verification.confirm else 0
        else:
            confirm = 0

        if wallet_exists:
            return InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="📤 Вывести",
                                             callback_data=main_cb.new("Profile", "money_transfer", confirm, user_id)
                                             ),
                        InlineKeyboardButton(text="📥 Пополнить",
                                             callback_data=main_cb.new("Profile", "money_reload", confirm, user_id)
                                             )
                    ],
                    [
                        InlineKeyboardButton(text="◀️ Назад", callback_data=main_cb.new(target, action_back,
                                                                                        0, user_id)
                                             )
                    ]
                ]
            )
        else:
            return InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text=name, callback_data=main_cb.new(name_items["target_back"],
                                                                              name_items["action"],
                                                                              name_items["id"],
                                                                              name_items["editid"])
                                             )
                    ] for name, name_items in data.items()
                ]
            )

    @staticmethod
    async def start_ikb(user_id: int) -> InlineKeyboardMarkup:
        """
        Клавиатура главного меню
        :param user_id: id пользователя
        :return:
        """
        data = {
            "BYN 🇧🇾": {"target": "Pay", "action": "EnterAmount", "id": "BYN", "editid": user_id},
            "RUB 🇷🇺": {"target": "Pay", "action": "EnterAmount", "id": "RUB", "editid": user_id},
            "BTC ₿": {"target": "Pay", "action": "get_SellBTC", "id": 0, "editid": user_id},
        }

        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="💻 Профиль",
                                         callback_data=main_cb.new("Profile", "get_Profile", 0, user_id))
                ]
            ] + [
                [
                    InlineKeyboardButton(text=name, callback_data=main_cb.new(name_items["target"],
                                                                              name_items["action"],
                                                                              name_items["id"],
                                                                              name_items["editid"]))
                    for name, name_items in data.items()
                ]
            ]
        )

    @staticmethod
    async def profile_ikb(user_id: int, target: str) -> InlineKeyboardMarkup:
        """
        Клавиатура профиля
        :param user_id: id пользователя
        :param target: Параметр что бы указать куда переходить назад
        :return:
        """
        user = await CRUDUsers.get(user_id=user_id)
        verification = await CRUDVerification.get(user_id=user.id)

        data = {"🤝 Сделки": {"target": "Profile", "action": "get_transaction", "id": 0, "editid": user_id},
                "👨‍👦‍👦 Рефералы": {"target": "Profile", "action": "get_referrals", "id": 0, "editid": user_id},
                "👛 Кошелек": {"target": "Profile", "action": "get_userWallet", "id": 0, "editid": user_id},
                "◀️ Назад": {"target": target, "action": "get_MainForm", "id": 0, "editid": user_id}
                }
        if verification is None:
            data = {"🤝 Сделки": {"target": "Profile", "action": "get_transaction", "id": 0, "editid": user_id},
                    "✅ Верификация": {"target": "Profile", "action": "get_verification", "id": 0, "editid": user_id},
                    "👨‍👦‍👦 Рефералы": {"target": "Profile", "action": "get_referrals", "id": 0, "editid": user_id},
                    "👛 Кошелек": {"target": "Profile", "action": "get_userWallet", "id": 0, "editid": user_id},
                    "◀️ Назад": {"target": target, "action": "get_MainForm", "id": 0, "editid": user_id}
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
    async def pagination_transaction_ikb(target: str,
                                         user_id: int,
                                         action: str = None,
                                         page: int = 0) -> InlineKeyboardMarkup:
        """
        Клавиатура пагинации проведенных операций пользователя
        :param target:  Параметр что бы указать куда переходить назад
        :param user_id: id пользователя
        :param action: Не обязательный параметр, он необходим если в callback_data есть подзапрос для вкладки
        :param page: текущая страница пагинации
        :return:
        """
        orders = await CRUDTransaction.get_all(user_id=user_id)

        orders_count = len(orders)

        prev_page: int
        next_page: int

        if page == 0:
            prev_page = orders_count - 1
            next_page = page + 1
        elif page == orders_count - 1:
            prev_page = page - 1
            next_page = 0
        else:
            prev_page = page - 1
            next_page = page + 1

        back_ikb = InlineKeyboardButton("◀️ Назад", callback_data=main_cb.new("Profile", "get_Profile", 0, 0))
        prev_page_ikb = InlineKeyboardButton("←", callback_data=main_cb.new(target, action, prev_page, 0))
        check = InlineKeyboardButton("🧾 Чек", callback_data=main_cb.new("Profile", "get_check", page, 0))
        page = InlineKeyboardButton(f"{str(page + 1)}/{str(orders_count)}",
                                    callback_data=main_cb.new("", "", 0, 0))
        next_page_ikb = InlineKeyboardButton("→", callback_data=main_cb.new(target, action, next_page, 0))

        if orders_count == 1:
            return InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        check
                    ],
                    [
                        back_ikb
                    ]
                ]
            )
        else:
            return InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        prev_page_ikb,
                        page, check,
                        next_page_ikb,
                    ],
                    [
                        back_ikb
                    ]
                ]
            )

    @staticmethod
    async def money_transfer_ikb(user_id: int) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Отпраить",
                                         callback_data=main_cb.new("Profile", "approved_trans_money", user_id, 0)),
                    InlineKeyboardButton(text="◀️ Назад",
                                         callback_data=main_cb.new("Profile", "get_userWallet", user_id, 0))
                ]
            ]
        )

    @staticmethod
    @logger.catch
    async def process_profile(callback: CallbackQuery = None, message: Message = None,
                              state: FSMContext = None) -> None:

        if callback:
            if callback.data.startswith('main'):
                data = main_cb.parse(callback_data=callback.data)
                # Главное меню
                if data.get("target") == "MainForm":
                    if data.get("action") == "get_MainForm":
                        await state.finish()
                        await callback.message.delete()
                        await callback.message.answer(text=CONFIGTEXT.MAIN_FORM.TEXT,
                                                      reply_markup=await MainForm.start_ikb(
                                                          user_id=callback.from_user.id)
                                                      )

                # Профиль
                elif data.get("target") == "Profile":
                    if data.get("action") == "get_Profile":
                        user = await CRUDUsers.get(user_id=callback.from_user.id)
                        transaction = await CRUDTransaction.get_all(user_id=user.id)
                        verification = await CRUDVerification.get(user_id=user.id)
                        if verification:
                            get_verification = "верифицированный ✅" if verification.confirm \
                                else "не верифицированный ❌\n" \
                                     "<i>ожидайте потверждения</i>"
                        else:
                            get_verification = "не верифицированный ❌"

                        text = f"Профиль {get_verification}\n\n" \
                               f"Регитрация в боте - {user.date_created.strftime('%Y.%m.%d')}\n" \
                               f"Количество сделок - {len(transaction)}\n\n" \
                               f"Реферальная ссылка: \n" \
                               f"<code>{CONFIG.BOT.BOT_LINK}?start={callback.from_user.id}</code>"
                        await callback.message.delete()
                        await callback.message.answer(text=text,
                                                      reply_markup=await MainForm.profile_ikb(
                                                          user_id=callback.from_user.id,
                                                          target="MainForm"),
                                                      parse_mode="HTML"
                                                      )

                    elif data.get('action') == "get_verification":
                        await callback.message.edit_text(text="Что бы пройти верификацию не обходимо загрузить две "
                                                              "фотографии",
                                                         reply_markup=await MainForm.continue_ikb())

                    elif data.get('action') == "get_continue":
                        await callback.message.edit_text(text="Загрузите фото последней страницы паспорта")
                        await MainState.VerificationPhotoOne.set()

                    elif data.get("action") == "get_transaction":
                        user = await CRUDUsers.get(user_id=callback.from_user.id)
                        transaction = await CRUDTransaction.get_all(user_id=user.id)

                        if transaction:
                            currency = await CRUDCurrency.get(currency_id=transaction[0].currency_id)
                            approved = "✅ одобрена ✅" if transaction[0].approved else "❌ не одобрена ❌"

                            text = f"🤝 Сделка № {transaction[0].id} {approved}\n\n" \
                                   f"📈 Курс покупки: <i>{transaction[0].exchange_rate}\n</i>" \
                                   f"   ₿  Куплено BTC: <i>{transaction[0].buy_BTC}\n</i>" \
                                   f"💸 Продано {currency.name}: <i>{transaction[0].sale}\n</i>" \
                                   f"👛 Кошелек <i>{transaction[0].wallet}</i>"
                            try:
                                await callback.message.edit_text(text=f"<i>Мои сделки</i>\n\n"
                                                                      f"{text}",
                                                                 reply_markup=await MainForm.pagination_transaction_ikb(
                                                                     user_id=user.id,
                                                                     target="Profile",
                                                                     action="pagination_transaction"),
                                                                 parse_mode="HTML"
                                                                 )
                            except BadRequest:
                                await callback.message.delete()
                                await callback.message.answer(text=f"<i>Мои сделки</i>\n\n"
                                                                   f"{text}",
                                                              reply_markup=await MainForm.pagination_transaction_ikb(
                                                                  user_id=user.id,
                                                                  target="Profile",
                                                                  action="pagination_transaction"),
                                                              parse_mode="HTML"
                                                              )

                        else:
                            await callback.message.edit_text(text="Вы не совершали сделок 😞",
                                                             reply_markup=await MainForm.back_ikb(
                                                                 user_id=callback.from_user.id,
                                                                 target="Profile",
                                                                 action="get_Profile")
                                                             )

                    elif data.get("action") == "pagination_transaction":
                        page = int(data.get('id'))

                        user = await CRUDUsers.get(user_id=callback.from_user.id)
                        transaction = await CRUDTransaction.get_all(user_id=user.id)

                        if transaction:
                            currency = await CRUDCurrency.get(currency_id=transaction[page].currency_id)
                            approved = "✅ подтверждена ✅" if transaction[page].approved else "❌ не подтверждена ❌"

                            text = f"🤝 Сделка № {transaction[page].id} {approved}\n\n" \
                                   f"📈 Курс покупки: <i>{transaction[page].exchange_rate}\n</i>" \
                                   f"   ₿  Куплено BTC: <i>{transaction[page].buy_BTC}\n</i>" \
                                   f"💸 Продано {currency.name}: <i>{transaction[page].sale}\n</i>" \
                                   f"👛 Кошелек <i>{transaction[page].wallet}</i>"
                            try:
                                await callback.message.edit_text(text=f"<i>Мои сделки</i>\n\n"
                                                                      f"{text}",
                                                                 reply_markup=await MainForm.pagination_transaction_ikb(
                                                                     user_id=user.id,
                                                                     page=page,
                                                                     target="Profile",
                                                                     action="pagination_transaction"),
                                                                 parse_mode="HTML"
                                                                 )
                            except BadRequest:
                                await callback.message.delete()
                                await callback.message.answer(text=f"<i>Мои сделки</i>\n\n"
                                                                   f"{text}",
                                                              reply_markup=await MainForm.pagination_transaction_ikb(
                                                                  user_id=user.id,
                                                                  page=page,
                                                                  target="Profile",
                                                                  action="pagination_transaction"),
                                                              parse_mode="HTML"
                                                              )
                        else:
                            await callback.message.edit_text(text="Вы не совершали сделок 😞",
                                                             reply_markup=await MainForm.back_ikb(
                                                                 user_id=callback.from_user.id,
                                                                 target="Profile",
                                                                 action="get_Profile")
                                                             )

                    elif data.get('action') == 'get_check':
                        try:
                            check = int(data.get('id'))

                            user = await CRUDUsers.get(user_id=callback.from_user.id)
                            transaction = await CRUDTransaction.get_all(user_id=user.id)

                            if transaction[check].check != "None":
                                page = int(data.get("id"))
                                photo = open(f'user_check/{transaction[page].check}.jpg', 'rb')
                                await callback.message.delete()
                                await bot.send_photo(chat_id=callback.from_user.id, photo=photo,
                                                     caption=f"Фото чека",
                                                     reply_markup=await MainForm.back_ikb(user_id=callback.from_user.id,
                                                                                          target="Profile",
                                                                                          action="pagination_transaction",
                                                                                          page=check)
                                                     )
                            else:
                                await callback.answer(text="Фото чека не добавлено")
                        except Exception as e:
                            print(e)

                    elif data.get("action") == "get_referrals":
                        user = await CRUDUsers.get(user_id=callback.from_user.id)
                        referrals = await CRUDReferral.get_all(user_id=user.id)

                        text = f"Количество зарегистрированных рефералов по вашей ссылке : {len(referrals)}"
                        await callback.message.edit_text(text=text,
                                                         reply_markup=await MainForm.back_ikb(
                                                             user_id=callback.from_user.id,
                                                             target="Profile",
                                                             page=0,
                                                             action="get_Profile")
                                                         )

                    elif data.get("action") == "get_userWallet":
                        await state.finish()
                        user = await CRUDUsers.get(user_id=callback.from_user.id)
                        wallet = await CRUDWallet.get(user_id=user.id)
                        #await CreateWallet.new_wallet()

                        if wallet:
                            qr_code = f"https://chart.googleapis.com/chart?chs=250x250&cht=qr&chl={wallet.address}"
                            await callback.message.delete()
                            balance = await CreateWallet.get_balance(wallet=wallet.address)
                            await bot.send_photo(photo=qr_code,
                                                 chat_id=callback.from_user.id,
                                                 caption=f"Ваш адрес кошелька\n"
                                                         f"<code>{wallet.address}</code>\n"
                                                         f"Баланс : "
                                                         f"{float(balance)} BTC",
                                                 reply_markup=await MainForm.wallet_user_ikb(
                                                     user_id=callback.from_user.id,
                                                     target="Profile",
                                                     action_back="get_Profile",
                                                     wallet_exists=True),
                                                 parse_mode="HTML"
                                                 )
                        else:
                            await callback.message.edit_text(text="У вас нету кошелька",
                                                             reply_markup=await MainForm.wallet_user_ikb(
                                                                 user_id=callback.from_user.id,
                                                                 target="Profile",
                                                                 action_back="get_Profile",
                                                                 wallet_exists=False)
                                                             )

                    elif data.get("action") == "get_createWallet":
                        get_wallet = await CreateWallet.create_wallet()
                        if get_wallet:
                            address = str(get_wallet['wallet']['address'])
                            passphrase = str(get_wallet['wallet']['passphrase'])
                            user = await CRUDUsers.get(user_id=callback.from_user.id)

                            await CRUDWallet.add(wallet=WalletSchema(user_id=user.id,
                                                                     address=address,
                                                                     passphrase=passphrase)
                                                 )
                            await callback.message.edit_text(text=f"Запомните ваш ключ востановления\n\n"
                                                                  f"{passphrase}",
                                                             reply_markup=await MainForm.next_ikb()
                                                             )
                        else:
                            pass

                    elif data.get("action") == "get_NextWallet":
                        user = await CRUDUsers.get(user_id=callback.from_user.id)
                        wallet = await CRUDWallet.get(user_id=user.id)
                        qr_code = f"https://chart.googleapis.com/chart?chs=250x250&cht=qr&chl={wallet.address}"
                        await callback.message.delete()
                        await bot.send_photo(photo=qr_code,
                                             chat_id=callback.from_user.id,
                                             caption=f"Ваш адрес кошелька\n"
                                                     f"<code>{wallet.address}</code>\n",
                                             reply_markup=await MainForm.wallet_user_ikb(
                                                 user_id=callback.from_user.id,
                                                 target="MainForm",
                                                 action_back="get_MainForm",
                                                 wallet_exists=True),
                                             parse_mode="HTML"
                                             )

                    elif data.get('action') == "money_transfer":
                        data = int(data.get('id'))
                        await callback.message.delete()
                        if data == 0:
                            await callback.message.answer(text="Вывод средст не доступен\n\n"
                                                               "Пройтите верификацию аккаунта",
                                                          reply_markup=await MainForm.profile_ikb(
                                                              user_id=callback.from_user.id,
                                                              target="MainForm"),
                                                          parse_mode="HTML"
                                                          )
                        else:
                            await callback.message.answer(text="Введите адрес кошелька на который хотите переести BTC",
                                                          reply_markup=await MainForm.back_ikb(
                                                              user_id=callback.from_user.id,
                                                              target="Profile",
                                                              action="get_userWallet",
                                                              page=0)
                                                          )

                        await MainState.WalletRecipient.set()

                    elif data.get('action') == "approved_trans_money":
                        data = await state.get_data()
                        user = await CRUDUsers.get(user_id=callback.from_user.id)
                        wallet = await CRUDWallet.get(user_id=user.id)

                        transfer = await CreateWallet.money_transfer(wif_sender=wallet.wif,
                                                                     address_recipient=data["address_recipient"],
                                                                     btc_money=float(data["btc_money"]))
                        await callback.message.edit_text(text="Транзакция успешно проведена\n\n"
                                                              f"{transfer}")
                        await state.finish()

                    elif data.get('action') == 'money_reload':
                        user = await CRUDUsers.get(user_id=callback.from_user.id)
                        wallet = await CRUDWallet.get(user_id=user.id)
                        await callback.message.delete()
                        await callback.message.answer(text='Что бы пополнить кошелек, переведите деньги '
                                                           'на ваш адрес кошелька\n\n'
                                                           f'<code>{wallet.address}</code>',
                                                      parse_mode="HTML",
                                                      reply_markup=await MainForm.back_ikb(
                                                          user_id=callback.from_user.id,
                                                          target="Profile",
                                                          action="get_userWallet"
                                                      ))

                # Меню выбора количесво суммы для покупки BTC
                elif data.get("target") == "BuyBTC":
                    price = await Cryptocurrency.get_Cryptocurrency(currency="USD")

                    text = "Выберите валюту\n"\
                           f"1 Bitcoin ₿ = {price} USD 🇺🇸 " \
                           f"<a href='https://www.coinbase.com/ru/converter/btc/usd'>Coinbase</a>\n\n"\

                    await callback.message.edit_text(text=text,
                                                     reply_markup=await MainForm.currency_ikb(
                                                         user_id=callback.from_user.id,
                                                         target="MainForm",
                                                         actionBack="get_MainForm"),
                                                     parse_mode="HTML",
                                                     disable_web_page_preview=True
                                                     )

                # Меню покупки Валюты
                elif data.get("target") == "Pay":
                    # Покупка BYN or RUB за BTC
                    if data.get("action") == "EnterAmount":
                        currency = data.get("id")
                        currency_txt = "BYN 🇧🇾" if currency == "BYN" else "RUB 🇷🇺"

                        if currency == "BYN":
                            #price = await Cryptocurrency.get_Cryptocurrency(currency="BYN")
                            byn = await Cryptocurrency.get_byn()
                            usd = await Cryptocurrency.get_Cryptocurrency("USD")
                            if usd is None:
                                while usd is None:
                                    usd = await Cryptocurrency.get_Cryptocurrency("USD")

                            price = round(Decimal(byn) * Decimal(usd))
                            text = "Купить BTC за BYN\n" \
                                   f"1 Bitcoin ₿ = {price} BYN 🇧🇾\n\n" \
                                   f"<i>Мин. сумма {CONFIG.COMMISSION.MIN_BYN} BYN</i>"
                        else:
                            #price = await Cryptocurrency.get_Cryptocurrency(currency="RUB")
                            usd = await Cryptocurrency.get_Cryptocurrency("USD")
                            #rub = await Cryptocurrency.get_rub()
                            rub = await Cryptocurrency.get_CryptocurrencyBTC(currency="RUB")
                            if rub is None:
                                while rub is None:
                                    rub = await Cryptocurrency.get_CryptocurrencyBTC(currency="RUB")

                            price = round(Decimal(rub))
                            text = "Купить BTC за RUB\n" \
                                   f"1 Bitcoin ₿ = {price} RUB 🇷🇺\n\n" \
                                   f"<i>Мин. сумма {CONFIG.COMMISSION.MIN_RUB}  RUB</i>"

                        await state.update_data(currency=currency)
                        await callback.message.edit_text(text=f"{text}\n\n"
                                                              f"Введите сумму в {currency_txt}:",
                                                         reply_markup=await MainForm.back_ikb(
                                                             action="get_MainForm",
                                                             user_id=callback.from_user.id,
                                                             target="MainForm"),
                                                         disable_web_page_preview=True
                                                         )
                        await MainState.UserCoin.set()

                    # Выбор валюты для покукик BTC
                    elif data.get('action') == 'get_SellBTC':
                        await callback.message.edit_text(text="Введите сумму в BTC:",
                                                         reply_markup=await MainForm.back_ikb(
                                                             user_id=callback.from_user.id,
                                                             target="MainForm",
                                                             action="get_MainForm")
                                                         )
                        await MainState.ByeBTC.set()

                    # # Покупка BTC за BYN or RUB
                    # elif data.get('action') == "get_Currency":
                    #     currency = data.get("id")
                    #     currency_txt = "BYN 🇧🇾" if currency == "BYN" else "RUB 🇷🇺"
                    #     get_data_buy = await state.get_data()
                    #     if currency == "BYN":
                    #         get_currency = await CRUDCurrency.get(currency_id=1)
                    #         await state.update_data(exchange_rate=get_data_buy['exchange_BYN'])
                    #         await state.update_data(sale=get_data_buy['price_BYN'])
                    #         await state.update_data(currency_id=get_currency.id)
                    #         await state.update_data(currency=get_currency.name)
                    #     else:
                    #         get_currency = await CRUDCurrency.get(currency_id=2)
                    #         await state.update_data(exchange_rate=get_data_buy['exchange_RUB'])
                    #         await state.update_data(sale=get_data_buy['price_RUB'])
                    #         await state.update_data(currency_id=get_currency.id)
                    #         await state.update_data(currency=get_currency.name)
                    #
                    #     data_bye = await state.get_data()
                    #     await callback.message.edit_text(text="🔐 Используйте встроенный 🔐:\n\n"
                    #                                           f"Покупка - {data_bye['buy_BTC']} BTC",
                    #                                      reply_markup=await MainForm.wallet_ikb(
                    #                                          user_id=callback.from_user.id,
                    #                                          target="BuyBTC", action="SelectUserWalletBTC")
                    #                                      )

                # Меню ввода кошелька
                elif data.get("target") == "Buy":
                    if data.get("action") == "get_buy":
                        bye = float(data.get("id"))
                        await callback.message.edit_text(text="🔐 Используйте встроенный 🔐:\n\n"
                                                              f"Покупка - {bye} BTC",
                                                         reply_markup=await MainForm.wallet_ikb(
                                                             user_id=callback.from_user.id,
                                                             target="BuyBTC",
                                                             action="SelectUserWallet")
                                                         )
                        await MainState.Wallet.set()

                    # Если нажата кнопка Повторного ввода кошелька
                    elif data.get("action") == "get_reenter":
                        get_data = await state.get_data()
                        await callback.message.edit_text(text="🔐 Используйте встроенный 🔐\n\n"
                                                              f"Покупка - {get_data['buy_BTC']} BTC",
                                                         reply_markup=await MainForm.back_ikb(
                                                             user_id=callback.from_user.id,
                                                             action="",
                                                             target="BuyBTC")
                                                         )
                        await MainState.Wallet.set()

                    # Нажата кнопка встроенного кошелька
                    elif data.get('action') == "SelectUserWalletBTC":
                        user = await CRUDUsers.get(user_id=callback.from_user.id)
                        get_wallet = await CRUDWallet.get(user_id=user.id)
                        check_wallet = await Cryptocurrency.Check_Wallet(btc_address=get_wallet.address)

                        if check_wallet:
                            try:
                                get_btc = await state.get_data()
                                text = f"Отправляем BTC {get_btc['buy_BTC']} ➡️➡️➡\n\n" \
                                       f"Необходимо оплатить {get_btc['sale']} {get_btc['currency']}\n\n" \
                                       f"Адрес кошелька: {get_wallet.address}\n" \
                                       f"Доступ к вашему кошельку находится в профиле\n\n" \
                                       f"☑️ Проверьте Всё верно?\n" \
                                       f"Если вы ввели неверный адрес кошелька нажмите кнопку " \
                                       f"Нет ⛔️, и начните процедуру заново.️"

                                await state.update_data(wallet=get_wallet.address)
                                await callback.message.edit_text(text=text,
                                                                 reply_markup=await MainForm.CheckOut_wallet_ikb())
                            except KeyError as e:
                                print(e)
                                await callback.message.edit_text(text="У вас вышло время на оплату",
                                                                 reply_markup=await MainForm.start_ikb(
                                                                     user_id=callback.from_user.id)
                                                                 )
                                await state.finish()
                                await callback.message.delete()

                        else:
                            await callback.message.edit_text(text=f"Адрес кошелька <i>{get_wallet.address}</i> "
                                                                  f"нету в blockchain\n\n"
                                                                  f"Желаете еще раз ввести ваш адрес Bitcoin - кошелька",
                                                             reply_markup=await MainForm.CheckOut_ikb(),
                                                             parse_mode="HTML"
                                                             )

                    # BTC
                    elif data.get('action') == "SelectUserWallet":
                        user = await CRUDUsers.get(user_id=callback.from_user.id)
                        get_wallet = await CRUDWallet.get(user_id=user.id)
                        check_wallet = await Cryptocurrency.Check_Wallet(btc_address=get_wallet.address)

                        if check_wallet:
                            try:
                                currency = data.get("id")
                                currency_txt = "BYN 🇧🇾" if currency == "BYN" else "RUB 🇷🇺"
                                get_data_buy = await state.get_data()
                                if currency == "BYN":
                                    get_currency = await CRUDCurrency.get(currency_id=1)
                                    await state.update_data(exchange_rate=get_data_buy['exchange_BYN'])
                                    await state.update_data(sale=get_data_buy['price_BYN'])
                                    await state.update_data(currency_id=get_currency.id)
                                    await state.update_data(currency=get_currency.name)
                                else:
                                    get_currency = await CRUDCurrency.get(currency_id=2)
                                    await state.update_data(exchange_rate=get_data_buy['exchange_RUB'])
                                    await state.update_data(sale=get_data_buy['price_RUB'])
                                    await state.update_data(currency_id=get_currency.id)
                                    await state.update_data(currency=get_currency.name)

                                get_btc = await state.get_data()
                                text = f"Отправляем BTC {get_btc['buy_BTC']} ➡️➡️➡\n\n" \
                                       f"Адрес кошелька: {get_wallet.address}\n" \
                                       f"Доступ к вашему кошельку находится в профиле\n\n" \
                                       f"☑️ Проверьте Всё верно?\n" \
                                       f"Если вы ввели неверный адрес кошелька нажмите кнопку " \
                                       f"Нет ⛔️, и начните процедуру заново.️"

                                await state.update_data(wallet=get_wallet.address)
                                await callback.message.edit_text(text=text,
                                                                 reply_markup=await MainForm.CheckOut_wallet_ikb())
                            except KeyError as e:
                                print(e)
                                await callback.message.edit_text(text="У вас вышло время на оплату",
                                                                 reply_markup=await MainForm.start_ikb(
                                                                     user_id=callback.from_user.id)
                                                                 )
                                await state.finish()
                                await callback.message.delete()

                        else:
                            await callback.message.edit_text(text=f"Адрес кошелька <i>{get_wallet.address}</i> "
                                                                  f"нету в blockchain\n\n"
                                                                  f"Желаете еще раз ввести ваш адрес Bitcoin - кошелька",
                                                             reply_markup=await MainForm.CheckOut_ikb(),
                                                             parse_mode="HTML"
                                                             )

                    elif data.get('action') == "get_requisites":
                        try:
                            wallet = await state.get_data()

                            text_wallet = f"🚀 На Ваш кошелек  ➡️➡️➡️ <i>{wallet['wallet']}</i>\n" \
                                          f"будет отправлено <i>{wallet['buy_BTC']}</i> BTC. 🚀"
                            if wallet['currency'] == "BYN":
                                await callback.message.edit_text(text=f"{text_wallet}\n\n"
                                                                      f"{CONFIGTEXT.RequisitesBYN.TEXT}",
                                                                 reply_markup=await MainForm.user_paid_ikb(),
                                                                 parse_mode="HTML"
                                                                 )
                            else:
                                await callback.message.edit_text(text=f"{text_wallet}\n\n"
                                                                      f"{CONFIGTEXT.RequisitesRUS.TEXT}",
                                                                 reply_markup=await MainForm.user_paid_ikb(),
                                                                 parse_mode="HTML"
                                                                 )
                        except Exception as e:
                            print(e)
                            await callback.message.delete()
                            await state.finish()
                            await callback.message.edit_text(text="У вас вышло время на оплату",
                                                             reply_markup=await MainForm.start_ikb(
                                                                 user_id=callback.from_user.id)
                                                             )

                # Загрузка картинки с потввержением об оплате
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
                # Ввод кошелька
                if await state.get_state() == "MainState:Wallet":
                    wallet = await Cryptocurrency.Check_Wallet(btc_address=message.text)
                    if wallet:
                        get_btc = await state.get_data()
                        text = f"Отправляем BTC {get_btc['buy_BTC']} ➡️➡️➡\n\n" \
                               f"Адрес кошелька: {message.text}\n" \
                               f"Доступ к вашему кошельку находится в профиле\n\n" \
                               f"☑️ Проверьте Всё верно?\n" \
                               f"Если вы ввели неверный адрес кошелька нажмите кнопку " \
                               f"Нет ⛔️, и начните процедуру заново.️"

                        await state.update_data(wallet=message.text)
                        await message.answer(text=text,
                                             reply_markup=await MainForm.CheckOut_wallet_ikb())

                    else:
                        await message.answer(text=f"Адрес кошелька <i>{message.text}</i> нету в blockchain\n\n"
                                                  f"Желаете еще раз ввести ваш адрес Bitcoin - кошелька",
                                             reply_markup=await MainForm.CheckOut_ikb(),
                                             parse_mode="HTML"
                                             )

                # Загрузка фото
                elif await state.get_state() == "MainState:UserPhoto":
                    if message.content_type == "photo":
                        if message.photo[0].file_size > 2000:
                            await message.answer(text="Картинка превышает 2 мб\n"
                                                      "Попробуйте загрузить еще раз")
                            await MainState.UserPhoto.set()
                        else:
                            get_photo = await bot.get_file(message.photo[len(message.photo) - 1].file_id)
                            photo = message.photo[0].file_id

                            get_data = await state.get_data()

                            user = await CRUDUsers.get(user_id=message.from_user.id)

                            transaction = await CRUDTransaction.add(transaction=TransactionSchema(user_id=user.id,
                                                                                                  operation_id=1,
                                                                                                  **get_data)
                                                                    )

                            try:
                                await bot.download_file(file_path=get_photo.file_path,
                                                        destination=f'user_check/{transaction.id}_{message.from_user.id}.jpg',
                                                        timeout=12,
                                                        chunk_size=1215000)

                                get_transaction = await CRUDTransaction.get(transaction=transaction.id)
                                get_transaction.check = f'{transaction.id}_{message.from_user.id}'
                                await CRUDTransaction.update(transaction=get_transaction)
                                if len(get_data) > 6:
                                    text = f"Заявка № {transaction.id}\n\n" \
                                           f"Имя: {message.from_user.first_name}\n" \
                                           f"Курс: {round(get_data['exchange_rate'])} {get_data['currency']}\n" \
                                           f"Процент от суммы {get_data['percent']}\n" \
                                           f"Получено BTC: {get_data['buy_BTC']}\n" \
                                           f"Нужно отправить {get_data['currency']}: {get_data['sale']}\n" \
                                           f"Кошелёк: {get_data['wallet']}"
                                else:
                                    text = f"Заявка № {transaction.id}\n\n" \
                                           f"Имя {message.from_user.first_name}\n" \
                                           f"Курс: {round(get_data['exchange_rate'])}\n" \
                                           f"Процент от суммы {get_data['percent']}\n" \
                                           f"Получено {get_data['currency']}: {get_data['sale']}\n" \
                                           f"Нужно отправить  BTC: {get_data['buy_BTC']}\n" \
                                           f"Кошелёк: {get_data['wallet']}"

                                for admin in CONFIG.BOT.ADMINS:
                                    await bot.send_photo(chat_id=admin, photo=photo,
                                                         caption=f"Пользователь оплатил!\n\n"
                                                                 f"{text}")

                                await MainForm.confirmation_timer(message=message)

                            except Exception as e:
                                print(e)
                                await message.answer(text="У вас вышло время на оплату",
                                                     reply_markup=await MainForm.start_ikb(user_id=message.from_user.id)
                                                     )
                            await state.finish()
                    else:
                        await message.answer(text="Загрузите картинку")
                        await MainState.UserPhoto.set()

                # Загрузка 1 фото для верификации
                elif await state.get_state() == "MainState:VerificationPhotoOne":
                    if message.content_type == "photo":
                        if message.photo[0].file_size > 2000:
                            await message.answer(text="Картинка превышает 2 мб\n"
                                                      "Попробуйте загрузить еще раз")
                            await MainState.VerificationPhotoOne.set()
                        else:
                            get_photo = await bot.get_file(message.photo[len(message.photo) - 1].file_id)
                            photo = message.photo[0].file_id

                            await bot.download_file(file_path=get_photo.file_path,
                                                    destination=f'user_verification/{message.from_user.id}_user_verification_1.jpg',
                                                    timeout=12,
                                                    chunk_size=1215000)

                            await state.update_data(verification=f'{message.from_user.id}_user_verification_1')
                            await message.answer(text="Загрузите селфи с паспортом последней страницы")
                            await MainState.VerificationPhotoTwo.set()
                    else:
                        await message.answer(text="Загрузите картинку")
                        await MainState.VerificationPhotoOne.set()

                # Загрузка 2 фото для верификации
                elif await state.get_state() == "MainState:VerificationPhotoTwo":
                    if message.content_type == "photo":
                        if message.photo[0].file_size > 2000:
                            await message.answer(text="Картинка превышает 2 мб\n"
                                                      "Попробуйте загрузить еще раз")
                            await MainState.VerificationPhotoTwo.set()
                        else:
                            get_photo = await bot.get_file(message.photo[len(message.photo) - 1].file_id)

                            await bot.download_file(file_path=get_photo.file_path,
                                                    destination=f'user_verification/{message.from_user.id}_user_verification_2.jpg',
                                                    timeout=12,
                                                    chunk_size=1215000)

                            await state.update_data(verification2=f'{message.from_user.id}_user_verification_2')
                            data = await state.get_data()
                            photo_id = [data['verification'], data['verification2']]
                            user = await CRUDUsers.get(user_id=message.from_user.id)

                            verification = await CRUDVerification.add(verification=VerificationSchema(
                                user_id=user.id,
                                photo_id=photo_id
                            ))
                            user.verification_id = verification.id

                            await CRUDUsers.update(user=user)

                            for admin in CONFIG.BOT.ADMINS:
                                await bot.send_message(chat_id=admin,
                                                       text=f"Пользователь {message.from_user.id}\n"
                                                            f"добавил фото для верификации")

                            await message.answer(text="Фото успешно загружены\n\n"
                                                      "Ожидайте потверждения")
                            await state.finish()
                    else:
                        await message.answer(text="Загрузите картинку")
                        await MainState.VerificationPhotoTwo.set()

                # Ввод пользователем BYN or RUB
                elif await state.get_state() == "MainState:UserCoin":
                    money = message.text.isdigit()
                    if money:
                        currency = await state.get_data()
                        if currency["currency"] == "BYN":
                            await MainForm.buying_currency(money=message.text,
                                                           currency=currency["currency"],
                                                           limit=CONFIG.COMMISSION.MIN_BYN,
                                                           message=message,
                                                           state=state)
                        else:
                            await MainForm.buying_currency(money=message.text,
                                                           currency=currency["currency"],
                                                           limit=CONFIG.COMMISSION.MIN_RUB,
                                                           message=message,
                                                           state=state)

                    else:
                        await message.answer(text="Вы ввели некорректные данные\n"
                                                  "Доступен ввод только цифр")
                        await MainState.UserCoin.set()

                # Ввод пользователем кошелька BTC для вывода денег
                elif await state.get_state() == "MainState:WalletRecipient":
                    wallet = await Cryptocurrency.Check_Wallet(btc_address=message.text)
                    if wallet:
                        user = await CRUDUsers.get(user_id=message.from_user.id)
                        wallet = await CRUDWallet.get(user_id=user.id)
                        balance = await CreateWallet.get_balance(wallet=wallet.address)

                        await state.update_data(address_recipient=message.text)  # запоминаем кошелек
                        await message.answer(text=f"Кошелек отправителя <i>{message.text}</i>\n\n"
                                                  f"Ваш баланс {balance}\n"
                                                  f"Введите количество BTC которое хотите отправить",
                                             parse_mode="HTML",
                                             reply_markup=await MainForm.back_ikb(
                                                 user_id=message.from_user.id,
                                                 target="Profile",
                                                 action="get_userWallet",
                                                 page=0)
                                             )
                        await MainState.Money.set()
                    else:
                        await message.answer(text=f"Адрес кошелька <i>{message.text}</i> нету в blockchain\n\n"
                                                  f"Введите еще раз адрес Bitcoin кошелька получателя",
                                             reply_markup=await MainForm.back_ikb(
                                                 user_id=message.from_user.id,
                                                 target="Profile",
                                                 action="get_userWallet",
                                                 page=0),
                                             parse_mode="HTML"
                                             )
                        await MainState.WalletRecipient.set()

                # Ввод пользователем кошелька BTC для вывода денег
                elif await state.get_state() == "MainState:Money":
                    user = await CRUDUsers.get(user_id=message.from_user.id)
                    wallet = await CRUDWallet.get(user_id=user.id)
                    balance = await CreateWallet.get_balance(wallet=wallet.address)

                    get_money = await MainForm.isfloat(message.text)
                    if get_money:
                        if float(message.text) < balance:
                            data = await state.get_data()
                            await state.update_data(btc_money=message.text)  # запоминаем ввуденую сумму BTC
                            await message.answer(text=f"Потвердите операцию\n\n"
                                                      f"Адрес кошелька получателя <i>{data['address_recipient']}</i>\n"
                                                      f"Отпраить BTC {float(message.text)}",
                                                 parse_mode="HTML",
                                                 reply_markup=await MainForm.money_transfer_ikb(
                                                     user_id=message.from_user.id)
                                                 )
                        else:
                            await message.answer(text=f"Недостаточно средств\n"
                                                      f"У вас на балансе доступно {balance} BTC\n\n"
                                                      f"Введите сумму занова",
                                                 reply_markup=await MainForm.back_ikb(
                                                     user_id=message.from_user.id,
                                                     target="Profile",
                                                     action="get_userWallet",
                                                     page=0)
                                                 )
                            await MainState.Money.set()
                    else:
                        await message.answer(text="Введите число!",
                                             reply_markup=await MainForm.back_ikb(
                                                 user_id=message.from_user.id,
                                                 target="Profile",
                                                 action="get_userWallet",
                                                 page=0)
                                             )
                        await MainState.Money.set()

                elif await state.get_state() == "MainState:ByeBTC":
                    money_int = message.text.isdigit()
                    money_float = await MainForm.isfloat(value=message.text)

                    if money_float or money_int:
                        await MainForm.buying_BTC(user_money=message.text,
                                                  message=message,
                                                  state=state)
                    else:
                        await message.answer(text="Введите число!")