import asyncio
from decimal import Decimal

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import BadRequest, ChatNotFound
from loguru import logger

from config.config import CONFIGTEXT, CONFIG
from crud import CRUDUsers, CRUDTransaction, CRUDCurrency
from crud.walCRUD import CRUDWallet
from handlers.users.AllCallbacks import btc_cb, byn_cb, main_cb, rub_cb
from handlers.users.Cryptocurrency import Cryptocurrency
from loader import bot
from schemas import TransactionSchema
from states.users.BtcState import BTCState


class BtcForm:

    @staticmethod
    async def isfloat(value: str):
        try:
            float(value)
            return True
        except ValueError:
            return False

    @staticmethod
    async def start_MainForm_ikb(user_id: int) -> InlineKeyboardMarkup:
        """
        Клавиатура главного меню
        :param user_id: id пользователя
        :return:
        """

        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="💻 Профиль",
                                         callback_data=main_cb.new("Profile", "get_Profile", 0, user_id))
                ],
                [
                    InlineKeyboardButton(text="BYN 🇧🇾", callback_data=byn_cb.new("Pay", "EnterAmount", 0, user_id)),
                    InlineKeyboardButton(text="RUB 🇷🇺", callback_data=rub_cb.new("Pay", "EnterAmount", 0, user_id)),
                    InlineKeyboardButton(text="BTC ₿", callback_data=btc_cb.new("Pay", "EnterAmount", 0, user_id))
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
                    InlineKeyboardButton(text="◀️ Назад", callback_data=btc_cb.new(target, action, page, user_id))
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
            "ОПЛАТИТЬ BYN 🇧🇾": {"target": "Buy", "action": "PayBTC", "id": "BYN", "editid": user_id},
            "ОПЛАТИТЬ RUB 🇷🇺": {"target": "Buy", "action": "PayBTC", "id": "RUB", "editid": user_id},
        }
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=name, callback_data=btc_cb.new(name_items["target"],
                                                                             name_items["action"],
                                                                             name_items["id"],
                                                                             name_items["editid"]))
                    for name, name_items in data.items()
                ],
                [
                    InlineKeyboardButton(text="◀️ Назад", callback_data=btc_cb.new(target, actionBack, 0, user_id))
                ]
            ]
        )

    @staticmethod
    async def buying_BTC(user_money, message, state):
        price_BYN = await Cryptocurrency.get_byn()
        price_RUB = await Cryptocurrency.get_rub()

        price_BTC = await Cryptocurrency.get_btc()

        bye_byn = round(Decimal(user_money) * Decimal(price_BTC) * Decimal(price_BYN), 2)
        bye_rub = round(Decimal(user_money) * Decimal(price_BTC) * Decimal(price_RUB), 2)

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

        # await state.update_data(exchange_RUB=float(Decimal(price_BTC) * Decimal(price_RUB)))
        await state.update_data(exchange_RUB=float(price_RUB))  # курс руб.
        await state.update_data(exchange_BYN=float(Decimal(price_BTC) * Decimal(price_BYN)))  # курс бел.

        await state.update_data(price_RUB=bye_rub)  # конечная цена которую пользователь получит в руб.
        await state.update_data(price_BYN=bye_byn)  # конечная цена которую пользователь получит в бел.

        await state.update_data(buy_BTC=user_money)  # Сколько пользователь хочет купить BTC

        await message.answer(text=text,
                             reply_markup=await BtcForm.currency_ikb(
                                 user_id=message.from_user.id,
                                 target="MainForm",
                                 actionBack="get_MainForm")
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
                    InlineKeyboardButton(text="Верно 👌", callback_data=btc_cb.new("Buy", "get_requisites", 0, 0)),
                    InlineKeyboardButton(text="Нет ⛔️", callback_data=btc_cb.new("MainForm", "get_MainForm", 0, 0))
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
                    InlineKeyboardButton(text="Я ОПЛАТИЛ ✅", callback_data=btc_cb.new("UserPaid", 0, 0, 0))
                ],
                [
                    InlineKeyboardButton(text="◀️ Назад", callback_data=btc_cb.new("MainForm", "get_MainForm", 0, 0))
                ]
            ]
        )

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
    @logger.catch
    async def process_btc(callback: CallbackQuery = None, message: Message = None, state: FSMContext = None) -> None:
        if callback:
            if callback.data.startswith('btc'):
                data = btc_cb.parse(callback_data=callback.data)

                if data.get("target") == "MainForm":
                    if data.get("action") == "get_MainForm":
                        await state.finish()
                        await callback.message.delete()
                        await callback.message.answer(text=CONFIGTEXT.MAIN_FORM.TEXT,
                                                      reply_markup=await BtcForm.start_MainForm_ikb(
                                                          user_id=callback.from_user.id)
                                                      )

                elif data.get("target") == "Pay":
                    if data.get("action") == "EnterAmount":
                        await callback.message.edit_text(text="Введите сумму в BTC:",
                                                         reply_markup=await BtcForm.back_ikb(
                                                             user_id=callback.from_user.id,
                                                             target="MainForm",
                                                             action="get_MainForm")
                                                         )
                        await BTCState.UserCoin.set()

                elif data.get("target") == "Buy":
                    if data.get("action") == "PayBTC":
                        user = await CRUDUsers.get(user_id=callback.from_user.id)
                        get_wallet = await CRUDWallet.get(user_id=user.id)
                        check_wallet = await Cryptocurrency.Check_Wallet(btc_address=get_wallet.address)

                        if check_wallet:
                            try:
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
                                                                 reply_markup=await BtcForm.CheckOut_wallet_ikb())
                            except KeyError as e:
                                print(e)
                                await callback.message.edit_text(text="У вас вышло время на оплату",
                                                                 reply_markup=await BtcForm.start_MainForm_ikb(
                                                                     user_id=callback.from_user.id)
                                                                 )
                                await state.finish()
                                await callback.message.delete()
                        else:
                            await callback.message.edit_text(text=f"Адрес кошелька <i>{get_wallet.address}</i> "
                                                                  f"нету в blockchain\n\n"
                                                                  f"Желаете еще раз ввести ваш адрес Bitcoin - кошелька",
                                                             reply_markup=await BtcForm.back_ikb(
                                                                 user_id=callback.from_user.id,
                                                                 target="MainForm",
                                                                 action="get_MainForm"),
                                                             parse_mode="HTML"
                                                             )

                    elif data.get("action") == "get_requisites":
                        try:
                            wallet = await state.get_data()

                            text_wallet = f"🚀 На Ваш кошелек  ➡️➡️➡️ <i>{wallet['wallet']}</i>\n" \
                                          f"будет отправлено <i>{wallet['buy_BTC']}</i> BTC. 🚀"
                            if wallet['currency'] == "BYN":
                                await callback.message.edit_text(text=f"{text_wallet}\n\n"
                                                                      f"{CONFIGTEXT.RequisitesBYN.TEXT}",
                                                                 reply_markup=await BtcForm.user_paid_ikb(),
                                                                 parse_mode="HTML"
                                                                 )
                            else:
                                await callback.message.edit_text(text=f"{text_wallet}\n\n"
                                                                      f"{CONFIGTEXT.RequisitesRUS.TEXT}",
                                                                 reply_markup=await BtcForm.user_paid_ikb(),
                                                                 parse_mode="HTML"
                                                                 )
                        except Exception as e:
                            print(e)
                            await callback.message.delete()
                            await state.finish()
                            await callback.message.edit_text(text="У вас вышло время на оплату",
                                                             reply_markup=await BtcForm.start_MainForm_ikb(
                                                                 user_id=callback.from_user.id)
                                                             )

                elif data.get("target") == "UserPaid":
                    await callback.message.edit_text(text="📸 Загрузите изображение подтверждающее оплату!\n"
                                                          "(до 2 Мб)")
                    await BTCState.UserPhoto.set()

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
                if await state.get_state() == "BTCState:UserCoin":
                    money_int = message.text.isdigit()
                    money_float = await BtcForm.isfloat(value=message.text)

                    if money_float or money_int:
                        await BtcForm.buying_BTC(user_money=message.text,
                                                 message=message,
                                                 state=state)
                    else:
                        await message.answer(text="Введите число!")

                elif await state.get_state() == "BTCState:UserPhoto":
                    if message.content_type == "photo":
                        if message.photo[0].file_size > 2000:
                            await message.answer(text="Картинка превышает 2 мб\n"
                                                      "Попробуйте загрузить еще раз")
                            await BTCState.UserPhoto.set()
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

                                text = f"Заявка № {transaction.id}\n\n" \
                                       f"Имя: {message.from_user.first_name}\n" \
                                       f"Курс: {round(get_data['exchange_rate'])} {get_data['currency']}\n" \
                                       f"Получено BTC: {get_data['buy_BTC']}\n" \
                                       f"Нужно отправить {get_data['currency']}: {get_data['sale']}\n" \
                                       f"Кошелёк: {get_data['wallet']}"

                                tasks = []
                                for admin in CONFIG.BOT.ADMINS:
                                    tasks.append(bot.send_photo(chat_id=admin, photo=photo,
                                                                caption=f"Пользователь оплатил!\n\n"
                                                                        f"{text}"))
                                await asyncio.gather(*tasks, return_exceptions=True) # Отправка всем админам сразу

                                await BtcForm.confirmation_timer(message=message)

                            except Exception as e:
                                print(e)
                                await message.answer(text="У вас вышло время на оплату",
                                                     reply_markup=await BtcForm.start_MainForm_ikb(
                                                         user_id=message.from_user.id)
                                                     )
                            await state.finish()
                    else:
                        await message.answer(text="Загрузите картинку")
                        await BTCState.UserPhoto.set()