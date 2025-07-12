import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
from datetime import datetime

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from sozlamalar import BOT_TOKEN
from botapp.models import User  # ← foydalanuvchilar modeli
from aiogram.types import Message

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))



async def send_daily_summary():
    """
    Har kuni soat 22:00 da yuboriladigan xabar.
    """
    users = User.objects.all()
    for user in users:
        try:
            await bot.send_message(user.telegram_id, "🔔 Kun yakuni eslatmasi: Xarajatlaringizni kiritishni unutmang!")
        except Exception as e:
            print(f"Xatolik: {e} foydalanuvchi {user.telegram_id} ga yuborishda")


def start_scheduler():
    scheduler = AsyncIOScheduler(timezone=pytz.timezone("Asia/Tashkent"))
    scheduler.add_job(send_daily_summary, CronTrigger(hour=22, minute=0))
    scheduler.start()
