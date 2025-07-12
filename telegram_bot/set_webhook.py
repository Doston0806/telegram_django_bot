import requests

BOT_TOKEN = "8060106619:AAFOlQTaga4yDHElHf5YvnZ6-zDPcO1vM94"
WEBHOOK_URL = "https://doston06.pythonanywhere.com/api/bot/"

set_webhook_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"

response = requests.post(set_webhook_url, data={"url": WEBHOOK_URL})

print(response.status_code)
print(response.json())
