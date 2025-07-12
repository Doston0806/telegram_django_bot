import asyncio
from aiogram import Bot

BOT_TOKEN = "8060106619:AAFOlQTaga4yDHElHf5YvnZ6-zDPcO1vM94"


bot = Bot(token=BOT_TOKEN)

async def set_webhook():
    url = "https://doston06.pythonanywhere.com/bot/"
    result = await bot.set_webhook(url)
    print("Webhook o‘rnatildi:", result)
    await bot.session.close()

if __name__ == "__main__":
    asyncio.run(set_webhook())
