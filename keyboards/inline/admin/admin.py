from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from aiogram.utils.exceptions import BadRequest

from config import CONFIG
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

