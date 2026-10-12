"""
Ingliz tili va Uy Vazifasi AI boti uchun barcha klaviaturalar (Reply va Inline).
"""

import urllib.parse
from typing import List, Dict, Any, Optional
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

SUBJECT_LIST = [
    ("🇬🇧 Ingliz tili", "sub:english"),
    ("📐 Matematika", "sub:matem"),
    ("⚛️ Fizika", "sub:physics"),
    ("🧪 Kimyo", "sub:chem"),
    ("📚 Ona tili & Adabiyot", "sub:uzbek"),
    ("💻 IT & Dasturlash", "sub:it"),
    ("🌍 Tarix & Geografiya", "sub:history"),
    ("🧬 Biologiya", "sub:bio"),
    ("🌐 Barcha fanlar (Umumiy)", "sub:general"),
]


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Asosiy menyu tugmalari — Ingliz tili fokusli va qulay."""
    keyboard = [
        [
            KeyboardButton(text="🇬🇧 Ingliz tili vazifasi"),
            KeyboardButton(text="📝 Insho / Esse yordamchisi")
        ],
        [
            KeyboardButton(text="📚 Qoidalar & Noto'g'ri fe'llar"),
            KeyboardButton(text="🎯 Grammatika Quizi")
        ],
        [
            KeyboardButton(text="📷 Rasm orqali vazifa yechish"),
            KeyboardButton(text="📚 Boshqa fanlar")
        ],
        [
            KeyboardButton(text="📊 Statistika"),
            KeyboardButton(text="🏆 Reyting"),
            KeyboardButton(text="⚙️ AI Kalit sozlash")
        ],
        [
            KeyboardButton(text="👥 Guruhga qo'shish"),
            KeyboardButton(text="❓ Yordam")
        ]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Inglizcha savol, mashq yoki rasm yuboring..."
    )


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Bekor qilish tugmasi."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Bekor qilish")]],
        resize_keyboard=True
    )


def get_subjects_inline_keyboard() -> InlineKeyboardMarkup:
    """Fanlarni tanlash uchun inline menyu."""
    buttons = []
    row = []
    for title, callback_data in SUBJECT_LIST:
        row.append(InlineKeyboardButton(text=title, callback_data=callback_data))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_solution_inline_keyboard(task_id: int) -> InlineKeyboardMarkup:
    """Yechim chiqqandan keyin yordamchi, audio talaffuz va do'stlarga ulashish tugmalari."""
    share_text = urllib.parse.quote(
        "Ingliz tilidan barcha uy vazifalarimni @uy_vazifa_bot orqali qadamma-qadam va to'g'ri yechyapman! 🇬🇧📚 Sen ham sinab ko'r!"
    )
    share_url = f"https://t.me/share/url?url=https://t.me/uy_vazifa_bot&text={share_text}"

    buttons = [
        [
            InlineKeyboardButton(text="🔊 Talaffuzni eshitish", callback_data=f"voice:{task_id}"),
            InlineKeyboardButton(text="🔄 Oddiyroq tushuntir", callback_data=f"mode:simple:{task_id}")
        ],
        [
            InlineKeyboardButton(text="📋 Qisqa xulosa", callback_data=f"mode:summary:{task_id}"),
            InlineKeyboardButton(text="📤 Do'stlarga ulashish", url=share_url)
        ],
        [
            InlineKeyboardButton(text="✏️ Yangi vazifa yechish", callback_data="act:new_task")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_formulas_keyboard() -> InlineKeyboardMarkup:
    """Foydali formulalar bo'yicha menyu."""
    buttons = [
        [
            InlineKeyboardButton(text="📐 Algebra", callback_data="formula:math_algebra"),
            InlineKeyboardButton(text="📐 Geometriya", callback_data="formula:math_geo")
        ],
        [
            InlineKeyboardButton(text="⚛️ Fizika", callback_data="formula:physics"),
            InlineKeyboardButton(text="🧪 Kimyo", callback_data="formula:chem")
        ],
        [
            InlineKeyboardButton(text="🇬🇧 Ingliz tili zamonlari", callback_data="rule:tenses_simple")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_english_rules_keyboard() -> InlineKeyboardMarkup:
    """Ingliz tili qoidalari va ma'lumotnomalari menyusi."""
    buttons = [
        [
            InlineKeyboardButton(text="⏱ Simple Zamonlar", callback_data="rule:tenses_simple"),
            InlineKeyboardButton(text="🔄 Continuous Zamonlar", callback_data="rule:tenses_continuous")
        ],
        [
            InlineKeyboardButton(text="✨ Perfect Zamonlar", callback_data="rule:tenses_perfect"),
            InlineKeyboardButton(text="🏗 Passive Voice", callback_data="rule:passive_voice")
        ],
        [
            InlineKeyboardButton(text="🔀 Conditionals (If...)", callback_data="rule:conditionals"),
            InlineKeyboardButton(text="📍 Predloglar (in/on/at)", callback_data="rule:prepositions")
        ],
        [
            InlineKeyboardButton(text="🅰️ Artikllar (A/AN/THE)", callback_data="rule:articles"),
            InlineKeyboardButton(text="📖 Noto'g'ri fe'llar ro'yxati", callback_data="irreg_page:1")
        ],
        [
            InlineKeyboardButton(text="🔍 Noto'g'ri fe'l qidirish", callback_data="act:search_irreg")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_irregular_pagination_keyboard(current_page: int, total_pages: int) -> InlineKeyboardMarkup:
    """Noto'g'ri fe'llar ro'yxatini varaqlash tugmalari."""
    nav_row = []
    if current_page > 1:
        nav_row.append(InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"irreg_page:{current_page - 1}"))
    
    nav_row.append(InlineKeyboardButton(text=f"📄 {current_page}/{total_pages}", callback_data="noop"))
    
    if current_page < total_pages:
        nav_row.append(InlineKeyboardButton(text="Keyingi ➡️", callback_data=f"irreg_page:{current_page + 1}"))

    return InlineKeyboardMarkup(inline_keyboard=[
        nav_row,
        [
            InlineKeyboardButton(text="🔍 Fe'l qidirish", callback_data="act:search_irreg"),
            InlineKeyboardButton(text="⬅️ Qoidalarga qaytish", callback_data="act:back_rules")
        ]
    ])


def get_quiz_keyboard(quiz_id: int) -> InlineKeyboardMarkup:
    """Grammatika testi uchun variantlar."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🅰️ Variant A", callback_data=f"quiz_ans:{quiz_id}:A"),
            InlineKeyboardButton(text="🅱️ Variant B", callback_data=f"quiz_ans:{quiz_id}:B")
        ],
        [
            InlineKeyboardButton(text="🅲 Variant C", callback_data=f"quiz_ans:{quiz_id}:C"),
            InlineKeyboardButton(text="🅳 Variant D", callback_data=f"quiz_ans:{quiz_id}:D")
        ],
        [
            InlineKeyboardButton(text="⏭ Boshqa savol", callback_data="quiz_next")
        ]
    ])


def get_share_inline_keyboard() -> InlineKeyboardMarkup:
    """Do'stlarga ulashish va guruhga qo'shish."""
    share_text = urllib.parse.quote(
        "Ingliz tilidan uy vazifalarini, grammatika va insholarni mukammal yechib beruvchi bot: @uy_vazifa_bot 🇬🇧📚"
    )
    share_url = f"https://t.me/share/url?url=https://t.me/uy_vazifa_bot&text={share_text}"
    add_group_url = "https://t.me/uy_vazifa_bot?startgroup=true"

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Botni Guruhga Qo'shish", url=add_group_url)],
        [InlineKeyboardButton(text="📤 Sinfdoshlarga yuborish", url=share_url)]
    ])


def get_history_keyboard(current_page: int, total_pages: int, tasks: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """Tarix ro'yxati."""
    buttons = []
    for task in tasks:
        subj = task.get("subject", "Vazifa")
        q_preview = task.get("question", "")[:25].replace("\n", " ")
        btn_text = f"#{task['id']} {subj}: {q_preview}..."
        buttons.append([InlineKeyboardButton(text=btn_text, callback_data=f"view_task:{task['id']}")])

    nav_row = []
    if current_page > 1:
        nav_row.append(InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"hist_page:{current_page - 1}"))
    nav_row.append(InlineKeyboardButton(text=f"📄 {current_page}/{max(1, total_pages)}", callback_data="noop"))
    if current_page < total_pages:
        nav_row.append(InlineKeyboardButton(text="Keyingi ➡️", callback_data=f"hist_page:{current_page + 1}"))

    buttons.append(nav_row)
    buttons.append([InlineKeyboardButton(text="🗑 Tarixni tozalash", callback_data="clear_history_prompt")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_task_detail_keyboard(task_id: int, back_page: int = 1) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Ro'yxatga qaytish", callback_data=f"hist_page:{back_page}")]
    ])


def get_clear_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔴 Ha, barchasini o'chirish", callback_data="clear_history_confirm"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="hist_page:1")
        ]
    ])
