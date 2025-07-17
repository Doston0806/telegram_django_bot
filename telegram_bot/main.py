import os
import sys
import django
import asyncio
from dotenv import load_dotenv

# .env faylni yuklab olamiz
load_dotenv()

# Django'ni sozlash
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Aiogram kutubxonalarini yuklaymiz
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# Bot tokenini olamiz
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN topilmadi. .env faylga to‘g‘ri yozilganiga ishonch hosil qiling.")

# Botni yaratamiz (parse_mode endi default orqali beriladi!)
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

# Dispatcher
dp = Dispatcher()

# Router va scheduler
from telegram_bot.handlers import router
from telegram_bot.scheduler import start_scheduler

# Botni ishga tushiruvchi asinxron funksiya
async def start_bot():
    dp.include_router(router)
    start_scheduler()
    await dp.start_polling(bot)
