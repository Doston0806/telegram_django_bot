import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))
BOT_TOKEN = os.getenv('BOT_TOKEN')
API_URL = "https://telegram-django-bot-22vj.onrender.com/api/"

