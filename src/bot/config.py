# Bot configuration
import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ.get(
    "TELEGRAM_BOT_TOKEN", "8342568470:AAE3D3OkkIb3WnXbRK1XHFWr7hruk3MhXSs"
)
DJANGO_API_URL = os.environ.get("DJANGO_API_URL", "http://localhost:8000/api")
