"""
Foydalanuvchi statistikasi, o'quv hisoboti, reyting, formulalar va ulashish handleri.
"""

import math
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from database.db import (
    get_user_stats,
    get_user_history,
    get_user_history_count,
    get_task_by_id,
    clear_user_history,
    get_leaderboard,
    get_user_rank,
    add_user
)
from keyboards.homework_keyboards import (
    get_history_keyboard,
    get_task_detail_keyboard,
    get_clear_confirm_keyboard,
    get_main_keyboard,
    get_formulas_keyboard,
    get_share_inline_keyboard
)
from services.formula_service import FORMULAS_DICT
from utils.formatters import format_user_stats, format_leaderboard, chunk_text

router = Router()

PAGE_SIZE = 5


@router.message(Command("stats"))
@router.message(F.text == "📊 Statistika")
@router.message(F.text == "📊 Mening statistikam")
async def cmd_my_stats(message: Message):
    """Foydalanuvchining shaxsiy ta'lim ko'rsatkichlari va hisoboti."""
    user = message.from_user
    await add_user(user.id, user.full_name, user.username)
    stats = await get_user_stats(user.id)
    text = format_user_stats(stats, user.full_name)
    await message.answer(text, parse_mode="Markdown")


@router.message(Command("top"))
@router.message(Command("leaderboard"))
@router.message(F.text == "🏆 Reyting")
@router.message(F.text == "🏆 O'quvchilar reytingi")
async def cmd_leaderboard(message: Message):
    """Eng faol o'quvchilar umumiy reytingi."""
    user = message.from_user
    await add_user(user.id, user.full_name, user.username)

    top_students = await get_leaderboard(limit=10)
    user_rank = await get_user_rank(user.id)

    text = format_leaderboard(top_students, user_rank, user.id)
    await message.answer(text, parse_mode="Markdown")


@router.message(Command("formulas"))
@router.message(F.text == "📖 Foydali formulalar")
async def cmd_formulas(message: Message):
    """Foydali formulalar va qoidalar menyusi."""
    text = (
        "📖 **Foydali Formulalar va Qoidalar Ma'lumotnomasi:**\n\n"
        "Kerakli fanni tanlang, bot sizga eng muhim formulalar, "
        "qoidalar va hisoblash usullarini taqdim etadi:"
    )
    await message.answer(text, reply_markup=get_formulas_keyboard())


@router.callback_query(F.data.startswith("formula:"))
async def callback_formula_detail(callback: CallbackQuery):
    """Tanlangan fan formulasini ko'rsatish."""
    key = callback.data.split("formula:")[1]
    formula_text = FORMULAS_DICT.get(key, "Formula ma'lumoti topilmadi.")

    await callback.answer()
    await callback.message.answer(formula_text, parse_mode="Markdown")


@router.message(Command("share"))
@router.message(F.text == "📤 Do'stlarga ulashish")
async def cmd_share(message: Message):
    """Botni do'stlarga va sinfdoshlarga ulashish."""
    text = (
        "📤 **Do'stlaringiz va sinfdoshlaringizga ham ulashing!**\n\n"
        "Ushbu bot boshqa o'quvchilar uchun ham bepul va juda foydali bo'lib, "
        "ularga qiyin misollarni o'rganishda va darslarni a'lo baholarga tayyorlashda yordam beradi.\n\n"
        "Quyidagi tugma orqali botni bir bosishda do'stlaringizga yuboring:"
    )
    await message.answer(text, reply_markup=get_share_inline_keyboard())


@router.message(F.text == "👥 Guruhga qo'shish")
async def cmd_add_to_group(message: Message):
    """Botni guruhga qo'shish yo'riqnomasi."""
    text = (
        "👥 **«VAZIFA BAJARADI» botini sinf yoki guruh chatiga qo'shing!**\n\n"
        "Bot guruhda birgalikda dars tayyorlash uchun juda qulay:\n\n"
        "📌 **Guruhda ishlash qoidalari:**\n"
        "1️⃣ Pastdagi «➕ Botni Guruhga Qo'shish» tugmasini bosing va o'z sinf/guruh chatini tanlang.\n"
        "2️⃣ Guruhda savol berish uchun shunchaki bot nomini yozing:\n"
        "   👉 Misol: `@uy_vazifa_bot 4x - 12 = 28 tenglamani yech`\n"
        "3️⃣ Yoki `/solve misol matni` buyrug'idan foydalaning.\n"
        "4️⃣ Bot boshqa odamlarning oddiy suhbatlariga xalaqit bermaydi, faqat unga murojaat qilingandagina javob beradi!"
    )
    await message.answer(text, reply_markup=get_share_inline_keyboard())


@router.message(Command("history"))
@router.message(F.text == "📜 Vazifalar tarixi")
async def cmd_my_history(message: Message):
    """Yechilgan vazifalar tarixini ko'rish."""
    user_id = message.from_user.id
    total_count = await get_user_history_count(user_id)

    if total_count == 0:
        await message.answer(
            "📜 **Sizda hali yechilgan vazifalar tarixi yo'q.**\n\n"
            "Vazifa yechish uchun misol yoki savolingizni yozib yuboring!",
            reply_markup=get_main_keyboard()
        )
        return

    total_pages = math.ceil(total_count / PAGE_SIZE)
    tasks = await get_user_history(user_id, limit=PAGE_SIZE, offset=0)

    text = (
        f"📜 **Sizning yechilgan vazifalaringiz tarixi:**\n"
        f"Jami vazifalar: {total_count} ta\n\n"
        f"Batafsil yechimni ko'rish uchun quyidagi tugmalardan birini bosing:"
    )

    await message.answer(
        text,
        reply_markup=get_history_keyboard(1, total_pages, tasks)
    )


@router.callback_query(F.data.startswith("hist_page:"))
async def callback_history_page(callback: CallbackQuery):
    """Tarix sahifasini almashtirish."""
    page_str = callback.data.split("hist_page:")[1]
    page = int(page_str)
    user_id = callback.from_user.id

    total_count = await get_user_history_count(user_id)
    total_pages = math.ceil(total_count / PAGE_SIZE)

    if page < 1:
        page = 1
    if page > total_pages:
        page = total_pages

    offset = (page - 1) * PAGE_SIZE
    tasks = await get_user_history(user_id, limit=PAGE_SIZE, offset=offset)

    text = (
        f"📜 **Sizning yechilgan vazifalaringiz tarixi:**\n"
        f"Jami vazifalar: {total_count} ta\n\n"
        f"Batafsil yechimni ko'rish uchun quyidagi tugmalardan birini bosing:"
    )

    await callback.answer()
    await callback.message.edit_text(
        text,
        reply_markup=get_history_keyboard(page, total_pages, tasks)
    )


@router.callback_query(F.data.startswith("view_task:"))
async def callback_view_task(callback: CallbackQuery):
    """Aniq bir vazifa va yechimini ko'rish."""
    task_id = int(callback.data.split("view_task:")[1])
    user_id = callback.from_user.id

    task = await get_task_by_id(task_id, user_id)
    if not task:
        await callback.answer("Vazifa topilmadi.", show_alert=True)
        return

    await callback.answer()

    date_str = str(task.get("created_at", ""))[:19]
    text = (
        f"📌 **Vazifa #{task['id']}**\n"
        f"📚 **Fan:** {task['subject']}\n"
        f"📅 **Sana:** {date_str}\n\n"
        f"❓ **Savol / Topshiriq:**\n{task['question']}\n\n"
        f"💡 **Yechim va tushuntirish:**\n{task['solution']}"
    )

    chunks = chunk_text(text, max_chars=3800)
    for idx, chunk in enumerate(chunks):
        if idx == len(chunks) - 1:
            await callback.message.answer(
                chunk,
                reply_markup=get_task_detail_keyboard(task_id)
            )
        else:
            await callback.message.answer(chunk)


@router.callback_query(F.data == "clear_history_prompt")
async def callback_clear_history_prompt(callback: CallbackQuery):
    """Tarixni tozalashni so'rash."""
    await callback.answer()
    await callback.message.edit_text(
        "⚠️ **Diqqat!** Rostdan ham barcha yechilgan vazifalar tarixingizni o'chirmoqchimisiz?\n\n"
        "Bu amalni ortga qaytarib bo'lmaydi.",
        reply_markup=get_clear_confirm_keyboard()
    )


@router.callback_query(F.data == "clear_history_confirm")
async def callback_clear_history_confirm(callback: CallbackQuery):
    """Tarixni butunlay tozalash."""
    user_id = callback.from_user.id
    count = await clear_user_history(user_id)
    await callback.answer("Tarix tozalandi!", show_alert=True)
    await callback.message.edit_text(
        f"✅ Sizning vazifalar tarixingiz tozalandi ({count} ta yozuv o'chirildi)."
    )


@router.callback_query(F.data == "noop")
async def callback_noop(callback: CallbackQuery):
    """Hech narsa qilmaydigan indikator tugmasi."""
    await callback.answer()
