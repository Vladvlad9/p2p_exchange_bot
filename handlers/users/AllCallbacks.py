from aiogram.utils.callback_data import CallbackData

admin_cb = CallbackData("admin", "target", "action", "id", "editId")
user_cb = CallbackData("user", "target", "action", "pagination", "id", "editId")