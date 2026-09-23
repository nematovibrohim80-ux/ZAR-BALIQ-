import html
import re
from datetime import datetime
from zoneinfo import ZoneInfo

def format_price(amount: int | float) -> str:
    """Narxni chiroyli formatda qaytarish: 125000 -> 125 000 so‘m"""
    try:
        val = int(amount)
        formatted = f"{val:,}".replace(",", " ")
        return f"{formatted} so‘m"
    except (ValueError, TypeError):
        return f"{amount} so‘m"

def get_current_time_str() -> str:
    """O'zbekiston (Toshkent) vaqti bo'yicha joriy vaqtni matn ko'rinishida olish"""
    try:
        tz = ZoneInfo("Asia/Tashkent")
        now = datetime.now(tz)
    except Exception:
        now = datetime.now()
    return now.strftime("%d.%m.%Y %H:%M")

def escape_text(text: str | None) -> str:
    """HTML maxsus belgilarini xavfsiz qilish"""
    if text is None:
        return ""
    return html.escape(str(text))

def clean_phone(phone: str) -> str:
    """Telefon raqamini tozalash va to'g'ri formatga keltirish"""
    cleaned = re.sub(r"[^\d+]", "", phone)
    if not cleaned.startswith("+") and cleaned.startswith("998"):
        cleaned = "+" + cleaned
    elif not cleaned.startswith("+") and len(cleaned) == 9:
        cleaned = "+998" + cleaned
    return cleaned

def is_valid_phone(phone: str) -> bool:
    """O'zbekiston telefon raqami formati to'g'riligini tekshirish"""
    cleaned = clean_phone(phone)
    # +998 followed by 9 digits
    return bool(re.match(r"^\+998\d{9}$", cleaned))
