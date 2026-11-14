import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
DB_PATH = os.getenv("DB_PATH", "mafia.sqlite3")

if not BOT_TOKEN or BOT_TOKEN == "PASTE_YOUR_TELEGRAM_BOT_TOKEN_HERE":
    raise RuntimeError(
        "BOT_TOKEN topilmadi. .env fayl yarating va BotFather tokenini kiriting."
    )
