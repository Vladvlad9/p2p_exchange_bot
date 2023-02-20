from aiogram import types
from aiogram.dispatcher import FSMContext

from filters import IsAdmin
from keyboards.inline.admin.admin import admin_cb, AdminForm
from loader import dp
from states.users.AdminState import AdminState


@dp.message_handler(IsAdmin(), commands=["admin"], state=AdminState.all_states)
async def registration_start_state(message: types.Message, state: FSMContext):
    await state.finish()


@dp.message_handler(IsAdmin(), commands=["admin"])
async def registration_start(message: types.Message):
    await message.answer(text="Админ панель")


@dp.callback_query_handler(admin_cb.filter())
@dp.callback_query_handler(admin_cb.filter(), state=AdminState.all_states)
async def process_admin_callback(callback: types.CallbackQuery, state: FSMContext = None):
    await AdminForm.process_admin_profile(callback=callback, state=state)


@dp.message_handler(state=AdminState.all_states, content_types=["text", "photo"])
async def process_admin_message(message: types.Message, state: FSMContext = None):
    await AdminForm.process_admin_profile(message=message, state=state)