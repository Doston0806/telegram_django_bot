# bot.py
from aiogram import Bot, Dispatcher
from sozlamalar import BOT_TOKEN
from handlers import router

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.include_router(router)
