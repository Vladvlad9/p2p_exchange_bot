import logging

from utils.set_bot_commands import set_default_commands
logging.basicConfig(level=logging.INFO)


async def on_startup(_):
    await set_default_commands(dp)


if __name__ == '__main__':
    from aiogram import executor
    from handlers import dp

    executor.start_polling(dp, skip_updates=False, on_startup=on_startup)
