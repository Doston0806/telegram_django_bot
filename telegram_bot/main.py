# telegram_bot/main.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import router
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
if BOT_TOKEN :

    print("BOT_TOKEN:", BOT_TOKEN)


if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN environment variable topilmadi!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(router)

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
