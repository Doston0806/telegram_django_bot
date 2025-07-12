
from aiogram import Bot, Dispatcher
from sozlamalar import BOT_TOKEN
from telegram_bot.handlers import router
from telegram_bot.scheduler import start_scheduler

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.include_router(router)

start_scheduler()
