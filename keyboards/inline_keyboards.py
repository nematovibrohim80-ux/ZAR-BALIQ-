from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.helpers import format_price

def get_somsa_page_keyboard(phone: str = "33-355-87-77") -> InlineKeyboardMarkup:
    """Somsa menyusi sahifasidagi tugmalar"""
    keyboard = [
        [InlineKeyboardButton(text="🛒 Somsa buyurtma berish", callback_data="order_cat_somsa")],
        [InlineKeyboardButton(text=f"📞 Aloqa: {phone}", callback_data="show_phone_direct")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_fish_page_keyboard(phone: str = "33-355-87-77") -> InlineKeyboardMarkup:
    """Baliq menyusi sahifasidagi tugmalar"""
    keyboard = [
        [InlineKeyboardButton(text="🛒 Baliq buyurtma berish", callback_data="order_cat_baliq")],
        [InlineKeyboardButton(text=f"📞 Aloqa: {phone}", callback_data="show_phone_direct")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_location_inline_keyboard(phone: str = "33-355-87-77", lat: float = 39.0558, lon: float = 66.8286) -> InlineKeyboardMarkup:
    """Manzil xaritasi va aloqa tugmalari"""
    keyboard = [
        [
            InlineKeyboardButton(text="🗺 Yandex Xarita", url=f"https://yandex.com/maps/?pt={lon},{lat}&z=16&l=map"),
            InlineKeyboardButton(text="🗺 Google Maps", url=f"https://www.google.com/maps?q={lat},{lon}")
        ],
        [
            InlineKeyboardButton(text=f"📞 Aloqa: {phone}", callback_data="show_phone_direct")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_product_pick_keyboard(products: list) -> InlineKeyboardMarkup:
    """Buyurtma berish uchun mahsulotni tanlash tugmalari"""
    keyboard = []
    for p in products:
        keyboard.append([
            InlineKeyboardButton(
                text=f"{p['name']} — {format_price(p['price_unit'])}",
                callback_data=f"order_prod_{p['id']}"
            )
        ])
    keyboard.append([InlineKeyboardButton(text="❌ Bekor qilish", callback_data="order_cancel")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_group_keyboard(group_url: str) -> InlineKeyboardMarkup:
    """Telegram guruhiga o'tish tugmasi"""
    url = group_url if group_url.startswith("http") else f"https://{group_url}"
    keyboard = [
        [InlineKeyboardButton(text="👥 Guruhga qo'shilish", url=url)]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_phone_keyboard(phone: str) -> InlineKeyboardMarkup:
    """Telefon va buyurtma tugmalari"""
    keyboard = [
        [InlineKeyboardButton(text="🛒 Buyurtma berish", callback_data="start_order_direct")],
        [InlineKeyboardButton(text="📍 Manzilimiz", callback_data="show_location_direct")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_quantity_keyboard(quantity: int, unit_price: int) -> InlineKeyboardMarkup:
    """Miqdorni tanlash uchun interaktiv tugmalar"""
    total_item_price = quantity * unit_price
    keyboard = [
        # Tezkor tanlash
        [
            InlineKeyboardButton(text="1 dona", callback_data="qty_set_1"),
            InlineKeyboardButton(text="2 dona", callback_data="qty_set_2"),
            InlineKeyboardButton(text="5 dona", callback_data="qty_set_5"),
            InlineKeyboardButton(text="10 dona", callback_data="qty_set_10"),
        ],
        # Kamaytirish va oshirish
        [
            InlineKeyboardButton(text="➖ 1 dona", callback_data="qty_minus"),
            InlineKeyboardButton(text=f"🔢 {quantity} dona", callback_data="qty_current"),
            InlineKeyboardButton(text="➕ 1 dona", callback_data="qty_plus"),
        ],
        # Davom etish tugmasi (jami narx ko'rinadi)
        [
            InlineKeyboardButton(
                text=f"✅ Davom etish ({format_price(total_item_price)})",
                callback_data="qty_continue"
            )
        ],
        [
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="order_cancel")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_order_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Buyurtmani tasdiqlash tugmalari"""
    keyboard = [
        [
            InlineKeyboardButton(text="✅ Buyurtmani tasdiqlash", callback_data="confirm_order_yes")
        ],
        [
            InlineKeyboardButton(text="✏️ O‘zgartirish", callback_data="order_restart"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="order_cancel")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_admin_order_keyboard(order_id: int, customer_phone: str, user_id: int) -> InlineKeyboardMarkup:
    """Admin uchun yangi buyurtma kelganda boshqaruv tugmalari"""
    cleaned_phone = customer_phone.replace(" ", "")
    keyboard = [
        [
            InlineKeyboardButton(text="✅ Qabul qilish", callback_data=f"adm_accept_{order_id}"),
            InlineKeyboardButton(text="❌ Rad etish", callback_data=f"adm_reject_{order_id}")
        ],
        [
            InlineKeyboardButton(text="👤 Telegram profili", url=f"tg://user?id={user_id}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_admin_main_keyboard() -> InlineKeyboardMarkup:
    """Admin asosiy paneli tugmalari"""
    keyboard = [
        [
            InlineKeyboardButton(text="📦 Mahsulotlar", callback_data="adm_products"),
            InlineKeyboardButton(text="📋 Buyurtmalar", callback_data="adm_orders")
        ],
        [
            InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="adm_settings"),
            InlineKeyboardButton(text="📢 Reklama tarqatish", callback_data="adm_broadcast")
        ],
        [
            InlineKeyboardButton(text="📊 Statistika", callback_data="adm_stats")
        ],
        [
            InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="adm_close")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_admin_products_keyboard(products: list) -> InlineKeyboardMarkup:
    """Admin mahsulotlar ro'yxati tugmalari"""
    keyboard = [
        [InlineKeyboardButton(text="➕ Yangi mahsulot qo‘shish", callback_data="adm_add_product")]
    ]
    for p in products:
        status = "🟢" if p.get("is_active", 1) else "🔴"
        keyboard.append([
            InlineKeyboardButton(
                text=f"{status} {p['name']} — {format_price(p['price_unit'])}",
                callback_data=f"adm_edit_prod_{p['id']}"
            )
        ])
    keyboard.append([InlineKeyboardButton(text="🔙 Admin menyuga", callback_data="adm_back_main")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_admin_product_edit_keyboard(product_id: int, is_active: int) -> InlineKeyboardMarkup:
    """Muayyan mahsulotni tahrirlash tugmalari"""
    status_text = "🔴 Faolsizlantirish" if is_active else "🟢 Faollashtirish"
    keyboard = [
        [InlineKeyboardButton(text="💰 Narxni o'zgartirish", callback_data=f"adm_ch_price_{product_id}")],
        [InlineKeyboardButton(text="📝 Nomini o'zgartirish", callback_data=f"adm_ch_name_{product_id}")],
        [InlineKeyboardButton(text="🖼 Rasmni almashtirish", callback_data=f"adm_ch_photo_{product_id}")],
        [InlineKeyboardButton(text=status_text, callback_data=f"adm_toggle_prod_{product_id}")],
        [InlineKeyboardButton(text="🔙 Mahsulotlarga qaytish", callback_data="adm_products")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_admin_settings_keyboard() -> InlineKeyboardMarkup:
    """Sozlamalar menyusi tugmalari"""
    keyboard = [
        [InlineKeyboardButton(text="📞 Telefon raqamini o'zgartirish", callback_data="adm_set_phone")],
        [InlineKeyboardButton(text="👥 Telegram guruh linkini o'zgartirish", callback_data="adm_set_group")],
        [InlineKeyboardButton(text="🚚 Yetkazib berish narxini o'zgartirish", callback_data="adm_set_delivery")],
        [InlineKeyboardButton(text="🔙 Admin menyuga", callback_data="adm_back_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_admin_back_keyboard(callback_data: str = "adm_back_main") -> InlineKeyboardMarkup:
    """Ortga qaytish inline tugmasi"""
    keyboard = [
        [InlineKeyboardButton(text="🔙 Ortga", callback_data=callback_data)]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
