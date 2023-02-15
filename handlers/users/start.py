from aiogram import types
from aiogram.dispatcher import FSMContext

from crud import CRUDUsers
from keyboards.inline.users.start_ikb import MainForm, main_cb
from loader import dp
from schemas import UserSchema
from states.users.MainState import MainState


@dp.message_handler(commands=["start"])
async def registration_start(message: types.Message):
    user = await CRUDUsers.get(user_id=message.from_user.id)
    if user:
        await message.delete()
        await message.answer(text="Добро пожаловать\n"
                                  "Выберите операцию",
                             reply_markup=await MainForm.start_ikb(message.from_user.id))
    else:
        await message.delete()
        await CRUDUsers.add(user=UserSchema(user_id=message.from_user.id))
        text = "Правила бота!\n"\
               "Условия для совершения сделки по приобретению BTC за BYN.\n"\
               "<i>1.  Этапы сделки:</i>\n"\
               "     - После подтверждения окончательной суммы у бота Вам будут высланы реквизиты.\n"\
               "     - Оплачиваете по данным реквизитам\n"\
               "     - Присылаете чек\n"\
               "     - Присылаете адрес BTC\n"\
               "     - После проверки транзакции отправляю BTC\n"\
               "<i>2 . Если Вы перевели деньги и Вам никто не отвечает нажмите кнопку «Оператор»</i>\n"\
               "<i>3. Время обработки транзакции  составляет  20 - 90 мин.</i>\n" \
               "<i>4. Для новых пользователей могут быть запрошены дополнительно паспортные данные " \
               "для подтверждение личности (проверка проводится  1 раз)</i>\n" \
               "<i>5. При не выполнении пункта №4  Ваши средства будут храниться 30 дней на счете депонирование до " \
               "окончания прохождения проверки личности. В случаи отказа от прохождения верификации; " \
               "не до конца пройденной верификации средства будут утеряны безвозвратно по истечении 30 дней.</i>\n\n" \
               "Нажав кнопку Подтвердить Вы соглашаетесь со всеми правилами этого бота."

        await message.answer(text=text, reply_markup=await MainForm.proof_ikb(), parse_mode="HTML")


@dp.callback_query_handler(main_cb.filter())
@dp.callback_query_handler(main_cb.filter(), state=MainState.all_states)
async def process_callback(callback: types.CallbackQuery, state: FSMContext = None):
    await MainForm.process_profile(callback=callback, state=state)


@dp.message_handler(state=MainState.all_states, content_types=["text"])
async def process_message(message: types.Message, state: FSMContext = None):
    await MainForm.process_profile(message=message, state=state)