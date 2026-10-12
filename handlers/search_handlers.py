"""
Yangiliklarni kalit so'z bo'yicha qidirish handlerlari.
"""

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from states.news_states import SearchStates
from services.news_service import news_service
from keyboards.news_keyboards import (
    get_cancel_keyboard,
    get_main_keyboard,
    get_news_list_keyboard
)
from utils.formatters import format_news_list

router = Router()


@router.message(lambda msg: msg.text and msg.text.strip().lower() in ["🔍 qidiruv", "qidiruv", "qidirish", "izlash", "search"])
@router.message(Command("search"))
async def start_search(message: Message, state: FSMContext):
    """Qidiruv rejimini yoqish."""
    await state.set_state(SearchStates.waiting_for_query)
    prompt_text = (
        "🔍 <b>Yangiliklarni qidirish:</b>\n\n"
        "O'zingizni qiziqtirgan mavzu yoki kalit so'zni yozing.\n"
        "<i>Masalan: AQSH, Eron, Sun'iy intellekt, Neft, Futbol, Apple</i>\n\n"
        "Jarayonni to'xtatish uchun '❌ Bekor qilish' tugmasini bosing."
    )
    await message.answer(prompt_text, reply_markup=get_cancel_keyboard(), parse_mode="HTML")


@router.message(SearchStates.waiting_for_query)
async def process_search_query(message: Message, state: FSMContext):
    """Foydalanuvchi kiritgan so'z bo'yicha yangiliklarni topish."""
    query = (message.text or "").strip()

    if query == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Qidiruv bekor qilindi.", reply_markup=get_main_keyboard())
        return

    if len(query) < 2:
        await message.answer(
            "⚠️ Qidiruv so'zi kamida 2 ta harfdan iborat bo'lishi kerak. Iltimos, qaytadan kiriting:",
            reply_markup=get_cancel_keyboard()
        )
        return

    wait_msg = await message.answer(f"🔍 <i>'{query}'</i> bo'yicha qidirilmoqda...")
    results = await news_service.search_news(query, limit=5)
    await wait_msg.delete()

    if not results:
        await message.answer(
            f"❌ <b>'{query}'</b> bo'yicha hech qanday yangilik topilmadi.\n\n"
            "Boshqa kalit so'z bilan izlab ko'ring yoki '❌ Bekor qilish' tugmasini bosing:",
            reply_markup=get_cancel_keyboard(),
            parse_mode="HTML"
        )
        return

    # Natijalar topildi
    await state.clear()
    header = f"🔍 '{query}' bo'yicha topilgan yangiliklar:"
    text = format_news_list(results, title_header=header)
    keyboard = get_news_list_keyboard(results, "world")

    await message.answer(text, reply_markup=keyboard, parse_mode="HTML", disable_web_page_preview=True)
    await message.answer(
        "Boshqa yangiliklarni ko'rish uchun asosiy menyudan foydalanishingiz mumkin 👇",
        reply_markup=get_main_keyboard()
    )


@router.message(F.text & ~F.text.startswith("/"))
async def auto_smart_search(message: Message):
    """Foydalanuvchi to'g'ridan-to'g'ri biror so'z yozganda avtomatik qidiruv qilish."""
    query = (message.text or "").strip()
    if len(query) < 2:
        await message.answer("Bosh menyudan kerakli bo'limni tanlang 👇", reply_markup=get_main_keyboard())
        return

    results = await news_service.search_news(query, limit=5)
    if results:
        header = f"🔍 '{query}' mavzusidagi yangiliklar:"
        text = format_news_list(results, title_header=header)
        keyboard = get_news_list_keyboard(results, "world")
        await message.answer(text, reply_markup=keyboard, parse_mode="HTML", disable_web_page_preview=True)
    else:
        await message.answer(
            f"🔍 <i>'{query}'</i> bo'yicha hozircha yangilik topilmadi.\n\n"
            "Kerakli bo'limni menyudan tanlashingiz mumkin 👇",
            reply_markup=get_main_keyboard(),
            parse_mode="HTML"
        )

