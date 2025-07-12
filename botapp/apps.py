from django.apps import AppConfig
import asyncio
import threading

class BotappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'botapp'

    def ready(self):
        from telegram_bot.main import main
        def start():
            asyncio.run(main())
        threading.Thread(target=start).start()
