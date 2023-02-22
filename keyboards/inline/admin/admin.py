from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import BadRequest

from config import CONFIG
from crud import CRUDUsers, CRUDTransaction
from handlers.users.Cryptocurrency import Cryptocurrency
from loader import bot
from schemas import TransactionSchema
from states.admins.AdminState import AdminState

admin_cb = CallbackData("admin", "target", "action", "id", "editId")


class AdminForm:
    @staticmethod
    async def back_ikb(target: str, action: str = None) -> InlineKeyboardMarkup:
        """
        Общая клавиатура для перехода на один шаг назад
        :param action: Не обязательный параметр, он необходим если в callback_data есть подзапрос для вкладки
        :param target: Параметр что бы указать куда переходить назад
        :return:
        """
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="◀️ Назад", callback_data=admin_cb.new(target, action, 0, 0))
                ]
            ]
        )

    @staticmethod
    async def change_ikb(get_change: str) -> InlineKeyboardMarkup:
        """
        Клавиатура для изменения данных Комиссии(0) или Расчётный счёт(1)
        :param get_change: необходим для того что бы отслеживать что выбрал админ 1 или 0
        :return:
        """
        data = {"🔁 Изменить": {"target": "PaymentSetup", "action": "get_change", "id": 1, "editId": get_change},
                "◀️ Назад": {"target": "PaymentSetup", "action": "get_Setup", "id": 2, "editId": get_change},
                }

        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=name, callback_data=admin_cb.new(name_items["target"],
                                                                               name_items["action"],
                                                                               name_items["id"],
                                                                               name_items["editId"]))
                ] for name, name_items in data.items()
            ]
        )

    @staticmethod
    async def start_ikb() -> InlineKeyboardMarkup:
        """
        Клавиатура главного меню админ панели
        :return:
        """
        data = {"⚙️ Настройка Оплаты": {"target": "PaymentSetup", "action": "get_Setup", "id": 0, "editid": 0},
                "📨 Рассылка": {"target": "Newsletter", "action": "get_Newsletter", "id": 0, "editid": 0},
                "👨‍💻 Пользователи": {"target": "Users", "action": "get_Users", "id": 0, "editid": 0},
                }
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=name, callback_data=admin_cb.new(name_items["target"],
                                                                               name_items["action"],
                                                                               name_items["id"],
                                                                               name_items["editid"]))
                ] for name, name_items in data.items()
            ]
        )

    @staticmethod
    async def payment_setup_ikb() -> InlineKeyboardMarkup:
        data = {"% Комиссия": {"target": "PaymentSetup", "action": "get_Commission", "id": 0, "editid": 0},
                "🧾 Расчетный Счет": {"target": "PaymentSetup", "action": "get_Settlement_Account", "id": 0,
                                      "editid": 0},
                "◀️ Назад": {"target": "StartMenu", "action": "", "id": 0, "editid": 0},
                }
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=name, callback_data=admin_cb.new(name_items["target"],
                                                                               name_items["action"],
                                                                               name_items["id"],
                                                                               name_items["editid"]))
                ] for name, name_items in data.items()
            ]
        )

    @staticmethod
    async def users_ikb() -> InlineKeyboardMarkup:
        """
                Клавиатура главного меню админ панели
                :return:
                """
        data = {"👥 Все пользователи": {"target": "Users", "action": "get_AllUsers", "id": 0, "editid": 0},
                "#️⃣ Номер чек": {"target": "Users", "action": "get_CheckNumber", "id": 0, "editid": 0},
                "🆔 id Пользователя": {"target": "Users", "action": "get_UsersId", "id": 0, "editid": 0},
                "◀️ Назад": {"target": "StartMenu", "action": "", "id": 0, "editid": 0},
                }
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=name, callback_data=admin_cb.new(name_items["target"],
                                                                               name_items["action"],
                                                                               name_items["id"],
                                                                               name_items["editid"]))
                ] for name, name_items in data.items()
            ]
        )

    @staticmethod
    async def check_confirmation_ikb(user_id: int, page: int = 0, action_back: str = None,
                                     action_confirm: str = None) -> InlineKeyboardMarkup:
        """
        Клавиатура для взаимодействия с транзакцией пользователя
        :param user_id: id Пользователя
        :param page: не обходимо для того что бы возвращаться к определенной странице
        :param action_back: не обходимо для того что бы возвращаться на определеную страницу
        :param action_confirm: не обходимо для того что бы возвращаться на определеную страницу
        :return:
        """
        user = await CRUDUsers.get(id=user_id)
        chat = await bot.get_chat(chat_id=user.user_id)
        button_url = chat.user_url

        data = {"✅ Потвердить Оплату": {"target": "Users", "action": action_confirm, "id": user_id, "editid": page},
                "◀️ Назад": {"target": "Users", "action": action_back, "id": page, "editid": user_id},
                }
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="📲 Связаться", url=button_url)
                ]

            ] + [
                [
                    InlineKeyboardButton(text=name, callback_data=admin_cb.new(name_items["target"],
                                                                               name_items["action"],
                                                                               name_items["id"],
                                                                               name_items["editid"])
                                         )
                ] for name, name_items in data.items()
            ]
        )

    @staticmethod
    async def pagination_transaction_ikb(target: str,
                                         user_id: int = None,
                                         action: str = None,
                                         action_back: str = None,
                                         page: int = 0) -> InlineKeyboardMarkup:
        """
        Клавиатура пагинации проведенных операций пользователя
        :param action_back:
        :param target:  Параметр что бы указать куда переходить назад
        :param user_id: id пользователя
        :param action: Не обязательный параметр, он необходим если в callback_data есть подзапрос для вкладки
        :param page: текущая страница пагинации
        :return:
        """
        if user_id:
            orders = await CRUDTransaction.get_all(user_id=user_id)
        else:
            orders = await CRUDTransaction.get_all()

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

        back_ikb = InlineKeyboardButton("◀️ Назад", callback_data=admin_cb.new("Users", action_back, 0, user_id))
        prev_page_ikb = InlineKeyboardButton("←", callback_data=admin_cb.new(target, action, prev_page, user_id))
        check = InlineKeyboardButton("☰", callback_data=admin_cb.new("Users", "get_check_admin", page, user_id))
        page = InlineKeyboardButton(f"{str(page + 1)}/{str(orders_count)}",
                                    callback_data=admin_cb.new("", "", 0, 0))
        next_page_ikb = InlineKeyboardButton("→", callback_data=admin_cb.new(target, action, next_page, user_id))

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
    async def process_admin_profile(callback: CallbackQuery = None, message: Message = None,
                                    state: FSMContext = None) -> None:
        if callback:
            if callback.data.startswith('admin'):
                data = admin_cb.parse(callback_data=callback.data)

                if data.get("target") == "StartMenu":
                    await callback.message.edit_text(text="Админ панель",
                                                     reply_markup=await AdminForm.start_ikb())

                elif data.get("target") == "PaymentSetup":
                    if data.get("action") == "get_Setup":
                        await callback.message.edit_text(text="Настройка оплаты",
                                                         reply_markup=await AdminForm.payment_setup_ikb())
                        await state.finish()

                    elif data.get("action") == "get_Commission":
                        await callback.message.edit_text(text=f"Комиссия составляет {CONFIG.COMMISSION}%",
                                                         reply_markup=await AdminForm.change_ikb(get_change="COMMISSION")
                                                         )

                    elif data.get("action") == "get_Settlement_Account":
                        await callback.message.edit_text(text=f"Расчётный счёт <i>{CONFIG.PAYMENT.REQUISITES}</i>",
                                                         reply_markup=await AdminForm.change_ikb(get_change="REQUISITES"),
                                                         parse_mode="HTML"
                                                         )

                    elif data.get("action") == "get_change":
                        get_change_data = str(data.get("editId"))
                        text = ""

                        if get_change_data == "COMMISSION":
                            text = "Введите новые данные для Комиссии"
                            await AdminState.COMMISSION.set()

                        elif get_change_data == "REQUISITES":
                            text = "Введите новые данные для Расчётного счёта"
                            await AdminState.REQUISITES.set()

                        await callback.message.edit_text(text=text,
                                                         reply_markup=await AdminForm.back_ikb(target="PaymentSetup",
                                                                                               action="get_Setup")
                                                         )

                elif data.get("target") == "PaymentSetup":
                    if data.get("action") == "get_Newsletter":
                        pass

                elif data.get("target") == "Users":
                    if data.get("action") == "get_Users":
                        try:
                            await callback.message.edit_text(text="Найти пользователя",
                                                             reply_markup=await AdminForm.users_ikb())
                        except BadRequest:
                            await callback.message.delete()
                            await callback.message.answer(text="Найти пользователя",
                                                          reply_markup=await AdminForm.users_ikb())

                    elif data.get("action") == "get_AllUsers":
                        transaction = await CRUDTransaction.get_all()

                        if transaction:
                            approved = "✅ одобрена ✅" if transaction[0].approved else "❌ не одобрена ❌"

                            text = f"🤝 Сделка № {transaction[0].id} {approved}\n\n" \
                                   f"📈 Курс покупки: <i>{transaction[0].exchange_rate}\n</i>" \
                                   f"   ₿  Куплено BTC: <i>{transaction[0].buy_BTC}\n</i>" \
                                   f"💸 Продано BYN: <i>{transaction[0].sale_BYN}\n</i>" \
                                   f"👛 Кошелек <i>{transaction[0].wallet}</i>"

                            await callback.message.edit_text(text="<i>Сделки пользователя</i>\n\n"
                                                                  f"{text}",
                                                             reply_markup=await AdminForm.pagination_transaction_ikb(
                                                                 target="Users",
                                                                 action="pagination_user_transaction",
                                                                 action_back="get_Users",
                                                                 user_id=transaction[0].user_id),
                                                             parse_mode="HTML"
                                                             )
                            await state.finish()
                        else:
                            await message.answer(text="Не найдено")
                            await state.finish()

                    elif data.get("action") == "get_CheckNumber":
                        await callback.message.edit_text(text="Введите номер чек",
                                                         reply_markup=await AdminForm.back_ikb(target="Users",
                                                                                               action="get_Users")
                                                         )
                        await AdminState.CheckNumber.set()

                    elif data.get("action") == "get_UsersId":
                        await callback.message.edit_text(text="Введите id Пользователя",
                                                         reply_markup=await AdminForm.back_ikb(target="Users",
                                                                                               action="get_Users")
                                                         )
                        await AdminState.UsersId.set()

                    elif data.get('action') == "pagination_user_transaction":
                        page = int(data.get('id'))
                        get_user_id = int(data.get('editId'))

                        user = await CRUDUsers.get(id=get_user_id)
                        transaction = await CRUDTransaction.get_all(user_id=user.id)

                        if transaction:
                            approved = "✅ одобрена ✅" if transaction[0].approved else "❌ не одобрена ❌"

                            text = f"🤝 Сделка № {transaction[page].id} {approved}\n\n" \
                                   f"📈 Курс покупки: <i>{transaction[page].exchange_rate}\n</i>" \
                                   f"   ₿  Куплено BTC: <i>{transaction[page].buy_BTC}\n</i>" \
                                   f"💸 Продано BYN: <i>{transaction[page].sale_BYN}\n</i>" \
                                   f"👛 Кошелек <i>{transaction[page].wallet}</i>"
                            try:
                                await callback.message.edit_text(text=f"<i>Сделки пользователя</i>\n\n"
                                                                      f"{text}",
                                                                 reply_markup=await AdminForm.pagination_transaction_ikb(
                                                                     user_id=user.id,
                                                                     page=page,
                                                                     target="Users",
                                                                     action="pagination_user_transaction",
                                                                     action_back="get_Users"),
                                                                 parse_mode="HTML"
                                                                 )
                            except BadRequest:
                                await callback.message.delete()
                                await callback.message.answer(text=f"<i>Сделки Пользователя</i>\n\n"
                                                                   f"{text}",
                                                              reply_markup=await AdminForm.pagination_transaction_ikb(
                                                                  user_id=user.id,
                                                                  page=page,
                                                                  target="Users",
                                                                  action="pagination_user_transaction",
                                                                  action_back="get_Users"),
                                                              parse_mode="HTML"
                                                              )
                        else:
                            await callback.message.edit_text(text="Пользователь не совершал сделок 😞",
                                                             reply_markup=await AdminForm.back_ikb(
                                                                 target="Users",
                                                                 action="get_Users")
                                                             )

                    elif data.get('action') == "get_check_admin":
                        page = int(data.get('id'))
                        get_user_id = int(data.get('editId'))

                        user = await CRUDUsers.get(id=get_user_id)
                        transaction = await CRUDTransaction.get_all(user_id=user.id)

                        if transaction:
                            approved = "✅ одобрена ✅" if transaction[page].approved else "❌ не одобрена ❌"

                            text = f"🤝 Сделка № {transaction[page].id} {approved}\n\n" \
                                   f"📈 Курс покупки: <i>{transaction[page].exchange_rate}\n</i>" \
                                   f"   ₿  Куплено BTC: <i>{transaction[page].buy_BTC}\n</i>" \
                                   f"💸 Продано BYN: <i>{transaction[page].sale_BYN}\n</i>" \
                                   f"👛 Кошелек <i>{transaction[page].wallet}</i>"

                            if transaction[page].check != "None":
                                try:
                                    await callback.message.delete()
                                    photo = open(f'user_check/{transaction[page].check}.jpg', 'rb')
                                    await bot.send_photo(chat_id=callback.from_user.id, photo=photo,
                                                         caption=f"<i>Сделка пользователя</i>\n\n"
                                                                 f"{text}",
                                                         reply_markup=await AdminForm.check_confirmation_ikb(
                                                             page=page,
                                                             user_id=user.id,
                                                             action_back="pagination_user_transaction",
                                                             action_confirm="get_One_ConfirmPayment")
                                                         )
                                except FileNotFoundError:
                                    pass
                            else:
                                await callback.message.edit_text(text=f"<i>Сделка пользователя</i>\n\n"
                                                                      f"Пользователь не добавил чек\n\n"
                                                                      f"{text}",
                                                                 reply_markup=await AdminForm.check_confirmation_ikb(
                                                                     page=page,
                                                                     user_id=user.id,
                                                                     action_back="pagination_user_transaction",
                                                                     action_confirm="get_One_ConfirmPayment")
                                                                 )
                        else:
                            await callback.message.edit_text(text="Не найдено",
                                                             reply_markup=await AdminForm.back_ikb(target="Users",
                                                                                                   action="get_Users")
                                                             )

                    elif data.get('action') == "get_ConfirmPayment":
                        get_user_id = int(data.get('id'))
                        get_page_id = int(data.get('editId'))

                        user = await CRUDUsers.get(id=get_user_id)
                        transaction = await CRUDTransaction.get_all(user_id=user.id)

                        transaction[get_page_id].approved = True
                        await CRUDTransaction.update(transaction=transaction[get_page_id])
                        text = f"✅ Вам потвердили сделку № {transaction[get_page_id].id} ✅\n\n"\
                               f"📈 Курс покупки: <i>{transaction[get_page_id].exchange_rate}\n</i>" \
                               f"   ₿  Куплено BTC: <i>{transaction[get_page_id].buy_BTC}\n</i>" \
                               f"💸 Продано BYN: <i>{transaction[get_page_id].sale_BYN}\n</i>" \
                               f"👛 Кошелек <i>{transaction[get_page_id].wallet}</i>"

                        await bot.send_message(chat_id=user.user_id, text=text )

                        await callback.message.delete()
                        await callback.message.answer(text="Вы успешно потвердили сделку",
                                                      reply_markup=await AdminForm.users_ikb()
                                                      )

                    elif data.get('action') == "get_One_ConfirmPayment":
                        get_page_id = int(data.get('editId'))

                        transaction = await CRUDTransaction.get(transaction=get_page_id)
                        user = await CRUDUsers.get(id=transaction.user_id)
                        transaction.approved = True
                        await CRUDTransaction.update(transaction=transaction)
                        text = f"✅ Вам потвердили сделку № {transaction.id} ✅\n\n"\
                               f"📈 Курс покупки: <i>{transaction.exchange_rate}\n</i>" \
                               f"   ₿  Куплено BTC: <i>{transaction.buy_BTC}\n</i>" \
                               f"💸 Продано BYN: <i>{transaction.sale_BYN}\n</i>" \
                               f"👛 Кошелек <i>{transaction.wallet}</i>"

                        await bot.send_message(chat_id=user.user_id, text=text)

                        await callback.message.delete()
                        await callback.message.answer(text="Вы успешно потвердили сделку",
                                                      reply_markup=await AdminForm.users_ikb()
                                                      )

                    elif data.get("action") == "get_ContactUser":
                        pass

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
                if await state.get_state() == "AdminState:COMMISSION":
                    if message.text.isdigit():
                        CONFIG.COMMISSION = message.text
                        await message.answer(text=f"Комиссия изменена {message.text}",
                                             reply_markup=await AdminForm.payment_setup_ikb())
                        await state.finish()
                    else:
                        await message.answer(text="Доступен ввод только цифр")
                        await AdminState.COMMISSION.set()

                elif await state.get_state() == "AdminState:REQUISITES":
                    if message.text.isdigit():
                        CONFIG.COMMISSION = message.text
                        await message.answer(text=f"Комиссия изменена {message.text}",
                                             reply_markup=await AdminForm.payment_setup_ikb())
                        await state.finish()
                    else:
                        await message.answer(text="Доступен ввод только цифр")
                        await AdminState.REQUISITES.set()

                elif await state.get_state() == "AdminState:CheckNumber":
                    if message.text.isdigit():
                        transaction = await CRUDTransaction.get(transaction=int(message.text))
                        if transaction:
                            approved = "✅ одобрена ✅" if transaction.approved else "❌ не одобрена ❌"

                            text = f"🤝 Сделка № {transaction.id} {approved}\n\n" \
                                   f"📈 Курс покупки: <i>{transaction.exchange_rate}\n</i>" \
                                   f"   ₿  Куплено BTC: <i>{transaction.buy_BTC}\n</i>" \
                                   f"💸 Продано BYN: <i>{transaction.sale_BYN}\n</i>" \
                                   f"👛 Кошелек <i>{transaction.wallet}</i>"
                            if transaction.check != "None":
                                try:
                                    photo = open(f'user_check/{transaction.check}.jpg', 'rb')
                                    await bot.send_photo(chat_id=message.from_user.id, photo=photo,
                                                         caption=f"<i>Сделка пользователя</i>\n\n"
                                                                 f"{text}",
                                                         reply_markup=await AdminForm.check_confirmation_ikb(
                                                             user_id=transaction.user_id,
                                                             page=transaction.id,
                                                             action_back="get_Users",
                                                             action_confirm="get_One_ConfirmPayment")
                                                         )
                                    await state.finish()
                                except FileNotFoundError:
                                    pass
                            else:
                                await message.answer(text=f"<i>Сделка пользователя</i>\n\n"
                                                          f"Пользователь не добавил чек\n\n"
                                                          f"{text}",
                                                     reply_markup=await AdminForm.check_confirmation_ikb(
                                                         user_id=transaction.user_id,
                                                         page=transaction.id,
                                                         action_back="get_Users",
                                                         action_confirm="get_One_ConfirmPayment")
                                                     )
                                await state.finish()
                        else:
                            await message.answer(text="Не найдено",
                                                 reply_markup=await AdminForm.back_ikb(target="Users",
                                                                                       action="get_Users")
                                                 )
                            await state.finish()

                    else:
                        await message.answer(text="Доступен ввод только цифр")
                        await AdminState.CheckNumber.set()

                elif await state.get_state() == "AdminState:UsersId":
                    if message.text.isdigit():
                        user = await CRUDUsers.get(user_id=int(message.text))
                        transaction = await CRUDTransaction.get_all(user_id=user.id)

                        if transaction:
                            approved = "✅ одобрена ✅" if transaction[0].approved else "❌ не одобрена ❌"

                            text = f"🤝 Сделка № {transaction[0].id} {approved}\n\n" \
                                   f"📈 Курс покупки: <i>{transaction[0].exchange_rate}\n</i>" \
                                   f"   ₿  Куплено BTC: <i>{transaction[0].buy_BTC}\n</i>" \
                                   f"💸 Продано BYN: <i>{transaction[0].sale_BYN}\n</i>" \
                                   f"👛 Кошелек <i>{transaction[0].wallet}</i>"

                            await message.answer(text="<i>Сделки пользователя</i>\n\n"
                                                      f"{text}",
                                                 reply_markup=await AdminForm.pagination_transaction_ikb(
                                                     target="Users",
                                                     action="pagination_user_transaction",
                                                     action_back="get_Users",
                                                     user_id=user.id),
                                                 parse_mode="HTML"
                                                 )
                            await state.finish()
                        else:
                            await message.answer(text="Не найдено")
                            await state.finish()
                    else:
                        await message.answer(text="Доступен ввод только цифр")
                        await AdminState.UsersId.set()
