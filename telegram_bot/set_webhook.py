# telegram_bot/set_webhook.py
import asyncio
from aiogram import Bot
from sozlamalar import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)

async def set_webhook():
    await bot.set_webhook("https://doston06.pythonanywhere.com/api/bot/")

if __name__ == "__main__":
    asyncio.run(set_webhook())
