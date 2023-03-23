from decimal import Decimal

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import BadRequest

from config import CONFIG
from crud import CRUDCurrency, CRUDUsers, CRUDTransaction
from crud.walCRUD import CRUDWallet
from handlers.users.AllCallbacks import money_cb, main_cb
from handlers.users.Cryptocurrency import Cryptocurrency
from loader import bot
from schemas import TransactionSchema
from states.users.MainState import MainState
from states.users.ReloadState import ReloadState


class Money_reload:

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
                                                         callback_data=main_cb.new("Profile", "get_Profile", 0,
                                                                                   user_id)
                                                         )
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
    async def isfloat(value: str):
        try:
            float(value)
            return True
        except ValueError:
            return False

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
                    InlineKeyboardButton(text="◀️ Назад", callback_data=money_cb.new(target, action, page, user_id))
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
            "ОПЛАТИТЬ BYN 🇧🇾": {"target": "Pay", "action": "get_Currency", "id": "BYN", "editid": user_id},
            "ОПЛАТИТЬ RUB 🇷🇺": {"target": "Pay", "action": "get_Currency", "id": "RUB", "editid": user_id},
        }
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=name, callback_data=money_cb.new(name_items["target"],
                                                                               name_items["action"],
                                                                               name_items["id"],
                                                                               name_items["editid"])
                                         )
                    for name, name_items in data.items()
                ],
                [
                    InlineKeyboardButton(text="◀️ Назад", callback_data=money_cb.new("Pay", "get_reenter", 0, user_id))
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
                    InlineKeyboardButton(text="Верно 👌", callback_data=money_cb.new("Pay", "get_requisites", 0, 0)),
                    InlineKeyboardButton(text="Нет ⛔️", callback_data=money_cb.new("Pay", "get_reenter", 0, 0))
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
                    InlineKeyboardButton(text="Я ОПЛАТИЛ ✅", callback_data=money_cb.new("UserPaid", 0, 0, 0))
                ],
                [
                    InlineKeyboardButton(text="◀️ Назад", callback_data=money_cb.new("Buy", "get_reenter", 0, 0))
                ]
            ]
        )

    @staticmethod
    async def Money_reload(callback: CallbackQuery = None, message: Message = None, state: FSMContext = None) -> None:

        if callback:
            if callback.data.startswith('money'):
                data = money_cb.parse(callback_data=callback.data)

                if data.get('target') == "get_Profile":
                    if data.get('action') == "money_reload":
                        await callback.message.delete()
                        await callback.message.answer(text="Введите количество BTC которое хотите купить",
                                                      reply_markup=await Money_reload.back_ikb(
                                                          user_id=callback.from_user.id,
                                                          target="Pay",
                                                          action="get_reenter",
                                                          page=0)
                                                      )
                        await ReloadState.ReloadMoney.set()

                    elif data.get('action') == "Profile":
                        pass

                if data.get('target') == "Pay":
                    if data.get('action') == "get_Currency":
                        currency = data.get("id")
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

                        user = await CRUDUsers.get(user_id=callback.from_user.id)
                        get_wallet = await CRUDWallet.get(user_id=user.id)
                        check_wallet = await Cryptocurrency.Check_Wallet(btc_address=get_wallet.address)

                        try:
                            get_btc = await state.get_data()
                            text = f"Отправляем BTC {get_btc['buy_BTC']} ➡️➡️➡\n\n" \
                                   f"Необходимо оплатить {get_btc['sale']} {get_btc['currency']}\n\n" \
                                   f"Адрес кошелька: {get_wallet.address}\n\n" \
                                   f"☑️ Проверьте Всё верно?\n" \
                                   f"Если вы ввели неверный адрес кошелька нажмите кнопку " \
                                   f"Нет ⛔️, и начните процедуру заново.️"

                            await state.update_data(wallet=get_wallet.address)
                            await callback.message.edit_text(text=text,
                                                             reply_markup=await Money_reload.CheckOut_wallet_ikb())
                        except KeyError as e:
                            print(e)
                            await callback.message.edit_text(text="У вас вышло время на оплату",
                                                             reply_markup=await Money_reload.start_ikb(
                                                                 user_id=callback.from_user.id)
                                                             )
                            await callback.message.delete()

                    elif data.get('action') == "get_requisites":
                        try:
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
                                                             reply_markup=await Money_reload.user_paid_ikb(),
                                                             parse_mode="HTML"
                                                             )
                        except Exception as e:
                            print(e)
                            await callback.message.delete()
                            await callback.message.edit_text(text="У вас вышло время на оплату",
                                                             reply_markup=await Money_reload.start_ikb(
                                                                 user_id=callback.from_user.id)
                                                             )

                    elif data.get('action') == "get_reenter":
                        await state.finish()
                        await callback.message.edit_text(text="Сделака отменена!\n"
                                                              "Инструкция:\n"
                                                              "1. Выберите валюту в которой будем считать\n"
                                                              "2. Введите сумму (в Сообщении) \n"
                                                              "3. Прочитайте и нажмите кнопку  ОПЛАТИТЬ✅ \n"
                                                              "4. После оплаты нажмите кнопку Я ОПЛАТИЛ✅\n"
                                                              "5. Загрузите изображение подтверждающее оплату\n"
                                                              "6. Введите адрес bitcoin кошелька (в Сообщении)\n"
                                                              "7. Проверьте ваши данные и подтвердите их\n"
                                                              "Выберите валюту в которой будем считать:",
                                                         reply_markup=await Money_reload.start_ikb(
                                                             user_id=callback.from_user.id
                                                         ))

                # Загрузка картинки с потввержением об оплате
                elif data.get("target") == "UserPaid":
                    await callback.message.edit_text(text="📸 Загрузите изображение подтверждающее оплату!\n"
                                                          "(до 2 Мб)")
                    await ReloadState.UserPhoto.set()

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
                if await state.get_state() == "ReloadState:ReloadMoney":
                    get_float = await Money_reload.isfloat(message.text)
                    if get_float:
                        price_BTC = await Cryptocurrency.get_Cryptocurrency(currency="USD")
                        rub = float(await Cryptocurrency.get_rub())
                        usd_to_byn = await Cryptocurrency.get_usd()
                        user_coin = Decimal(message.text)

                        bye_byn = round(user_coin * Decimal(usd_to_byn) * Decimal(price_BTC), 3)
                        bye_rub = round(user_coin * Decimal(rub) * Decimal(price_BTC), 3)

                        await state.update_data(buy_BTC=message.text)
                        await state.update_data(exchange_BYN=Decimal(price_BTC) * Decimal(usd_to_byn))
                        await state.update_data(exchange_RUB=Decimal(price_BTC) * Decimal(rub))
                        await state.update_data(price_BYN=bye_byn)
                        await state.update_data(price_RUB=bye_rub)

                        text = f"📈 Текущая цена Bitcoin: {price_BTC}$\n" \
                               f"📢 Внимание! Текущая цена покупки зафиксирована!\n" \
                               f"Нажав кнопку ОПЛАТИТЬ✅ необходимо " \
                               f"оплатить счет в течении ⏱{CONFIG.PAYMENT_TIMER / 60} минут!\n\n" \
                               f"🧾 Сумма к оплате: 🇧🇾 {bye_byn} BYN\n\n" \
                               f"🧾 Сумма к оплате: 🇷🇺 {bye_rub} RUB\n\n" \
                               f"➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                               f"Вы получите BTC: {Decimal(message.text)}\n" \
                               f"➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                               f"ПЕРЕЙТИ К ОПЛАТЕ?"

                        await message.answer(text=text,
                                             reply_markup=await Money_reload.currency_ikb(
                                                 user_id=message.from_user.id,
                                                 target="get_MainForm",
                                                 actionBack="MainForm")
                                             )
                    else:
                        await message.answer(text="Введено некоректно число\n"
                                                  "Попробуйте еще раз")
                        await MainState.ReloadMoney.set()

                elif await state.get_state() == "ReloadState:UserPhoto":
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
                                                                                                  operation_id=3,
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
                                           f"Курс: {round(get_data['exchange_rate'], 3)} {get_data['currency']}\n" \
                                           f"Пополнить кошелек на {get_data['buy_BTC']} BTC\n" \
                                           f"Нужно отправить {get_data['currency']}: {get_data['sale']}\n" \
                                           f"Кошелёк: {get_data['wallet']}"
                                else:
                                    text = f"Заявка № {transaction.id}\n\n" \
                                           f"Курс: {get_data['exchange_rate']}\n" \
                                           f"Получено {get_data['currency']}: {get_data['sale']}\n" \
                                           f"Нужно отправить  BTC: {get_data['buy_BTC']}\n" \
                                           f"Кошелёк: {get_data['wallet']}"

                                for admin in CONFIG.BOT.ADMINS:
                                    await bot.send_photo(chat_id=admin, photo=photo,
                                                         caption=f"Пользователь {message.from_user.id} "
                                                                 f"хочет пополнить кошелек\n\n"
                                                                 f"{text}")

                                #await MainForm.confirmation_timer(message=message)

                            except Exception as e:
                                print(e)

                                await message.answer(text="У вас вышло время на оплату",
                                                     reply_markup=await Money_reload.start_ikb(user_id=message.from_user.id)
                                                     )
                            await state.finish()
                    else:
                        await message.answer(text="Загрузите картинку")
                        await MainState.UserPhoto.set()