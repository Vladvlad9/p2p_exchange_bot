from aiogram import types
from aiogram.dispatcher import FSMContext

from handlers.users.AllCallbacks import btc_cb
from keyboards.inline.users.btc import BtcForm
from loader import dp
from states.users.BtcState import BTCState


@dp.callback_query_handler(btc_cb.filter())
@dp.callback_query_handler(btc_cb.filter(), state=BTCState.all_states)
async def process_btc_callback(callback: types.CallbackQuery, state: FSMContext = None):
    await BtcForm.process_btc(callback=callback, state=state)


@dp.message_handler(state=BTCState.all_states, content_types=["text", "photo"])
async def process_btc_message(message: types.Message, state: FSMContext = None):
    await BtcForm.process_btc(message=message, state=state)