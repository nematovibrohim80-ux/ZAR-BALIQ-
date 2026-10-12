import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# Admin ID larini ro'yxat ko'rinishida olish
raw_admins = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = []
for admin_id in raw_admins.split(","):
    admin_id = admin_id.strip()
    if admin_id.isdigit():
        ADMIN_IDS.append(int(admin_id))

# Ma'lumotlar bazasi fayli
DB_PATH = BASE_DIR / os.getenv("DB_PATH", "database/uy_vazifa.db")

# AI API kalitlari (ixtiyoriy)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY", "").strip()


def is_admin(user_id: int) -> bool:
    """Foydalanuvchi admin ekanligini tekshirish."""
    return user_id in ADMIN_IDS
