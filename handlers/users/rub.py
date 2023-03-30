from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards.inline.users.rub import Rub, rub_cb
from loader import dp
from states.users.RubState import RubState


@dp.callback_query_handler(rub_cb.filter())
@dp.callback_query_handler(rub_cb.filter(), state=RubState.all_states)
async def process_rub_callback(callback: types.CallbackQuery, state: FSMContext = None):
    await Rub.process_rub(callback=callback, state=state)


@dp.message_handler(state=RubState.all_states, content_types=["text", "photo"])
async def process_rub_message(message: types.Message, state: FSMContext = None):
    await Rub.process_rub(message=message, state=state)