import asyncio
import logging
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import bot_main, bot_warn
from middlewares.access import AccessMiddleware
from handlers import get_main_router, get_second_router
from database import init_db

logging.basicConfig(level=logging.INFO)

async def main():
    await init_db()

    dp_main = Dispatcher(storage=MemoryStorage())
    dp_main.message.outer_middleware(AccessMiddleware())
    dp_main.callback_query.outer_middleware(AccessMiddleware())
    dp_main.include_router(get_main_router())

    dp_warn = Dispatcher()
    dp_warn.include_router(get_second_router())
    print("🚀 Bots are pulling their shit to your server \n productet by lxrkii")
    await asyncio.gather(
        dp_main.start_polling(bot_main),
        dp_warn.start_polling(bot_warn)
    )

if __name__ == "__main__":
    asyncio.run(main())