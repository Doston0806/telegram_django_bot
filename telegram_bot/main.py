import os
import sys
import django
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

# Django va muhit sozlash
load_dotenv()
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# Bot sozlamalari
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN .env faylda topilmadi!")


async def main():
    # Storage va Dispatcher sozlash
    storage = MemoryStorage()
    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=storage)

    # Handlerni ulash (sizning routeringiz)
    from telegram_bot.handlers import router
    dp.include_router(router)

    try:
        # Pollingni boshlash
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Botda xato yuz berdi: {e}")
    finally:
        # Bot to'xtaganda resurslarni tozalash
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())