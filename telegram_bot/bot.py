from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from sozlamalar import BOT_TOKEN
from telegram_bot.handlers import router

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(router)
