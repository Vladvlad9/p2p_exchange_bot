from aiogram import types
from aiogram.dispatcher import FSMContext

from crud import CRUDUsers
from crud.referralCRUD import CRUDReferral
from crud.walCRUD import CRUDWallet
from handlers.users.CreateWallet import CreateWallet
from keyboards.inline.users.start_ikb import MainForm, main_cb
from loader import dp, bot
from schemas import UserSchema, ReferralSchema, WalletSchema
from states.users.MainState import MainState


@dp.message_handler(commands=["start"], state=MainState.all_states)
async def registration_start_state(message: types.Message, state: FSMContext):
    await state.finish()
    user = await CRUDUsers.get(user_id=message.from_user.id)
    if user:
        await message.delete()
        await message.answer(text="СДЕЛКА ОТМЕНЕНА\n"
                                  "Добро пожаловать\n"
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


@dp.message_handler(commands=["start"])
async def registration_start(message: types.Message):
    user = await CRUDUsers.get(user_id=message.from_user.id)
    if user:
        await message.delete()
        await message.answer(text="Добро пожаловать\n"
                                  "Выберите операцию",
                             reply_markup=await MainForm.start_ikb(message.from_user.id))
    else:
        start_commands = message.text
        referral_id = str(start_commands[7:])
        if str(referral_id) != "":
            if str(referral_id) != str(message.from_user.id):
                current_user = await CRUDUsers.get(user_id=int(referral_id))
                await CRUDUsers.add(user=UserSchema(user_id=message.from_user.id))
                await CRUDReferral.add(referral=ReferralSchema(user_id=current_user.id,
                                                               referral_id=int(referral_id))
                                       )
                try:
                    await bot.send_message(chat_id=int(referral_id),
                                           text="По вашей ссылке зарегистрировался новый пользователь!")
                except Exception:
                    pass
            else:
                await message.answer(text="Нельзя регистрироваться по собственной реферальной ссылке!")
        else:
            await CRUDUsers.add(user=UserSchema(user_id=message.from_user.id))
            get_wallet = await CreateWallet.create_wallet(label=f"{str(message.from_user.id)}71811291")
            if get_wallet:
                address = str(get_wallet['wallet']['address'])
                passphrase = str(get_wallet['wallet']['passphrase'])
                user = await CRUDUsers.get(user_id=message.from_user.id)

                await CRUDWallet.add(wallet=WalletSchema(user_id=user.id,
                                                         address=address,
                                                         passphrase=passphrase)
                                     )
            else:
                pass

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


@dp.message_handler(state=MainState.all_states, content_types=["text", "photo"])
async def process_message(message: types.Message, state: FSMContext = None):
    await MainForm.process_profile(message=message, state=state)