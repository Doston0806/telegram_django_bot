import os
import sys
import django
import asyncio
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from handlers import router
from scheduler import start_scheduler

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN topilmadi. .env faylga to‘g‘ri yozilganiga ishonch hosil qiling.")

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

async def main():
    dp.include_router(router)
    start_scheduler()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
