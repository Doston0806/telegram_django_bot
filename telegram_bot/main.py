# telegram_bot/main.py
import os
import django
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from telegram_bot.handlers import router

import sys
from aiohttp import web

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = Bot(token=BOT_TOKEN, default=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(router)

async def on_startup(bot: Bot):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(bot: Bot):
    await bot.delete_webhook()

async def start_webhook(request):
    # Bu endpoint faqat POST request uchun
    return await SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        handle_in_background=False,
    ).handler(request)

# Django URLConf orqali start_webhook view sifatida ishlatiladi
