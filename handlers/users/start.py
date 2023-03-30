from aiogram import types
from aiogram.dispatcher import FSMContext
from loguru import logger

from config.config import CONFIGTEXT
from crud import CRUDUsers
from crud.referralCRUD import CRUDReferral
from crud.walCRUD import CRUDWallet
from handlers.users.AllCallbacks import money_cb
from handlers.users.CreateWallet import CreateWallet
from handlers.users.Cryptocurrency import Cryptocurrency
from keyboards import byn_cb
from keyboards.inline.users.money_reload import Money_reload
from keyboards.inline.users.start_ikb import MainForm, main_cb
from loader import dp, bot
from schemas import UserSchema, ReferralSchema, WalletSchema
from states.users.BtcState import BTCState
from states.users.BynState import BynState
from states.users.ReloadState import ReloadState
from states.users.MainState import MainState
from states.users.RubState import RubState

logger.add("debug.log", format="{time} {level} {message}", level="DEBUG", serialize=True)


@dp.message_handler(commands=["start"], state=BynState.all_states)
@dp.message_handler(commands=["start"], state=RubState.all_states)
@dp.message_handler(commands=["start"], state=BTCState.all_states)
@dp.message_handler(commands=["start"], state=ReloadState.all_states)
@dp.message_handler(commands=["start"], state=MainState.all_states)
async def registration_start_state(message: types.Message, state: FSMContext):
    await state.finish()
    user = await CRUDUsers.get(user_id=message.from_user.id)
    if user:
        await message.delete()
        await message.answer(text="СДЕЛКА ОТМЕНЕНА \n"
                                  f"{CONFIGTEXT.MAIN_FORM.TEXT}",
                             reply_markup=await MainForm.start_ikb(message.from_user.id))
    else:
        await message.delete()
        await CRUDUsers.add(user=UserSchema(user_id=message.from_user.id))
        text = CONFIGTEXT.FIRST_PAGE.TEXT
        await message.answer(text=text, reply_markup=await MainForm.proof_ikb(), parse_mode="HTML")


@dp.message_handler(commands=["start"])
async def registration_start(message: types.Message):
    user = await CRUDUsers.get(user_id=message.from_user.id)
    if user:
        await message.delete()
        await message.answer(text=CONFIGTEXT.MAIN_FORM.TEXT,
                             reply_markup=await MainForm.start_ikb(message.from_user.id))
    else:
        start_commands = message.text
        referral_id = str(start_commands[7:])
        if str(referral_id) != "":
            if str(referral_id) != str(message.from_user.id):
                current_user = await CRUDUsers.get(user_id=int(referral_id))
                if current_user:
                    await CRUDUsers.add(user=UserSchema(user_id=message.from_user.id))
                    await CRUDReferral.add(referral=ReferralSchema(user_id=current_user.id,
                                                                   referral_id=int(referral_id))
                                           )
                    try:
                        await bot.send_message(chat_id=int(referral_id),
                                               text="По вашей ссылке зарегистрировался новый пользователь!")
                        get_wallet = await CreateWallet.create_wallet()
                        if get_wallet:
                            address = str(get_wallet['wallet']['address'])
                            wif = str(get_wallet['wallet']['wif'])

                            user = await CRUDUsers.get(user_id=message.from_user.id)

                            await CRUDWallet.add(wallet=WalletSchema(user_id=user.id,
                                                                     address=address,
                                                                     wif=wif)
                                                 )
                            print('wallet added')
                    except Exception:
                        pass
                else:
                    await message.answer(text="Пользователя не найдено")
            else:
                await message.answer(text="Нельзя регистрироваться по собственной реферальной ссылке!")
        else:
            await CRUDUsers.add(user=UserSchema(user_id=message.from_user.id))
            get_wallet = await CreateWallet.create_wallet()
            if get_wallet:
                address = str(get_wallet['wallet']['address'])
                wif = str(get_wallet['wallet']['wif'])

                user = await CRUDUsers.get(user_id=message.from_user.id)

                await CRUDWallet.add(wallet=WalletSchema(user_id=user.id,
                                                         address=address,
                                                         wif=wif)
                                     )
                print('wallet added')
            else:
                pass

        # text = "Правила бота!\n"\
        #        "Условия для совершения сделки по приобретению BTC за BYN.\n"\
        #        "<i>1.  Этапы сделки:</i>\n"\
        #        "     - После подтверждения окончательной суммы у бота Вам будут высланы реквизиты.\n"\
        #        "     - Оплачиваете по данным реквизитам\n"\
        #        "     - Присылаете чек\n"\
        #        "     - Присылаете адрес BTC\n"\
        #        "     - После проверки транзакции отправляю BTC\n"\
        #        "<i>2 . Если Вы перевели деньги и Вам никто не отвечает нажмите кнопку «Оператор»</i>\n"\
        #        "<i>3. Время обработки транзакции  составляет  20 - 90 мин.</i>\n" \
        #        "<i>4. Для новых пользователей могут быть запрошены дополнительно паспортные данные " \
        #        "для подтверждение личности (проверка проводится  1 раз)</i>\n" \
        #        "<i>5. При не выполнении пункта №4  Ваши средства будут храниться 30 дней на счете депонирование до " \
        #        "окончания прохождения проверки личности. В случаи отказа от прохождения верификации; " \
        #        "не до конца пройденной верификации средства будут утеряны безвозвратно по истечении 30 дней.</i>\n\n" \
        #        "Нажав кнопку Подтвердить Вы соглашаетесь со всеми правилами этого бота."

        await message.answer(text=CONFIGTEXT.FIRST_PAGE.TEXT, reply_markup=await MainForm.proof_ikb(), parse_mode="HTML")


@dp.message_handler(commands=['test'])
@logger.catch
async def test(message: types.Message):
    #price_BTC = await Cryptocurrency.get_CryptocurrencyBTC("RUB")
    #await CreateWallet.money_text()
    # a = await Cryptocurrency.get_rub()
    # b = await Cryptocurrency.get_Cryptocurrency("USD")
    # c = a * b
    # print('asd')
    # await CreateWallet.money_text()
    # print('asd')
    #a = 1/0
    pass


@dp.callback_query_handler(main_cb.filter())
@dp.callback_query_handler(main_cb.filter(), state=MainState.all_states)
async def process_callback(callback: types.CallbackQuery, state: FSMContext = None):
    await MainForm.process_profile(callback=callback, state=state)


@dp.message_handler(state=MainState.all_states, content_types=["text", "photo"])
async def process_message(message: types.Message, state: FSMContext = None):
    await MainForm.process_profile(message=message, state=state)


@dp.callback_query_handler(money_cb.filter())
@dp.callback_query_handler(money_cb.filter(), state=ReloadState.all_states)
async def process_callback_Money_reload(callback: types.CallbackQuery, state: FSMContext = None):
    await Money_reload.Money_reload(callback=callback, state=state)


@dp.message_handler(state=ReloadState.all_states, content_types=["text", "photo"])
async def process_Money_reload(message: types.Message, state: FSMContext = None):
    await Money_reload.Money_reload(message=message, state=state)