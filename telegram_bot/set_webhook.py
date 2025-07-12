import asyncio
from aiogram import Bot
from sozlamalar import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)

async def set():
    await bot.set_webhook("https://doston06.pythonanywhere.com/api/bot/")  # domeningiz o'rnatiladi

def set_webhook():
    asyncio.run(set())
