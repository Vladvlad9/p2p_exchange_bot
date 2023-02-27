import random

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import BadRequest

from crud import CRUDTransaction, CRUDCurrency, CRUDUsers
from handlers.users.AllCallbacks import admin_cb, user_cb
from handlers.users.TransactionHandler import TransactionHandler
from loader import bot
from states.admins.AdminState import AdminState


class Users:

    @staticmethod
    async def Transaction_Confirmation(data: dict, message, check_number=False):

        try:
            get_user_id = int(data['id'])
            get_page_id = int(data['page'])
            user = await CRUDUsers.get(id=get_user_id)

            if check_number:
                transaction = await CRUDTransaction.get(transaction=get_page_id)
                currency = await CRUDCurrency.get(currency_id=transaction.currency_id)

                transaction.approved = True
                await CRUDTransaction.update(transaction=transaction)
                text = f"✅ Вам потвердили сделку № {transaction.id} ✅\n\n" \
                       f"📈 Курс покупки: <i>{transaction.exchange_rate}\n</i>" \
                       f"   ₿  Куплено BTC: <i>{transaction.buy_BTC}\n</i>" \
                       f"💸 Продано {currency.name}: <i>{transaction.sale}\n</i>" \
                       f"👛 Кошелек <i>{transaction.wallet}</i>"

                await bot.send_message(chat_id=user.user_id, text=text)

                await message.answer(text="Вы успешно потвердили сделку")
            else:
                transaction = await CRUDTransaction.get_all(user_id=user.id)
                currency = await CRUDCurrency.get(currency_id=transaction[get_page_id].currency_id)

                transaction[get_page_id].approved = True
                await CRUDTransaction.update(transaction=transaction[get_page_id])
                text = f"✅ Вам потвердили сделку № {transaction[get_page_id].id} ✅\n\n" \
                       f"📈 Курс покупки: <i>{transaction[get_page_id].exchange_rate}\n</i>" \
                       f"   ₿  Куплено BTC: <i>{transaction[get_page_id].buy_BTC}\n</i>" \
                       f"💸 Продано {currency.name}: <i>{transaction[get_page_id].sale}\n</i>" \
                       f"👛 Кошелек <i>{transaction[get_page_id].wallet}</i>"

                await bot.send_message(chat_id=user.user_id, text=text)

                await message.answer(text="Вы успешно потвердили сделку")

        except Exception as e:
            print(e)

    @staticmethod
    async def captch():
        numb_1 = random.randint(1, 10)
        numb_2 = random.randint(1, 10)

        itog = numb_1 + numb_2

        return numb_1, numb_2, itog

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
    async def check_confirmation_ikb(target: str,
                                     user_id: int,
                                     page: int = 0,
                                     action_back: str = None,
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

        data = {
            "✅ Потвердить Оплату": {
                "target": target,
                "action": action_confirm,
                "pagination": "get_ApproveCheck",
                "id": user_id,
                "editid": page
            },

            "◀️ Назад": {
                "target": target, "action": action_back, "pagination": "", "id": page, "editid": user_id},
        }

        return InlineKeyboardMarkup(
            inline_keyboard=[
                                [
                                    InlineKeyboardButton(text="📲 Связаться", url=button_url)
                                ]

                            ] + [
                                [
                                    InlineKeyboardButton(text=name, callback_data=user_cb.new(name_items["target"],
                                                                                              name_items["action"],
                                                                                              name_items["pagination"],
                                                                                              name_items["id"],
                                                                                              name_items["editid"])
                                                         )
                                ] for name, name_items in data.items()
                            ]
        )

    @staticmethod
    async def users_ikb() -> InlineKeyboardMarkup:
        approved_transaction = list(filter(lambda x: x.approved, await CRUDTransaction.get_all()))
        not_approved_transaction = list(filter(lambda x: x.approved == False, await CRUDTransaction.get_all()))
        """
        Клавиатура главного меню админ панели

        :return:
        """
        data = {
            "#️⃣ Номер чека": {
                "target": "UsersCheck",
                "action": "get_CheckNumber",
                "pagination": "",
                "id": 0,
                "editid": 0
            },

            "🆔 id Пользователя": {
                "target": "UsersId",
                "action": "get_UsersId",
                "pagination": "",
                "id": 0,
                "editid": 0
            },

            f"✅ Одобренные ({len(approved_transaction)})": {
                "target": "UsersApproved",
                "action": "get_Approved",
                "pagination": "",
                "id": "Yes",
                "editid": 0
            },

            f"❌ Неодобренные ({len(not_approved_transaction)})": {
                "target": "UsersNoApproved",
                "action": "get_Approved",
                "pagination": "",
                "id": "No",
                "editid": 0
            },

            "◀️ Назад": {
                "target": "StartMenu",
                "action": "",
                "pagination": "",
                "id": 0,
                "editid": 0
            },
        }

        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=name, callback_data=user_cb.new(name_items["target"],
                                                                              name_items["action"],
                                                                              name_items["pagination"],
                                                                              name_items["id"],
                                                                              name_items["editid"]))
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

        back_ikb = InlineKeyboardButton("◀️ Назад", callback_data=user_cb.new("UsersId", action_back, 0, 0, user_id))
        prev_page_ikb = InlineKeyboardButton("←", callback_data=user_cb.new(target, action, 0, prev_page, user_id))
        check = InlineKeyboardButton("☰", callback_data=user_cb.new("UsersId",
                                                                    "get_check_transaction", 0, page, user_id))
        page = InlineKeyboardButton(f"{str(page + 1)}/{str(orders_count)}",
                                    callback_data=user_cb.new("", "", 0, 0, 0))
        next_page_ikb = InlineKeyboardButton("→", callback_data=user_cb.new(target, action, 0, next_page, user_id))

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

                if data.get("target") == "Users":

                    if data.get("action") == "get_Users":
                        try:
                            await callback.message.edit_text(text="Найти пользователя",
                                                             reply_markup=await Users.users_ikb())
                        except BadRequest:
                            await callback.message.delete()
                            await callback.message.answer(text="Найти пользователя",
                                                          reply_markup=await Users.users_ikb())

            elif callback.data.startswith('user'):
                data = user_cb.parse(callback_data=callback.data)

                if data.get("target") == "UsersCheck":
                    if data.get("action") == "get_Users":
                        try:
                            await callback.message.edit_text(text="Найти пользователя",
                                                             reply_markup=await Users.users_ikb())
                        except BadRequest:
                            await callback.message.delete()
                            await callback.message.answer(text="Найти пользователя",
                                                          reply_markup=await Users.users_ikb())

                    # Потвердить оплату
                    if data.get("pagination") == "get_ApproveCheck":
                        captcha = await Users.captch()
                        try:
                            await callback.message.edit_text(
                                text="Вы уверены, что готовы перевести средства?\n\n"
                                     f"Введите результат {captcha[0]} + {captcha[1]}")

                            await state.update_data(captcha=captcha[2])

                            await AdminState.CAPTCHA.set()
                        except Exception as e:
                            print(e)
                            await callback.message.delete()
                            await callback.message.answer(text="Вы уверены, что готовы перевести средства?\n\n"
                                                               f"Введите результат {captcha[0]} + {captcha[1]}")
                            await state.update_data(captcha=captcha[2])
                            await AdminState.CAPTCHA.set()

                    # Поиск по номеру чека
                    elif data.get("action") == "get_CheckNumber":
                        await callback.message.edit_text(text="Введите номер чек",
                                                         reply_markup=await Users.back_ikb(target="Users",
                                                                                           action="get_Users")
                                                         )
                        await AdminState.CheckNumber.set()

                elif data.get("target") == "UsersId":

                    # Поиск по id
                    if data.get("action") == "get_UsersId":
                        await callback.message.edit_text(text="Введите id Пользователя",
                                                         reply_markup=await Users.back_ikb(target="Users",
                                                                                           action="get_Users")
                                                         )
                        await AdminState.UsersId.set()

                    # Пагинация
                    elif data.get("action") == "pagination_user_transaction":
                        page = int(data.get('id'))
                        get_user_id = int(data.get('editId'))

                        user = await CRUDUsers.get(id=get_user_id)
                        transaction = await CRUDTransaction.get_all(user_id=user.id)
                        currency = await CRUDCurrency.get(currency_id=transaction[page].currency_id)

                        if transaction:

                            approved = "✅ одобрена ✅" if transaction[page].approved else "❌ не одобрена ❌"

                            text = f"🤝 Сделка № {transaction[page].id} {approved}\n\n" \
                                   f"📈 Курс покупки: <i>{transaction[page].exchange_rate}\n</i>" \
                                   f"   ₿  Куплено BTC: <i>{transaction[page].buy_BTC}\n</i>" \
                                   f"💸 Продано {currency.name}: <i>{transaction[page].sale}\n</i>" \
                                   f"👛 Кошелек <i>{transaction[page].wallet}</i>"
                            try:
                                await callback.message.edit_text(text=f"<i>Сделки пользователя</i>\n\n"
                                                                      f"{text}",
                                                                 reply_markup=await Users.pagination_transaction_ikb(
                                                                     user_id=user.id,
                                                                     page=page,
                                                                     target="UsersId",
                                                                     action="pagination_user_transaction",
                                                                     action_back="get_Users"),
                                                                 parse_mode="HTML"
                                                                 )
                            except BadRequest:
                                await callback.message.delete()
                                await callback.message.answer(text=f"<i>Сделки Пользователя</i>\n\n"
                                                                   f"{text}",
                                                              reply_markup=await Users.pagination_transaction_ikb(
                                                                  user_id=user.id,
                                                                  page=page,
                                                                  target="UsersId",
                                                                  action="pagination_user_transaction",
                                                                  action_back="get_Users"),
                                                              parse_mode="HTML"
                                                              )
                        else:
                            await callback.message.edit_text(text="Пользователь не совершал сделок 😞",
                                                             reply_markup=await Users.back_ikb(
                                                                 target="UsersId",
                                                                 action="get_Users")
                                                             )

                    # Бургер меню
                    elif data.get("action") == "get_check_transaction":
                        page = int(data.get('id'))
                        get_user_id = int(data.get('editId'))

                        user = await CRUDUsers.get(id=get_user_id)
                        transaction = await CRUDTransaction.get_all(user_id=user.id)

                        if transaction:
                            approved = "✅ одобрена ✅" if transaction[page].approved else "❌ не одобрена ❌"
                            currency = await CRUDCurrency.get(currency_id=transaction[page].currency_id)

                            text = f"🤝 Сделка № {transaction[page].id} {approved}\n\n" \
                                   f"📈 Курс покупки: <i>{transaction[page].exchange_rate}\n</i>" \
                                   f"   ₿  Куплено BTC: <i>{transaction[page].buy_BTC}\n</i>" \
                                   f"💸 Продано {currency.name}: <i>{transaction[page].sale}\n</i>" \
                                   f"👛 Кошелек <i>{transaction[page].wallet}</i>"

                            await state.update_data(id=get_user_id)
                            await state.update_data(page=page)
                            await state.update_data(check_number=False)

                            if transaction[page].check != "None":
                                try:
                                    await callback.message.delete()
                                    photo = open(f'user_check/{transaction[page].check}.jpg', 'rb')
                                    await bot.send_photo(chat_id=callback.from_user.id, photo=photo,
                                                         caption=f"<i>Сделка пользователя</i>\n\n"
                                                                 f"{text}",
                                                         reply_markup=await Users.check_confirmation_ikb(
                                                             page=page,
                                                             user_id=user.id,
                                                             target="UsersId",
                                                             action_back="pagination_user_transaction",
                                                             action_confirm="Confirmation_Transaction")
                                                         )
                                except FileNotFoundError:
                                    pass
                            else:
                                await callback.message.edit_text(text=f"<i>Сделка пользователя</i>\n\n"
                                                                      f"Пользователь не добавил чек\n\n"
                                                                      f"{text}",
                                                                 reply_markup=await Users.check_confirmation_ikb(
                                                                     page=page,
                                                                     user_id=user.id,
                                                                     target="UsersId",
                                                                     action_back="pagination_user_transaction",
                                                                     action_confirm="Confirmation_Transaction")
                                                                 )
                        else:
                            await callback.message.edit_text(text="Не найдено",
                                                             reply_markup=await Users.back_ikb(target="Users",
                                                                                               action="get_Users")
                                                             )

                    # Потверждение оплаты
                    elif data.get("action") == "Confirmation_Transaction":
                        captcha = await Users.captch()
                        try:
                            await callback.message.edit_text(text="Вы уверены, что готовы перевести средства?\n\n"
                                                                  f"Введите результат {captcha[0]} + {captcha[1]}")
                            await state.update_data(captcha=captcha[2])

                            await AdminState.CAPTCHA.set()
                        except Exception as e:
                            print(e)
                            await callback.message.delete()
                            await callback.message.answer(text="Вы уверены, что готовы перевести средства?\n\n"
                                                               f"Введите результат {captcha[0]} + {captcha[1]}")
                            await state.update_data(captcha=captcha[2])
                            await AdminState.CAPTCHA.set()

                elif data.get("target") == "UsersApproved":

                    if data.get("action") == "get_Approved":
                        pass

        if message:
            try:
                await bot.delete_message(
                    chat_id=message.from_user.id,
                    message_id=message.message_id - 1
                )
            except BadRequest:
                pass

            if state:
                # Ввод номера чека
                if await state.get_state() == "AdminState:CheckNumber":
                    if message.text.isdigit():
                        transaction = await CRUDTransaction.get(transaction=int(message.text))
                        if transaction:
                            approved = "✅ одобрена ✅" if transaction.approved else "❌ не одобрена ❌"
                            currency = await CRUDCurrency.get(currency_id=transaction.currency_id)

                            text = f"🤝 Сделка № {transaction.id} {approved}\n\n" \
                                   f"📈 Курс покупки: <i>{transaction.exchange_rate}\n</i>" \
                                   f"   ₿  Куплено BTC: <i>{transaction.buy_BTC}\n</i>" \
                                   f"💸 Продано {currency.name}: <i>{transaction.sale}\n</i>" \
                                   f"👛 Кошелек <i>{transaction.wallet}</i>"
                            if transaction.check != "None":
                                try:
                                    photo = open(f'user_check/{transaction.check}.jpg', 'rb')
                                    await bot.send_photo(chat_id=message.from_user.id, photo=photo,
                                                         caption=f"<i>Сделка пользователя</i>\n\n"
                                                                 f"{text}",
                                                         reply_markup=await Users.check_confirmation_ikb(
                                                             user_id=transaction.user_id,
                                                             page=transaction.id,
                                                             target="UsersCheck",
                                                             action_back="get_Users",
                                                             action_confirm="'")
                                                         )
                                    await state.finish()

                                    await state.update_data(id=transaction.user_id)
                                    await state.update_data(page=transaction.id)
                                    await state.update_data(check_number=True)

                                except FileNotFoundError:
                                    pass
                            else:
                                await message.answer(text=f"<i>Сделка пользователя</i>\n\n"
                                                          f"Пользователь не добавил чек\n\n"
                                                          f"{text}",
                                                     reply_markup=await Users.check_confirmation_ikb(
                                                         user_id=transaction.user_id,
                                                         page=transaction.id,
                                                         target="UsersCheck",
                                                         action_back="get_Users",
                                                         action_confirm="")
                                                     )
                                await state.finish()
                        else:
                            await message.answer(text="Не найдено",
                                                 reply_markup=await Users.back_ikb(target="Users",
                                                                                   action="get_Users")
                                                 )
                            await state.finish()

                elif await state.get_state() == "AdminState:CAPTCHA":
                    get_captcha = await state.get_data()
                    if message.text == str(get_captcha["captcha"]):
                        await Users.Transaction_Confirmation(data=get_captcha,
                                                             message=message,
                                                             check_number=get_captcha["check_number"])
                        await state.finish()
                    else:
                        captcha = await Users.captch()
                        await message.answer(text="Неверно!\n\n"
                                                  f"Введите результат {captcha[0]} + {captcha[1]}")
                        await AdminState.CAPTCHA.set()

                elif await state.get_state() == "AdminState:UsersId":
                    if message.text.isdigit():
                        user = await CRUDUsers.get(user_id=int(message.text))
                        if user:
                            transaction = await CRUDTransaction.get_all(user_id=user.id)

                            if transaction:
                                approved = "✅ одобрена ✅" if transaction[0].approved else "❌ не одобрена ❌"
                                currency = await CRUDCurrency.get(currency_id=transaction[0].currency_id)

                                text = f"🤝 Сделка № {transaction[0].id} {approved}\n\n" \
                                       f"📈 Курс покупки: <i>{transaction[0].exchange_rate}\n</i>" \
                                       f"   ₿  Куплено BTC: <i>{transaction[0].buy_BTC}\n</i>" \
                                       f"💸 Продано {currency.name}: <i>{transaction[0].sale}\n</i>" \
                                       f"👛 Кошелек <i>{transaction[0].wallet}</i>"

                                await message.answer(text="<i>Сделки пользователя</i>\n\n"
                                                          f"{text}",
                                                     reply_markup=await Users.pagination_transaction_ikb(
                                                         target="UsersId",
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
                            await message.answer(text="Не найдено")
                            await state.finish()
                    else:
                        await message.answer(text="Доступен ввод только цифр")
                        await AdminState.UsersId.set()
