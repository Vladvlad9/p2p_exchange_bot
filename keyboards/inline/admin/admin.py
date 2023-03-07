from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from aiogram.utils.exceptions import BadRequest

from config import CONFIG
from crud import CRUDUsers
from handlers.users.AllCallbacks import admin_cb
from loader import bot
from states.admins.AdminState import AdminState


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
    async def newsletter_ikb() -> InlineKeyboardMarkup:
        """
        Клавиатура главного меню админ панели
        :return:
        """
        data = {"🏞 Картинка": {"target": "Newsletter", "action": "get_Picture", "id": 0, "editid": 0},
                "🗒 Текст": {"target": "Newsletter", "action": "get_Text", "id": 0, "editid": 0},
                "🏞 Картинка + Текст 🗒": {"target": "Newsletter", "action": "get_PicTex", "id": 1, "editid": 0},
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
                                                         reply_markup=await AdminForm.change_ikb(
                                                             get_change="COMMISSION")
                                                         )

                    elif data.get("action") == "get_Settlement_Account":
                        await callback.message.edit_text(text=f"Расчётный счёт <i>{CONFIG.PAYMENT.REQUISITES}</i>",
                                                         reply_markup=await AdminForm.change_ikb(
                                                             get_change="REQUISITES"),
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

                elif data.get("target") == "Newsletter":
                    await state.finish()

                    if data.get("action") == "get_Newsletter":
                        text = "Вы можете выделять текст жирным шрифтом или курсивом, добавлять стиль кода или " \
                               "гиперссылки для лучшей визуализации важной информации.\n\n" \
                               "Список поддерживаемых тегов:\n" \
                               "b<b> текст </b>/b - Выделяет текст жирным шрифтом\n" \
                               "i<i> текст </i>/i - Выделяет текст курсивом\n" \
                               "u<u> текст </u>/u - Выделяет текст подчеркиванием\n" \
                               "s<s> текст </s>/s - Добавляет зачеркивание текста\n" \
                               "tg-spoiler<tg-spoiler> текст </tg-spoiler>/tg-spoiler - Добавляет защиту от спойлера, " \
                               "которая скрывает выделенный текст\n" \
                               "<a href='http://www.tg.com/'>текст</a> - Создает гиперссылку на выделенный текст"
                        await callback.message.edit_text(text=f"{text}",
                                                         reply_markup=await AdminForm.newsletter_ikb())
                        # await AdminState.Newsletter.set()

                    elif data.get('action') == "get_Picture":
                        id = data.get('id')
                        await state.update_data(id=id)
                        await callback.message.edit_text(text="Выберите картинку!",
                                                         reply_markup=await AdminForm.back_ikb(
                                                             target="Newsletter",
                                                             action="get_Newsletter")
                                                         )
                        await AdminState.NewsletterPhoto.set()

                    elif data.get('action') == "get_Text":
                        id = data.get('id')
                        await state.update_data(id=id)
                        await callback.message.edit_text(text="Введите текст, так же можете его отформатировать",
                                                         reply_markup=await AdminForm.back_ikb(
                                                             target="Newsletter",
                                                             action="get_Newsletter")
                                                         )
                        await AdminState.NewsletterText.set()

                    elif data.get('action') == "get_PicTex":
                        id = data.get('id')
                        await state.update_data(id=id)
                        await callback.message.edit_text(text="Введите текст!",
                                                         reply_markup=await AdminForm.back_ikb(
                                                             target="Newsletter",
                                                             action="get_Newsletter")
                                                         )
                        await AdminState.NewsletterText.set()

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

                elif await state.get_state() == "AdminState:NewsletterText":
                    try:
                        get_state = await state.get_data()
                        if int(get_state['id']) == 1:
                            await message.answer(text="Выберите картинку")
                            await state.update_data(caption=message.text)
                            await AdminState.NewsletterPhoto.set()
                        else:
                            users = await CRUDUsers.get_all()
                            for user in users:
                                await bot.send_message(text=message.text,
                                                       chat_id=user.user_id,
                                                       parse_mode="HTML")

                            await state.finish()
                    except Exception as e:
                        print(e)

                elif await state.get_state() == "AdminState:NewsletterPhoto":
                    if message.content_type == "photo":
                        try:
                            state_id = await state.get_data()
                            users = await CRUDUsers.get_all()
                            if int(state_id['id']) == 1:
                                for user in users:
                                    await bot.send_photo(chat_id=user.user_id,
                                                         caption=state_id['caption'],
                                                         photo=message.photo[2].file_id)
                            else:
                                for user in users:
                                    await bot.send_photo(chat_id=user.user_id,
                                                         photo=message.photo[2].file_id)

                        except Exception as e:
                            print(e)

                        await state.finish()
                        await message.answer(text="Рассылка картинки прошла успешно",
                                             reply_markup=await AdminForm.start_ikb()
                                             )
                    else:
                        await message.answer(text="Это не картинка!\n"
                                                  "Попробуйте еще раз",
                                             reply_markup=await AdminForm.back_ikb(
                                                 target="Newsletter",
                                                 action="get_Newsletter")
                                             )
                        await AdminState.NewsletterPhoto.set()


