# scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Inline tugmalar
keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📝 Bugungi xarajatlar", callback_data="view_today")],
    [InlineKeyboardButton(text="💸 Bugungi qarzlar", callback_data="view_debts")],
])

# Bu funksiya soat 22:00 da ishlaydi
async def send_nightly_reminder(bot: Bot):
    # Foydalanuvchi IDlarini shu yerdan olasiz (bu oddiy usulda - realda bazadan olish kerak)
    user_ids = [7801349824]  # vaqtincha sinov uchun qo'lda yoziladi

    for user_id in user_ids:
        try:
            await bot.send_message(
                chat_id=user_id,
                text="📢 Bugungi xarajatlaringizni kiritishni unutmang!",
                reply_markup=keyboard
            )
        except Exception as e:
            print(f"❌ {user_id} ga yuborib bo‘lmadi: {e}")

# Scheduler ni ishga tushurish
def start_scheduler(bot: Bot):
    scheduler = AsyncIOScheduler(timezone="Asia/Tashkent")
    scheduler.add_job(send_nightly_reminder, "cron", hour=5, minute=6, args=[bot])
    scheduler.start()
