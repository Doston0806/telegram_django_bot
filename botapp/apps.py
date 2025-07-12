from django.apps import AppConfig

class BotappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'botapp'

    def ready(self):
        from telegram_bot.set_webhook import set_webhook
        set_webhook()
