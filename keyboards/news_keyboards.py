"""
Dunyo Yangiliklari boti uchun sodda va qulay tugmalar.
"""

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from typing import List
from services.news_service import NewsItem


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Asosiy menyu (Reply Keyboard)."""
    buttons = [
        [KeyboardButton(text="🌍 Dunyo yangiliklari"), KeyboardButton(text="🇺🇿 O'zbekiston")],
        [KeyboardButton(text="⚡️ Qaynoq xabarlar"), KeyboardButton(text="📂 Kategoriyalar")],
        [KeyboardButton(text="🔍 Qidiruv"), KeyboardButton(text="ℹ️ Bot haqida")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder="Kerakli bo'limni tanlang..."
    )


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Amalni bekor qilish tugmasi."""
    buttons = [
        [KeyboardButton(text="❌ Bekor qilish")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def get_categories_keyboard() -> InlineKeyboardMarkup:
    """Kategoriyalarni tanlash inline menyusi."""
    buttons = [
        [InlineKeyboardButton(text="🌐 Jahon va Siyosat", callback_data="cat_world")],
        [InlineKeyboardButton(text="💻 Texnologiya va IT", callback_data="cat_tech")],
        [InlineKeyboardButton(text="💰 Iqtisodiyot va Moliya", callback_data="cat_economy")],
        [InlineKeyboardButton(text="⚽️ Sport olami", callback_data="cat_sport")],
        [InlineKeyboardButton(text="🇺🇿 Jamiyat & O'zbekiston", callback_data="cat_uzb")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_news_list_keyboard(items: List[NewsItem], category_code: str) -> InlineKeyboardMarkup:
    """Yangiliklar ro'yxati ostidagi raqamli tugmalar va yangilash."""
    num_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    row_buttons = []

    for idx, item in enumerate(items[:5]):
        label = num_emojis[idx] if idx < len(num_emojis) else f"#{idx+1}"
        row_buttons.append(
            InlineKeyboardButton(text=label, callback_data=f"view_{item.id}")
        )

    inline_keyboard = [row_buttons] if row_buttons else []
    inline_keyboard.append([
        InlineKeyboardButton(text="🔄 Yangilash", callback_data=f"refresh_{category_code}")
    ])
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def get_news_detail_keyboard(link: str, category_code: str = "world") -> InlineKeyboardMarkup:
    """Bitta yangilikning batafsil kartochkasi uchun tugmalar."""
    buttons = [
        [InlineKeyboardButton(text="📖 Saytda to'liq o'qish", url=link)],
        [InlineKeyboardButton(text="🔙 Ro'yxatga qaytish", callback_data=f"cat_{category_code}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
