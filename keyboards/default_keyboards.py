from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    """Asosiy menyu tugmalari"""
    keyboard = [
        [
            KeyboardButton(text="🥟 Somsa narxlari"),
            KeyboardButton(text="🐟 Baliq narxlari")
        ],
        [
            KeyboardButton(text="📍 Manzil"),
            KeyboardButton(text="📞 Bog'lanish")
        ],
        [
            KeyboardButton(text="🛒 Buyurtma berish"),
            KeyboardButton(text="ℹ️ Biz haqimizda")
        ]
    ]
    if is_admin:
        keyboard.append([KeyboardButton(text="⚙️ Admin Panel")])

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Bo'limni tanlang..."
    )

def get_contact_keyboard() -> ReplyKeyboardMarkup:
    """Telefon raqamni yuborish tugmasi"""
    keyboard = [
        [KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)],
        [KeyboardButton(text="❌ Bekor qilish")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Tugmani bosing yoki raqamingizni yozing..."
    )

def get_order_type_keyboard() -> ReplyKeyboardMarkup:
    """Buyurtma turini tanlash tugmalari"""
    keyboard = [
        [
            KeyboardButton(text="🚚 Yetkazib berish"),
            KeyboardButton(text="🏪 Olib ketish")
        ],
        [KeyboardButton(text="❌ Bekor qilish")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_location_keyboard() -> ReplyKeyboardMarkup:
    """Manzil/Lokatsiya yuborish tugmasi"""
    keyboard = [
        [KeyboardButton(text="📍 Lokatsiyani yuborish", request_location=True)],
        [KeyboardButton(text="❌ Bekor qilish")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Lokatsiya yuboring yoki manzilni yozing..."
    )

def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Faqat bekor qilish tugmasi"""
    keyboard = [
        [KeyboardButton(text="❌ Bekor qilish")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )
