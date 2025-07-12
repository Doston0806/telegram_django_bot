
from django.apps import AppConfig
import threading
import logging

class BotappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'botapp'

    def ready(self):
        from telegram_bot.set_webhook import set_webhook
        try:
            threading.Thread(target=set_webhook).start()
        except Exception as e:
            logging.error(f"Webhook o‘rnatishda xatolik: {e}")

