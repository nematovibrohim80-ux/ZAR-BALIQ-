"""
Matematika Boti uchun Telegram tugmalari (O'zbek tilida).
"""

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

def get_math_main_keyboard() -> ReplyKeyboardMarkup:
    """Asosiy menyu klaviaturasi."""
    keyboard = [
        [
            KeyboardButton(text="🧮 Ifodalar / Kalkulyator"),
            KeyboardButton(text="📐 Tenglamani Yechish")
        ],
        [
            KeyboardButton(text="📊 Kvadrat Tenglama (D)"),
            KeyboardButton(text="🔢 Kasrlar bilan Amallar")
        ],
        [
            KeyboardButton(text="📈 Hosila va Integral"),
            KeyboardButton(text="📐 Geometriya Hisoblagich")
        ],
        [
            KeyboardButton(text="📖 Matematika Shpargalkasi"),
            KeyboardButton(text="❓ Yordam & Misollar")
        ]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="Misol yoki tenglamani yuboring..."
    )


def get_formulas_inline_keyboard() -> InlineKeyboardMarkup:
    """Formulalar va shpargalka menyusi."""
    buttons = [
        [
            InlineKeyboardButton(text="📐 Qisqa Ko'paytirish Formulalari", callback_data="formula_short_mult"),
        ],
        [
            InlineKeyboardButton(text="📊 Kvadrat Tenglama & Viet", callback_data="formula_quadratic"),
            InlineKeyboardButton(text="🔺 Geometriya Yuzalari", callback_data="formula_geometry"),
        ],
        [
            InlineKeyboardButton(text="🌐 Trigonometriya Formulalari", callback_data="formula_trig"),
            InlineKeyboardButton(text="📈 Hosila & Integral Qoidalari", callback_data="formula_calculus"),
        ],
        [
            InlineKeyboardButton(text="💡 Misollar bilan sinab ko'rish", callback_data="show_math_examples")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_examples_inline_keyboard() -> InlineKeyboardMarkup:
    """Tezkor sinab ko'rish uchun tayyor misollar."""
    buttons = [
        [
            InlineKeyboardButton(text="Misol 1: 2x + 8 = 20", callback_data="ex_linear"),
            InlineKeyboardButton(text="Misol 2: x² - 5x + 6 = 0", callback_data="ex_quad"),
        ],
        [
            InlineKeyboardButton(text="Misol 3: 3/4 + 5/6 - 1/2", callback_data="ex_fraction"),
            InlineKeyboardButton(text="Misol 4: (x + 3)²", callback_data="ex_expand"),
        ],
        [
            InlineKeyboardButton(text="Misol 5: Hosila 3x³ - 5x²", callback_data="ex_derivative"),
            InlineKeyboardButton(text="Misol 6: Integral 3x² + 4x", callback_data="ex_integral"),
        ],
        [
            InlineKeyboardButton(text="🔄 Asosiy Menyu", callback_data="back_to_menu")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_solution_action_keyboard(math_text: str = "") -> InlineKeyboardMarkup:
    """Yechim ostidagi qo'shimcha amallar tugmalari."""
    buttons = [
        [
            InlineKeyboardButton(text="📖 Formulalar", callback_data="open_formulas"),
            InlineKeyboardButton(text="💡 Boshqa misol", callback_data="show_math_examples")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
