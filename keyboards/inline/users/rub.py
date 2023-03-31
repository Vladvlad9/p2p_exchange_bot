import asyncio
from decimal import Decimal

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import BadRequest
from loguru import logger

from config.config import CONFIGTEXT, CONFIG
from crud import CRUDCurrency, CRUDReferral, CRUDUsers, CRUDTransaction
from crud.transactions_referralsCRUD import CRUDTransactionReferrals
from crud.walCRUD import CRUDWallet
from handlers.users.AllCallbacks import main_cb, byn_cb, rub_cb, btc_cb
from handlers.users.Cryptocurrency import Cryptocurrency
from loader import bot
from schemas import TransactionSchema, UserInDBSchema, TransactionsReferralSchema
from states.users.RubState import RubState


class Rub:
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
                    InlineKeyboardButton(text="◀️ Назад", callback_data=rub_cb.new(target, action, page, user_id))
                ]
            ]
        )

    @staticmethod
    async def send_timer_message(chat_id: int, state):
        await state.finish()
        user = await CRUDUsers.get(user_id=chat_id)
        if user.buy_timer:
            await asyncio.sleep(0)
            user.buy_timer = False
            await CRUDUsers.update(user=user)
            return
        else:
            await bot.send_message(chat_id=chat_id,
                                   text='Время вышло!\n'
                                        f'{CONFIGTEXT.MAIN_FORM.TEXT}',
                                   reply_markup=await Rub.start_MainForm_ikb(chat_id))

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

        user_money: int = int(money)
        if user_money < limit:
            await message.answer(text=f"Минимальная сумма {limit} {currency}\n"
                                      f"Введите сумму в {currency}")
            await RubState.UserCoin.set()
        else:
            price_BTC: float = await Cryptocurrency.get_btc()
            bye: float = round(int(user_money) / price_BTC, 8)

            currency = await CRUDCurrency.get(currency_name=currency)

            percent = round((Decimal(bye) / Decimal(100) * Decimal(CONFIG.COMMISSION.COMMISSION_BOT)), 8)
            percent_referral = round((Decimal(bye) / Decimal(100) * Decimal(CONFIG.COMMISSION.COMMISSION_REFERRAL)), 8)

            get_referral = await CRUDReferral.get(referral_id=message.from_user.id)

            if get_referral:
                await state.update_data(percent_referral=percent_referral)
                await state.update_data(referral_id=get_referral.user_id)  # Сколько получается процентов от суммы
                current_bye = round(Decimal(bye) - Decimal(percent) - Decimal(percent_referral), 8)
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
                   f"{referral_txt}\n"

            await message.answer(text=text,
                                 reply_markup=await Rub.bue_ikb(
                                     user_id=message.from_user.id,
                                     count=bye,
                                     target="MainForm")
                                 )

            await state.update_data(currency_id=currency.id)  # Валюта
            await state.update_data(sale=user_money)  # Сколько пользователь покупает В BYN
            await state.update_data(exchange_rate=price_BTC)  # Курс BTC
            await state.update_data(buy_BTC=current_bye)  # Сколько получается в BTC
            await state.update_data(percent=percent)  # Сколько получается процентов от суммы

            await asyncio.sleep(int(CONFIG.PAYMENT_TIMER))
            await Rub.send_timer_message(chat_id=message.from_user.id, state=state)

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
                    InlineKeyboardButton(text="Купить ✅",
                                         callback_data=rub_cb.new("BuyRUB", "SelectUserWalletBitcoin", count, user_id))
                ],
                [
                    InlineKeyboardButton(text="◀️ Назад", callback_data=rub_cb.new(target, "get_MainForm", 0, user_id))
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
                    InlineKeyboardButton(text="Верно 👌", callback_data=rub_cb.new("BuyRUB", "get_requisites", 0, 0)),
                    InlineKeyboardButton(text="Нет ⛔️", callback_data=rub_cb.new("MainForm", "get_MainForm", 0, 0))
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
                    InlineKeyboardButton(text="Я ОПЛАТИЛ ✅", callback_data=rub_cb.new("UserPaid", 0, 0, 0))
                ],
                [
                    InlineKeyboardButton(text="◀️ Назад", callback_data=rub_cb.new("MainForm", "get_MainForm", 0, 0))
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
    async def process_rub(callback: CallbackQuery = None, message: Message = None, state: FSMContext = None) -> None:
        if callback:
            if callback.data.startswith('rub'):
                data = rub_cb.parse(callback_data=callback.data)

                if data.get("target") == "MainForm":
                    if data.get("action") == "get_MainForm":
                        await state.finish()
                        await callback.message.delete()
                        await callback.message.answer(text=CONFIGTEXT.MAIN_FORM.TEXT,
                                                      reply_markup=await Rub.start_MainForm_ikb(
                                                          user_id=callback.from_user.id)
                                                      )

                elif data.get("target") == "Pay":
                    if data.get("action") == "EnterAmount":
                        rub = await Cryptocurrency.get_rub()
                        btc: float = await Cryptocurrency.get_btc()

                        price = round(Decimal(rub) * Decimal(btc))
                        text: str = "Купить BTC за RUB 🇷🇺\n" \
                                    f"1 Bitcoin ₿ = {price} RUB 🇷🇺\n\n" \
                                    f"<i>Мин. сумма {CONFIG.COMMISSION.MIN_RUB}  RUB</i>"

                        await callback.message.edit_text(text=f"{text}\n\n"
                                                              f"Введите сумму в RUB 🇷🇺:",
                                                         reply_markup=await Rub.back_ikb(
                                                             action="get_MainForm",
                                                             user_id=callback.from_user.id,
                                                             target="MainForm"),
                                                         disable_web_page_preview=True
                                                     )
                        await RubState.UserCoin.set()

                elif data.get('target') == "BuyRUB":
                    if data.get("action") == "SelectUserWalletBitcoin":
                        user = await CRUDUsers.get(user_id=callback.from_user.id)
                        get_wallet = await CRUDWallet.get(user_id=user.id)
                        check_wallet = await Cryptocurrency.Check_Wallet(btc_address=get_wallet.address)

                        if check_wallet:
                            try:
                                get_data_buy = await state.get_data()

                                text = f"Отправляем BTC {get_data_buy['buy_BTC']} ➡️➡️➡\n\n" \
                                       f"Адрес кошелька: {get_wallet.address}\n" \
                                       f"Доступ к вашему кошельку находится в профиле\n\n" \
                                       f"☑️ Проверьте Всё верно?\n" \
                                       f"Если вы ввели неверный адрес кошелька нажмите кнопку " \
                                       f"Нет ⛔️, и начните процедуру заново.️"

                                await state.update_data(wallet=get_wallet.address)
                                await callback.message.edit_text(text=text,
                                                                 reply_markup=await Rub.CheckOut_wallet_ikb())
                            except KeyError as e:
                                print(e)
                                await callback.message.edit_text(text="У вас вышло время на оплату",
                                                                 reply_markup=await Rub.start_MainForm_ikb(
                                                                     user_id=callback.from_user.id)
                                                                 )
                                await state.finish()
                                await callback.message.delete()

                        else:
                            await callback.message.edit_text(text=f"Адрес кошелька <i>{get_wallet.address}</i> "
                                                                  f"нету в blockchain\n",
                                                             reply_markup=await Rub.back_ikb(
                                                                 action="get_MainForm",
                                                                 user_id=callback.from_user.id,
                                                                 target="MainForm"),
                                                             parse_mode="HTML"
                                                             )

                    elif data.get('action') == "get_requisites":
                        try:
                            wallet = await state.get_data()

                            text_wallet = f"🚀 На Ваш кошелек  ➡️➡️➡️ <i>{wallet['wallet']}</i>\n" \
                                          f"будет отправлено <i>{wallet['buy_BTC']}</i> BTC. 🚀"

                            await callback.message.edit_text(text=f"{text_wallet}\n\n"
                                                                  f"{CONFIGTEXT.RequisitesRUS.TEXT}",
                                                             reply_markup=await Rub.user_paid_ikb(),
                                                             parse_mode="HTML"
                                                             )
                        except Exception as e:
                            print(e)
                            await callback.message.delete()
                            await state.finish()
                            await callback.message.edit_text(text="У вас вышло время на оплату",
                                                             reply_markup=await Rub.start_MainForm_ikb(
                                                                 user_id=callback.from_user.id)
                                                             )

                elif data.get('target') == "UserPaid":
                    await callback.message.edit_text(text="📸 Загрузите изображение подтверждающее оплату!\n"
                                                          "(до 2 Мб)")
                    await RubState.UserPhoto.set()

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
                if await state.get_state() == "RubState:UserCoin":
                    money = message.text.isdigit()
                    if money:
                        await Rub.buying_currency(money=message.text,
                                                  currency="RUB",
                                                  limit=CONFIG.COMMISSION.MIN_BYN,
                                                  message=message,
                                                  state=state)

                    else:
                        await message.answer(text="Вы ввели некорректные данные\n"
                                                  "Доступен ввод только цифр или целых чисел!")
                        await RubState.UserCoin.set()

                elif await state.get_state() == "RubState:UserPhoto":
                    if message.content_type == "photo":
                        if message.photo[0].file_size > 2000:
                            await message.answer(text="Картинка превышает 2 мб\n"
                                                      "Попробуйте загрузить еще раз")
                            await RubState.UserPhoto.set()
                        else:
                            get_photo = await bot.get_file(message.photo[len(message.photo) - 1].file_id)
                            photo = message.photo[0].file_id
                            get_data = await state.get_data()
                            user = await CRUDUsers.get(user_id=message.from_user.id)

                            transaction = await CRUDTransaction.add(transaction=TransactionSchema(user_id=user.id,
                                                                                                  operation_id=1,
                                                                                                  **get_data)
                                                                    )
                            #  Если обмен совершил реферал то ему придет уведомление
                            #  Нужно сделать перевод на кошелек
                            if "percent_referral" in get_data:
                                referral_id = await CRUDUsers.get(id=int(get_data['referral_id']))
                                await CRUDTransactionReferrals.add(transaction_referral=TransactionsReferralSchema(
                                    transaction_id=transaction.id,
                                    user_id=message.from_user.id,
                                    referral_id=referral_id.user_id,
                                    percent=float(get_data['percent_referral'])
                                ))
                                await bot.send_message(chat_id=referral_id.user_id,
                                                       text=f"Ваш реферал {message.from_user.id} совершил обмен\n"
                                                            f"Вам начислен процент - {get_data['percent_referral']}")

                            try:
                                await bot.download_file(file_path=get_photo.file_path,
                                                        destination=f'user_check/{transaction.id}_{message.from_user.id}.jpg',
                                                        timeout=12,
                                                        chunk_size=1215000)

                                get_transaction = await CRUDTransaction.get(transaction=transaction.id)
                                get_transaction.check = f'{transaction.id}_{message.from_user.id}'
                                await CRUDTransaction.update(transaction=get_transaction)

                                text = f"Заявка № {transaction.id}\n\n" \
                                       f"Имя {message.from_user.first_name}\n" \
                                       f"Курс: {round(get_data['exchange_rate'])}\n" \
                                       f"Процент от суммы {get_data['percent']}\n" \
                                       f"Получено RUB: {get_data['sale']}\n" \
                                       f"Нужно отправить  BTC: {get_data['buy_BTC']}\n" \
                                       f"Кошелёк: {get_data['wallet']}"

                                tasks = []
                                for admin in CONFIG.BOT.ADMINS:
                                    tasks.append(bot.send_photo(chat_id=admin, photo=photo,
                                                                caption=f"Пользователь оплатил!\n\n"
                                                                        f"{text}"))
                                await asyncio.gather(*tasks, return_exceptions=True)  # Отправка всем админам сразу

                                await Rub.confirmation_timer(message=message)

                                user.transaction_timer = True
                                await CRUDUsers.update(user=user)

                            except Exception as e:
                                print(e)
                                await message.answer(text="У вас вышло время на оплату",
                                                     reply_markup=await Rub.start_MainForm_ikb(
                                                         user_id=message.from_user.id)
                                                     )
                            await state.finish()
                    else:
                        await message.answer(text="Загрузите картинку")
                        await RubState.UserPhoto.set()