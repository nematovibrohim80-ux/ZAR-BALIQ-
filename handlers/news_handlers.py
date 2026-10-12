"""
Yangiliklarni chiqarish va ko'rish handlerlari.
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from services.news_service import news_service
from keyboards.news_keyboards import (
    get_categories_keyboard,
    get_news_list_keyboard,
    get_news_detail_keyboard
)
from utils.formatters import format_news_list, format_single_news

router = Router()

CATEGORY_TITLES = {
    "world": "🌐 Jahon va Siyosat yangiliklari",
    "breaking": "⚡️ Eng qaynoq xabarlar",
    "tech": "💻 Texnologiya va IT yangiliklari",
    "economy": "💰 Iqtisodiyot va Moliya yangiliklari",
    "sport": "⚽️ Sport olami yangiliklari",
    "uzb": "🇺🇿 Jamiyat & O'zbekiston yangiliklari"
}


WORLD_TRIGGERS = ["🌍 dunyo yangiliklari", "dunyo yangiliklari", "dunyo", "jahon", "jahon yangiliklari", "world", "world news"]
UZB_TRIGGERS = ["🇺🇿 o'zbekiston", "o'zbekiston", "ozbekiston", "o‘zbekiston", "uzbekiston", "uzb", "uzbekistan"]
BREAKING_TRIGGERS = ["⚡️ qaynoq xabarlar", "qaynoq xabarlar", "qaynoq", "so'nggi xabarlar", "songgi xabarlar", "tezkor", "breaking"]
CATEGORY_TRIGGERS = ["📂 kategoriyalar", "kategoriyalar", "bolimlar", "bo'limlar", "bo‘limlar", "mavzular"]


@router.message(lambda msg: msg.text and msg.text.strip().lower() in WORLD_TRIGGERS)
async def show_world_news(message: Message, state: FSMContext):
    """Dunyo yangiliklarini chiqarish."""
    await state.clear()
    wait_msg = await message.answer("🔄 Dunyo yangiliklari yuklanmoqda...")
    items = await news_service.get_world_news(limit=5)
    text = format_news_list(items, title_header="🌍 Dunyo / Jahon Yangiliklari")
    keyboard = get_news_list_keyboard(items, "world")
    await wait_msg.delete()
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML", disable_web_page_preview=True)


@router.message(lambda msg: msg.text and msg.text.strip().lower() in UZB_TRIGGERS)
async def show_uzbekistan_news(message: Message, state: FSMContext):
    """O'zbekiston yangiliklarini chiqarish."""
    await state.clear()
    wait_msg = await message.answer("🔄 O'zbekiston yangiliklari olinmoqda...")
    items = await news_service.get_by_category("uzb", limit=5)
    text = format_news_list(items, title_header="🇺🇿 O'zbekiston Yangiliklari")
    keyboard = get_news_list_keyboard(items, "uzb")
    await wait_msg.delete()
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML", disable_web_page_preview=True)


@router.message(lambda msg: msg.text and msg.text.strip().lower() in BREAKING_TRIGGERS)
async def show_breaking_news(message: Message, state: FSMContext):
    """Eng so'nggi daqiqalardagi qaynoq xabarlar."""
    await state.clear()
    wait_msg = await message.answer("🔄 Eng so'nggi xabarlar olinmoqda...")
    items = await news_service.get_breaking_news(limit=5)
    text = format_news_list(items, title_header="⚡️ Eng Qaynoq Yangiliklar")
    keyboard = get_news_list_keyboard(items, "breaking")
    await wait_msg.delete()
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML", disable_web_page_preview=True)


@router.message(lambda msg: msg.text and msg.text.strip().lower() in CATEGORY_TRIGGERS)
async def show_categories(message: Message, state: FSMContext):
    """Kategoriyalarni tanlash bo'limi."""
    await state.clear()
    text = (
        "📂 <b>Qaysi soha yangiliklari sizga qiziq?</b>\n\n"
        "Quyidagi mavzulardan birini tanlang:"
    )
    await message.answer(text, reply_markup=get_categories_keyboard(), parse_mode="HTML")


@router.callback_query(F.data.startswith("cat_"))
async def handle_category_select(callback: CallbackQuery):
    """Kategoriya tanlanganda yangiliklarni chiqarish."""
    cat_code = callback.data.replace("cat_", "")
    header = CATEGORY_TITLES.get(cat_code, "📰 Yangiliklar")

    await callback.answer("Yuklanmoqda...")
    items = await news_service.get_by_category(cat_code, limit=5)
    text = format_news_list(items, title_header=header)
    keyboard = get_news_list_keyboard(items, cat_code)

    try:
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML", disable_web_page_preview=True)
    except Exception:
        await callback.message.answer(text, reply_markup=keyboard, parse_mode="HTML", disable_web_page_preview=True)


@router.callback_query(F.data.startswith("refresh_"))
async def handle_refresh(callback: CallbackQuery):
    """Yangiliklarni majburiy yangilash."""
    cat_code = callback.data.replace("refresh_", "")
    await callback.answer("Yangiliklar yangilanmoqda...")

    await news_service.refresh_all_news()

    if cat_code == "world":
        items = await news_service.get_world_news(limit=5)
    elif cat_code == "breaking":
        items = await news_service.get_breaking_news(limit=5)
    else:
        items = await news_service.get_by_category(cat_code, limit=5)

    header = CATEGORY_TITLES.get(cat_code, "📰 Yangiliklar")
    text = format_news_list(items, title_header=header)
    keyboard = get_news_list_keyboard(items, cat_code)

    try:
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML", disable_web_page_preview=True)
    except Exception:
        pass


@router.callback_query(F.data.startswith("view_"))
async def handle_view_news(callback: CallbackQuery):
    """Bitta yangilikning to'liq kartochkasini rasm bilan ochish."""
    item_id = callback.data.replace("view_", "")
    item = await news_service.get_item_by_id(item_id)

    if not item:
        await callback.answer("Kechirasiz, ushbu yangilik eskirgan.", show_alert=True)
        return

    await callback.answer()
    caption_text = format_single_news(item)
    keyboard = get_news_detail_keyboard(item.link, item.category)

    # Agar rasm bo'lsa, rasmli xabar sifatida yuborish
    if item.image_url:
        try:
            await callback.message.answer_photo(
                photo=item.image_url,
                caption=caption_text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            return
        except Exception:
            # Agar rasm yuborishda xatolik bo'lsa, oddiy matn sifatida yuboramiz
            pass

    await callback.message.answer(
        text=caption_text,
        reply_markup=keyboard,
        parse_mode="HTML",
        disable_web_page_preview=False
    )
