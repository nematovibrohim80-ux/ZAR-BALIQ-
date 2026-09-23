import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# Admin ID larini ro'yxat ko'rinishida olish
raw_admins = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = []
for admin_id in raw_admins.split(","):
    admin_id = admin_id.strip()
    if admin_id.isdigit():
        ADMIN_IDS.append(int(admin_id))

TELEGRAM_GROUP_LINK = os.getenv("TELEGRAM_GROUP_LINK", "BU_YERGA_GURUH_LINKI").strip()
PHONE_NUMBER = os.getenv("PHONE_NUMBER", "33-355-87-77").strip()
ADDRESS_TEXT = os.getenv(
    "ADDRESS_TEXT",
    "Qashqadaryo viloyati, Shahrisabz tumani, Shamaton mahallasi (\"ZAR BALIQ\" choyxonasi)"
).strip()
LOCATION_LAT = float(os.getenv("LOCATION_LAT", "39.0558"))
LOCATION_LON = float(os.getenv("LOCATION_LON", "66.8286"))
DEFAULT_DELIVERY_PRICE = int(os.getenv("DEFAULT_DELIVERY_PRICE", "20000"))
DB_PATH = BASE_DIR / os.getenv("DB_PATH", "database/zarbaliq.db")

def is_admin(user_id: int) -> bool:
    """Foydalanuvchi admin ekanligini tekshirish"""
    return user_id in ADMIN_IDS
