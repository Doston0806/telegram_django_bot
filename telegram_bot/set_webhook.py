# telegram_bot/set_webhook.py
import asyncio
import os
import sys
from aiogram import Bot

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sozlamalar import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)

async def set_webhook():
    webhook_url = "https://doston06.pythonanywhere.com/api/bot/"
    result = await bot.set_webhook(webhook_url)
    print("Webhook o‘rnatildi:", result)
    await bot.session.close()

if __name__ == "__main__":
    asyncio.run(set_webhook())