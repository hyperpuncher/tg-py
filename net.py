import os

import httpx

BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"
BOT_FILE_URL = f"https://api.telegram.org/file/bot{BOT_TOKEN}/"


timeout = httpx.Timeout(timeout=5, connect=2, read=120)
tg_client = httpx.AsyncClient(base_url=BOT_URL, timeout=timeout)
