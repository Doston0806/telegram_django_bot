"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Django application
application = get_wsgi_application()

# Botni parallel ishga tushiramiz
import threading
import asyncio

from telegram_bot.main import start_bot

def run_bot():
    asyncio.run(start_bot())

# Bot alohida threadda ishga tushadi
threading.Thread(target=run_bot, daemon=True).start()

