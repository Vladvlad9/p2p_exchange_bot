from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards.inline.users.byn import byn_cb, Byn
from loader import dp
from states.users.BynState import BynState


@dp.callback_query_handler(byn_cb.filter())
@dp.callback_query_handler(byn_cb.filter(), state=BynState.all_states)
async def process_byn_callback(callback: types.CallbackQuery, state: FSMContext = None):
    await Byn.process_byn(callback=callback, state=state)


@dp.message_handler(state=BynState.all_states, content_types=["text", "photo"])
async def process_byn_message(message: types.Message, state: FSMContext = None):
    await Byn.process_byn(message=message, state=state)