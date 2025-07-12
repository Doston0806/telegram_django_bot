import json
import asyncio
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from telegram_bot.bot import bot, dp
from aiogram.types import Update

from asgiref.sync import async_to_sync

@csrf_exempt
def telegram_webhook(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            update = Update.model_validate(data)
            loop = asyncio.get_event_loop()
            loop.create_task(dp.feed_update(bot, update))

        except Exception as e:
            return JsonResponse({"ok": False, "error": str(e)})
        return JsonResponse({"ok": True})
    return JsonResponse({"ok": False, "error": "not a POST request"})