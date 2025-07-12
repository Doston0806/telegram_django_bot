# telegram_bot/set_webhook.py
import asyncio
import os
import sys
from aiogram import Bot

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sozlamalar import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)

async def set_webhook():
    await bot.set_webhook("https://doston06.pythonanywhere.com/api/bot/")

if __name__ == "__main__":
    asyncio.run(set_webhook())
