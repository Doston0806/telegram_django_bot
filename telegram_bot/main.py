# telegram_bot/main.py
from telegram.ext import ApplicationBuilder, CommandHandler
from telegram import Bot

TOKEN = "BOT_TOKENINGIZ"  # bot token
bot = Bot(token=TOKEN)

application = ApplicationBuilder().token(TOKEN).build()
dispatcher = application.dispatcher

async def start(update, context):
    await update.message.reply_text("Salom! Webhook ishlayapti.")

dispatcher.add_handler(CommandHandler("start", start))
