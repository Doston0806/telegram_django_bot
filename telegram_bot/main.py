from telegram_bot.bot_instance import bot, dp
from telegram_bot.handlers import router
from telegram_bot.scheduler import start_scheduler

dp.include_router(router)
start_scheduler()
