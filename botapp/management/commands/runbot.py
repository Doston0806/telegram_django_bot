import asyncio
import nest_asyncio
from django.core.management.base import BaseCommand
from botapp.apps import main

nest_asyncio.apply()

class Command(BaseCommand):
    help = 'Telegram botni ishga tushuradi'

    def handle(self, *args, **kwargs):
        asyncio.run(main())


import multiprocessing
import os
import time
import asyncio
from django.core.management import call_command

async def start_bot():
    from botapp.apps import main as bot_main
    await bot_main()

def run_server():
    os.system("python manage.py runserver")

if __name__ == '__main__':
    # Saytni boshqa processda ishga tushiramiz
    p = multiprocessing.Process(target=run_server)
    p.start()

    # Botni asyncio orqali ishga tushuramiz
    asyncio.run(start_bot())
