from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import BadRequest

from config import CONFIG
from crud import CRUDUsers, CRUDTransaction, CRUDCurrency
from crud.referralCRUD import CRUDReferral
from crud.walCRUD import CRUDWallet
from handlers.users.CreateWallet import CreateWallet
from handlers.users.Cryptocurrency import Cryptocurrency
from loader import bot
from schemas import TransactionSchema, WalletSchema
from states.users.MainState import MainState

main_cb = CallbackData("main", "target", "action", "id", "editId")


class MainForm:

    @staticmethod
    async def buying_currency(money: int, currency: str, limit: int, message, state):
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
            price_BTC = await Cryptocurrency.get_Cryptocurrency(currency)
            bye = round(int(user_money) / price_BTC, 8)

            currency = await CRUDCurrency.get(currency_name=currency)

            await state.update_data(currency_id=currency.id)
            await state.update_data(sale=user_money)
            await state.update_data(exchange_rate=price_BTC)
            await state.update_data(buy_BTC=bye)

            text = f"💳 Купить криптовалюту: BTC за {currency}\n" \
                   f"1 Bitcoin = {price_BTC} {currency}\n\n" \
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
                ],
                [
                    InlineKeyboardButton(text="◀️ Назад", callback_data=main_cb.new("Buy", "get_reenter", 0, 0))
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
                    InlineKeyboardButton(text="Нет ⛔️", callback_data=main_cb.new("Buy", "get_reenter", 0, 0))
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
        # data = {"50 BYN": {"target": "Pay", "action": "get_pay", "id": "50", "editid": user_id},
        #         "100 BYN": {"target": "Pay", "action": "get_pay", "id": "100", "editid": user_id},
        #         "200 BYN": {"target": "Pay", "action": "get_pay", "id": "200", "editid": user_id},
        #         }
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
    async def currency_ikb(user_id: int, target: str) -> InlineKeyboardMarkup:
        """
                Клавиатура при покупке валюты
                :param user_id: id пользователя
                :param target: Параметр что бы указать куда переходить назад
                :return:
                """
        data = {
            "BYN 🇧🇾": {"target": "Pay", "action": "get_BUN", "id": "BYN", "editid": user_id},
            "RUB 🇷🇺": {"target": "Pay", "action": "get_RUB", "id": "RUB", "editid": user_id},
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
                    InlineKeyboardButton(text="◀️ Назад", callback_data=main_cb.new(target, 0, 0, user_id))
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
    async def wallet_user_ikb(user_id: int, action_back: str, wallet_exists: bool) -> InlineKeyboardMarkup:
        """
        Клавиатура для ввода BTC кошелька
        :param wallet_exists: Проверка на существование кошелька, если есть выводить клавиатуру только с кнопкой назад,
        если не существует тогда выводить клавиатуру с кнопкой создать
        :param action_back: Параметр что бы указать куда переходить назад
        :param user_id: id пользователя
        :return:
        """

        data = {
            "➕ Создать": {"target": "Profile", "action": "get_createWallet", "id": 0, "editid": user_id},
            "◀️ Назад": {"target": "Profile", "action": action_back, "id": 0, "editid": user_id},
        }
        if wallet_exists:
            return InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="◀️ Назад", callback_data=main_cb.new("Profile", action_back,
                                                                                        0, user_id)
                                             )
                    ]
                ]
            )
        else:
            return InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text=name, callback_data=main_cb.new(name_items["target"],
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
            "💳 Купить BTC": {"target": "BuyBTC", "action": "get_BuyBTC", "id": 0, "editid": user_id},
            "💳 Продать BTC": {"target": "SellBTC", "action": "get_SellBTC", "id": 0, "editid": user_id},
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
        data = {"🤝 Сделки": {"target": "Profile", "action": "get_transaction", "id": 0, "editid": user_id},
                "👨‍👦‍👦 Рефералы": {"target": "Profile", "action": "get_referrals", "id": 0, "editid": user_id},
                "👛 Кошелек": {"target": "Profile", "action": "get_userWallet", "id": 0, "editid": user_id},
                "◀️ Назад": {"target": target, "action": "", "id": 0, "editid": user_id}
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
    async def process_profile(callback: CallbackQuery = None, message: Message = None,
                              state: FSMContext = None) -> None:

        if callback:
            if callback.data.startswith('main'):
                data = main_cb.parse(callback_data=callback.data)
                # Главное меню
                if data.get("target") == "MainForm":
                    await callback.message.edit_text(text="Добро пожаловать\n"
                                                          "Выберите операцию",
                                                     reply_markup=await MainForm.start_ikb(
                                                         user_id=callback.from_user.id)
                                                     )

                # Профиль
                elif data.get("target") == "Profile":
                    if data.get("action") == "get_Profile":
                        user = await CRUDUsers.get(user_id=callback.from_user.id)
                        transaction = await CRUDTransaction.get_all(user_id=user.id)

                        text = f"Профиль\n\n" \
                               f"Регитрация в боте - {user.date_created.strftime('%Y.%m.%d')}\n" \
                               f"Количество сделок - {len(transaction)}\n\n" \
                               f"Реферальная ссылка: \n" \
                               f"<code>{CONFIG.BOT.BOT_LINK}?start={callback.from_user.id}</code>"

                        await callback.message.edit_text(text=text,
                                                         reply_markup=await MainForm.profile_ikb(
                                                             user_id=callback.from_user.id,
                                                             target="MainForm"),
                                                         parse_mode="HTML"
                                                         )

                    elif data.get("action") == "get_transaction":
                        user = await CRUDUsers.get(user_id=callback.from_user.id)
                        transaction = await CRUDTransaction.get_all(user_id=user.id)
                        currency = await CRUDCurrency.get(currency_id=transaction[0].currency_id)

                        if transaction:
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
                        currency = await CRUDCurrency.get(currency_id=transaction[page].currency_id)

                        if transaction:
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
                        user = await CRUDUsers.get(user_id=callback.from_user.id)
                        wallet = await CRUDWallet.get(user_id=user.id)
                        if wallet:
                            await callback.message.edit_text(text=f"Ваш адрес кошелька\n"
                                                                  f"{wallet.address}\n"
                                                                  f"Баланс : {wallet.balance}",
                                                             reply_markup=await MainForm.wallet_user_ikb(
                                                                 user_id=callback.from_user.id,
                                                                 action_back="get_Profile",
                                                                 wallet_exists=True)
                                                             )
                        else:
                            await callback.message.edit_text(text="У вас нету кошелька",
                                                             reply_markup=await MainForm.wallet_user_ikb(
                                                                 user_id=callback.from_user.id,
                                                                 action_back="get_Profile",
                                                                 wallet_exists=False)
                                                             )

                    elif data.get("action") == "get_createWallet":
                        get_wallet = await CreateWallet.create_wallet(label=f"{str(callback.from_user.id)}")
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

                        await callback.message.edit_text(text=f"Ваш адрес кошелька\n"
                                                              f"<code>{wallet.address}</code>\n"
                                                              f"Баланс : {wallet.balance}",
                                                         reply_markup=await MainForm.wallet_user_ikb(
                                                             user_id=callback.from_user.id,
                                                             action_back="get_Profile",
                                                             wallet_exists=True),
                                                         parse_mode="HTML"
                                                         )

                # Меню выбора количесво суммы для покупки BTC
                elif data.get("target") == "BuyBTC":
                    price = await Cryptocurrency.get_Cryptocurrency(currency="USD")

                    text = "Выберите валюту\n"\
                           f"1 Bitcoin ₿ = {price} USD 🇺🇸 " \
                           f"<a href='https://www.coinbase.com/ru/converter/btc/usd'>Coinbase</a>\n\n"\

                    await callback.message.edit_text(text=text,
                                                     reply_markup=await MainForm.currency_ikb(
                                                         user_id=callback.from_user.id,
                                                         target="MainForm"),
                                                     parse_mode="HTML",
                                                     disable_web_page_preview=True
                                                     )

                # Меню покупки BTC
                elif data.get("target") == "Pay":
                    if data.get("action") == "get_pay":
                        price_BYN = int(data.get("id"))
                        price_BTC = await Cryptocurrency.get_Cryptocurrency(currency="BYN")
                        bye = round(price_BYN / price_BTC, 8)

                        await state.update_data(sale_BYN=price_BYN)
                        await state.update_data(exchange_rate=price_BTC)
                        await state.update_data(buy_BTC=bye)

                        text = "💳 Купить криптовалюту: BTC за BYN\n" \
                               f"1 Bitcoin = {price_BTC}\n\n" \
                               f"📢 Внимание!\n" \
                               f"Текущая цена покупки зафиксирована!\n" \
                               f"Нажав кнопку Купить ✅ " \
                               f"необходимо оплатить счет в течении ⏱60 минут!\n\n" \
                               f"{price_BYN} BYN = {bye} BTC"

                        await callback.message.edit_text(text=text,
                                                         reply_markup=await MainForm.bue_ikb(
                                                             user_id=callback.from_user.id,
                                                             count=bye,
                                                             target="BuyBTC")
                                                         )

                    elif data.get('action') == "get_BUN":
                        price = await Cryptocurrency.get_Cryptocurrency(currency="BYN")

                        text = "Купить BTC за BYN\n" \
                               f"1 Bitcoin ₿ = {price} BYN 🇧🇾 " \
                               f"<a href='https://www.coinbase.com/ru/converter/btc/byn'>Coinbase</a>\n\n" \
                               f"<i>Мин. сумма 50 BYN</i>"

                        await callback.message.edit_text(text=text,
                                                         reply_markup=await MainForm.money_entry_ikb(
                                                             user_id=callback.from_user.id,
                                                             target="BuyBTC",
                                                             currency="BYN"),
                                                         parse_mode="HTML",
                                                         disable_web_page_preview=True
                                                         )

                    elif data.get('action') == "get_RUB":
                        price = await Cryptocurrency.get_Cryptocurrency(currency="RUB")

                        text = "Купить BTC за RUB\n" \
                               f"1 Bitcoin ₿ = {price} RUB 🇷🇺 " \
                               f"<a href='https://www.coinbase.com/ru/converter/btc/rub'>Coinbase</a>\n\n" \
                               f"<i>Мин. сумма 1000 RUB</i>"

                        await callback.message.edit_text(text=text,
                                                         reply_markup=await MainForm.money_entry_ikb(
                                                             user_id=callback.from_user.id,
                                                             target="BuyBTC",
                                                             currency="RUB"),
                                                         parse_mode="HTML",
                                                         disable_web_page_preview=True
                                                         )

                    elif data.get("action") == "EnterAmount":
                        currency = data.get("id")
                        currency_txt = "BYN 🇧🇾" if currency == "BYN" else "RUB 🇷🇺"

                        await state.update_data(currency=currency)
                        await callback.message.edit_text(text=f"Введите сумму в {currency_txt}:",
                                                         reply_markup=await MainForm.back_ikb(
                                                             action="",
                                                             user_id=callback.from_user.id,
                                                             target="BuyBTC")
                                                         )
                        await MainState.UserCoin.set()

                # Меню ввода кошелька
                elif data.get("target") == "Buy":
                    bye = float(data.get("id"))
                    await callback.message.edit_text(text="🔐 Введите ваш адрес Bitcoin - кошелька 🔐:\n\n"
                                                          f"Покупка - {bye} BTC",
                                                     reply_markup=await MainForm.back_ikb(
                                                         user_id=callback.from_user.id,
                                                         action="",
                                                         target="BuyBTC")
                                                     )
                    await MainState.Wallet.set()

                    if data.get("action") == "get_reenter":
                        get_data = await state.get_data()
                        await callback.message.edit_text(text="🔐 Введите ваш адрес Bitcoin - кошелька 🔐:\n\n"
                                                              f"Покупка - {get_data['buy_BTC']} BTC",
                                                         reply_markup=await MainForm.back_ikb(
                                                             user_id=callback.from_user.id,
                                                             action="",
                                                             target="BuyBTC")
                                                         )
                        await MainState.Wallet.set()

                    elif data.get('action') == "get_requisites":
                        wallet = await state.get_data()

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

                        text_wallet = f"🚀 На Ваш кошелек  ➡️➡️➡️ <i>{wallet['wallet']}</i>\n" \
                                      f"будет отправлено <i>{wallet['buy_BTC']}</i> BTC. 🚀"

                        await callback.message.edit_text(text=f"{text_wallet}\n\n"
                                                              f"{text}",
                                                         reply_markup=await MainForm.user_paid_ikb(),
                                                         parse_mode="HTML"
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
                               f"Адрес кошелька: {message.text}\n\n" \
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
                                                                                                  **get_data)
                                                                    )

                            await bot.download_file(file_path=get_photo.file_path,
                                                    destination=f'user_check/{transaction.id}_{message.from_user.id}.jpg',
                                                    timeout=12,
                                                    chunk_size=1215000)

                            get_transaction = await CRUDTransaction.get(transaction=transaction.id)
                            get_transaction.check = f'{transaction.id}_{message.from_user.id}'
                            await CRUDTransaction.update(transaction=get_transaction)

                            text = f"Заявка № {transaction.id}\n\n" \
                                   f"Курс: {get_data['exchange_rate']}\n" \
                                   f"Получено {get_data['currency']}: {get_data['sale']}\n" \
                                   f"Нужно отправить  BTC: {get_data['buy_BTC']}\n" \
                                   f"Кошелёк: {get_data['wallet']}"

                            for admin in CONFIG.BOT.ADMINS:
                                await bot.send_photo(chat_id=admin, photo=photo,
                                                     caption=f"Пользователь оплатил!\n\n"
                                                             f"{text}")

                            await message.answer(text="Ваша заявка уже обрабатывается как только она будет "
                                                      "выполнена мы вам сообщим.\n\n"
                                                      "Спасибо что выбрали нас 🤗✌️\n\n"
                                                      "🚀 Желаем Вам отличного настроения!")
                            await state.finish()
                    else:
                        await message.answer(text="Загрузите картинку")
                        await MainState.UserPhoto.set()

                # Ввод пользователем BYN
                elif await state.get_state() == "MainState:UserCoin":
                    money = message.text.isdigit()
                    if money:
                        currency = await state.get_data()
                        if currency["currency"] == "BYN":
                            await MainForm.buying_currency(money=message.text,
                                                           currency=currency["currency"],
                                                           limit=50,
                                                           message=message,
                                                           state=state)
                        else:
                            await MainForm.buying_currency(money=message.text,
                                                           currency=currency["currency"],
                                                           limit=1000,
                                                           message=message,
                                                           state=state)

                    else:
                        await message.answer(text="Вы ввели некорректные данные\n"
                                                  "Доступен ввод только цифр")
                        await MainState.UserCoin.set()
