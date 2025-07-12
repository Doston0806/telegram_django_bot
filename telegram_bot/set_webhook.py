import asyncio
from telegram_bot.main import bot

async def set():
    await bot.set_webhook("https://YOUR_DOMAIN/api/bot/")

asyncio.run(set())
