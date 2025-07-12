# telegram_bot/views/webhook.py
import asyncio
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from telegram_bot.bot import bot, dp
from aiogram.types import Update

@csrf_exempt
def telegram_webhook(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            update = Update.model_validate(data)

            # asyncio.run ishlamaydi WSGIda!
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(dp.feed_update(bot, update))

        except Exception as e:
            return JsonResponse({"ok": False, "error": str(e)})
        return JsonResponse({"ok": True})
    return JsonResponse({"ok": False, "error": "not a POST request"})
