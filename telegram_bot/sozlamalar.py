import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))
BOT_TOKEN = os.getenv('BOT_TOKEN')

API_URL = "https://doston2006.pythonanywhere.com/api/"
