"""
Uy vazifalarini qabul qilish, AI orqali yechish va foydalanuvchiga taqdim etish handleri.
Maxsus Ingliz tili yordamchisi: Grammatika mashqlari, qavslarni ochish, insho/esse,
rasm orqali yechish (Vision), audio talaffuz (TTS) va interaktiv testlar (Quiz).
"""

import io
import re
import random
import logging
from pathlib import Path
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database.db import save_task, get_user_subject, set_user_subject, get_task_by_id, add_user
from services.ai_service import ai_service
from services.english_service import (
    english_service,
    ENGLISH_RULES,
    GRAMMAR_QUIZ,
    ESSAY_TEMPLATES
)
from services.tts_service import tts_service
from keyboards.homework_keyboards import (
    get_main_keyboard,
    get_solution_inline_keyboard,
    get_cancel_keyboard,
    get_english_rules_keyboard,
    get_irregular_pagination_keyboard,
    get_quiz_keyboard
)
from states.homework_states import HomeworkStates
from utils.formatters import chunk_text
from config import BASE_DIR

logger = logging.getLogger(__name__)
router = Router()

MENU_BUTTONS = {
    "🇬🇧 Ingliz tili vazifasi",
    "✏️ Yangi vazifa yechish",
    "📝 Insho / Esse yordamchisi",
    "📚 Qoidalar & Noto'g'ri fe'llar",
    "🎯 Grammatika Quizi",
    "📷 Rasm orqali vazifa yechish",
    "📚 Boshqa fanlar",
    "📚 Fanlar",
    "📊 Statistika",
    "📊 Mening statistikam",
    "🏆 Reyting",
    "🏆 O'quvchilar reytingi",
    "⚙️ AI Kalit sozlash",
    "📜 Vazifalar tarixi",
    "📖 Foydali formulalar",
    "👥 Guruhga qo'shish",
    "📤 Do'stlarga ulashish",
    "ℹ️ Bot haqida",
    "❓ Yordam",
    "❌ Bekor qilish"
}


async def safe_reply(message: Message, text: str, reply_markup=None):
    """Xabarni xavfsiz yuborish (Markdown xatolarini avtomatik chetlab o'tadi)."""
    try:
        return await message.answer(text, parse_mode="Markdown", reply_markup=reply_markup)
    except Exception:
        return await message.answer(text, parse_mode=None, reply_markup=reply_markup)


# =========================================================================
# 1. Vazifa yechish buyrug'i
# =========================================================================

@router.message(Command("solve"))
@router.message(Command("english"))
@router.message(Command("vazifa"))
@router.message(F.text == "🇬🇧 Ingliz tili vazifasi")
@router.message(F.text == "✏️ Yangi vazifa yechish")
async def cmd_solve(message: Message, state: FSMContext, bot: Bot):
    """Vazifa yechish buyrug'i."""
    user = message.from_user
    await add_user(user.id, user.full_name, user.username)
    current_subj = await get_user_subject(user.id)

    # Agar /solve bilan birga matn kelsa: masalan `/solve She (go) to school yesterday`
    if message.text and (message.text.startswith("/solve") or message.text.startswith("/english") or message.text.startswith("/vazifa")):
        parts = message.text.split(maxsplit=1)
        if len(parts) > 1:
            await process_question(message, parts[1].strip(), current_subj, bot)
            return

    if message.chat.type == "private":
        await state.set_state(HomeworkStates.waiting_for_question)
        await safe_reply(
            message,
            "🇬🇧 **Ingliz tili vazifasini yuboring:**\n\n"
            "Savol, mashq, qavslarni ochish, test yoki tarjima matnini yozing:\n"
            "_(Masalan: `She (visit) London last year` yoki `Nuqtalar o'rniga predlog qo'ying: interested ... art`)_\n\n"
            "💡 *Darslik yoki daftardagi mashq rasmini ham yuborishingiz mumkin!*",
            reply_markup=get_cancel_keyboard()
        )
    else:
        await safe_reply(
            message,
            "Guruhda vazifa yechish uchun buyruqdan so'ng misolni yozing:\n"
            "Masalan: `/solve She (visit) London last year`"
        )


@router.callback_query(F.data == "act:new_task")
async def callback_new_task(callback: CallbackQuery, state: FSMContext):
    """Inline tugma orqali yangi vazifa so'rash."""
    user_id = callback.from_user.id
    current_subj = await get_user_subject(user_id)

    await state.set_state(HomeworkStates.waiting_for_question)
    await callback.answer()
    await safe_reply(
        callback.message,
        f"🇬🇧 **Yangi vazifangizni yuboring** (Fan: {current_subj}):\n"
        f"Matn yoki rasm ko'rinishida yuborishingiz mumkin.",
        reply_markup=get_cancel_keyboard()
    )


# =========================================================================
# 2. Insho / Esse Yordamchisi (Writing Helper)
# =========================================================================

@router.message(Command("essay"))
@router.message(F.text == "📝 Insho / Esse yordamchisi")
async def cmd_essay(message: Message, state: FSMContext):
    """Insho yozish yoki tekshirish rejimi."""
    await state.set_state(HomeworkStates.waiting_for_essay)
    text = (
        "📝 **Ingliz tili Insho & Esse Yordamchisi:**\n\n"
        "1️⃣ **Yangi insho yozdirish:**\n"
        "Shunchaki mavzuni yuboring (Masalan: `Mavzu: My Future Profession` yoki `Mavzu: The Internet in our lives`).\n\n"
        "2️⃣ **O'zingiz yozgan inshoni tekshirtirish:**\n"
        "O'zingiz yozgan inglizcha matn yoki esseni yuboring — bot undagi barcha grammatik, imlo va uslubiy xatolarni "
        "aniqlab, tushuntirib va to'g'irlab beradi!\n\n"
        "👇 *Mavzuni yoki tayyor matningizni yuboring:*"
    )
    await safe_reply(message, text, reply_markup=get_cancel_keyboard())


@router.message(HomeworkStates.waiting_for_essay, F.text)
async def handle_essay_input(message: Message, state: FSMContext, bot: Bot):
    """Insho mavzusi yoki tekshirish uchun matn kelganda."""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=get_main_keyboard())
        return

    text = message.text.strip()
    await state.clear()

    await bot.send_chat_action(message.chat.id, "typing")
    wait_msg = await safe_reply(message, "✍️ *Insho tahlil qilinmoqda va tayyorlanmoqda...*")

    # Agar so'zlar soni ko'p bo'lsa (o'quvchi o'z inshosini yuborgan bo'lsa) -> tekshiramiz
    words = text.split()
    if len(words) >= 15 and not text.lower().startswith("mavzu:"):
        result = await ai_service.check_essay(text)
    else:
        prompt = (
            f"Quyidagi mavzuda maktab/litsey o'quvchisi uchun chiroyli, grammatik jihatdan to'g'ri, "
            f"kirish (Introduction), asosiy qism (Body) va xulosa (Conclusion)dan iborat insho (essay) yozib bering:\n"
            f"Mavzu: {text}\n"
            f"Insho matnidan so'ng, uning o'zbekcha tarjimasini va ishlatilgan 5 ta eng muhim so'zlar lug'atini ham qo'shing."
        )
        result = await ai_service.solve_homework(prompt, subject="🇬🇧 Ingliz tili")

    try:
        await wait_msg.delete()
    except Exception:
        pass

    user = message.from_user
    task_id = await save_task(user.id, "🇬🇧 Ingliz tili (Insho)", text[:100], result)

    chunks = chunk_text(f"📝 **Insho / Esse Natijasi:**\n\n" + result, max_chars=3800)
    for idx, chunk in enumerate(chunks):
        if idx == len(chunks) - 1:
            await safe_reply(message, chunk, reply_markup=get_solution_inline_keyboard(task_id))
        else:
            await safe_reply(message, chunk)


# =========================================================================
# 3. Ingliz tili Qoidalari va Noto'g'ri fe'llar
# =========================================================================

@router.message(Command("rules"))
@router.message(F.text == "📚 Qoidalar & Noto'g'ri fe'llar")
async def cmd_english_rules(message: Message):
    """Qoidalar va formulalar menyusi."""
    text = (
        "📚 **Ingliz tili Grammatika Qoidalari va Ma'lumotnomasi:**\n\n"
        "O'zingizga kerakli bo'limni tanlang:\n"
        "• ⏱ 12 ta Ingliz tili zamonlari (Simple, Continuous, Perfect)\n"
        "• 🏗 Passive Voice (Majhul nisbat)\n"
        "• 🔀 Conditionals (Shart ergash gaplar)\n"
        "• 📍 Predloglar (in, on, at) va Artikllar\n"
        "• 📖 150+ Noto'g'ri fe'llar (Irregular verbs) to'liq ro'yxati"
    )
    await message.answer(text, reply_markup=get_english_rules_keyboard(), parse_mode="Markdown")


@router.callback_query(F.data.startswith("rule:"))
async def callback_rule_detail(callback: CallbackQuery):
    """Qoida tafsilotlarini chiqarish."""
    rule_key = callback.data.split("rule:")[1]
    rule_content = english_service.get_rule_by_key(rule_key)

    if not rule_content:
        await callback.answer("Qoida topilmadi.", show_alert=True)
        return

    await callback.answer()
    back_markup = get_english_rules_keyboard()
    await callback.message.edit_text(rule_content, parse_mode="Markdown", reply_markup=back_markup)


@router.callback_query(F.data == "act:back_rules")
async def callback_back_rules(callback: CallbackQuery):
    """Qoidalar bosh menyusiga qaytish."""
    await callback.answer()
    text = "📚 **Ingliz tili Grammatika Qoidalari va Ma'lumotnomasi:**"
    await callback.message.edit_text(text, reply_markup=get_english_rules_keyboard(), parse_mode="Markdown")


@router.callback_query(F.data.startswith("irreg_page:"))
async def callback_irreg_page(callback: CallbackQuery):
    """Noto'g'ri fe'llar ro'yxatini varaqlash."""
    page = int(callback.data.split("irreg_page:")[1])
    text, total_pages = english_service.get_all_irregular_verbs_text(page=page)

    await callback.answer()
    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_irregular_pagination_keyboard(page, total_pages)
    )


@router.callback_query(F.data == "act:search_irreg")
async def callback_search_irreg(callback: CallbackQuery, state: FSMContext):
    """Noto'g'ri fe'l qidirish holati."""
    await state.set_state(HomeworkStates.waiting_for_irregular_search)
    await callback.answer()
    await safe_reply(
        callback.message,
        "🔍 **Noto'g'ri fe'l qidirish:**\n\n"
        "Fe'lning istalgan shaklini yoki o'zbekcha ma'nosini yozing:\n"
        "*(Masalan: `wrote`, `buy`, `seen`, `yozmoq`)*",
        reply_markup=get_cancel_keyboard()
    )


@router.message(HomeworkStates.waiting_for_irregular_search, F.text)
async def handle_search_irreg_input(message: Message, state: FSMContext):
    """Qidirilayotgan fe'lni qabul qilish."""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=get_main_keyboard())
        return

    query = message.text.strip()
    await state.clear()

    results = english_service.search_irregular_verb(query)
    if not results:
        await message.answer(
            f"❌ `{query}` bo'yicha noto'g'ri fe'l topilmadi.\n"
            f"Balki bu to'g'ri (regular) fe'ldir? To'g'ri fe'llarga o'tgan zamonda faqat `-ed` qo'shiladi.",
            reply_markup=get_main_keyboard()
        )
        return

    lines = [f"🔍 **«{query}» bo'yicha topilgan natijalar:**\n"]
    for v in results[:5]:
        lines.append(
            f"🔹 **V1 (Infinitive):** `{v['v1']}`\n"
            f"🔹 **V2 (Past Simple):** `{v['v2']}`\n"
            f"🔹 **V3 (Past Participle):** `{v['v3']}`\n"
            f"🇺🇿 **Ma'nosi:** **{v['uz']}**\n"
            f"📝 **Misol:** *{v['ex']}*\n"
        )

    await safe_reply(message, "\n".join(lines), reply_markup=get_main_keyboard())


# =========================================================================
# 4. Grammatika Quizi (Interaktiv Test)
# =========================================================================

@router.message(Command("quiz"))
@router.message(F.text == "🎯 Grammatika Quizi")
async def cmd_quiz(message: Message):
    """Grammatika testini boshlash."""
    q = random.choice(GRAMMAR_QUIZ)
    options_text = "\n".join(q["options"])
    text = (
        f"🎯 **Ingliz Tili Grammatika Quizi:**\n\n"
        f"❓ **Savol #{q['id']}:**\n"
        f"{q['question']}\n\n"
        f"{options_text}\n\n"
        f"To'g'ri variantni tanlang: 👇"
    )
    await message.answer(text, reply_markup=get_quiz_keyboard(q["id"]))


@router.callback_query(F.data.startswith("quiz_ans:"))
async def callback_quiz_answer(callback: CallbackQuery):
    """Foydalanuvchi variant tanlaganda tekshirish."""
    parts = callback.data.split(":")
    quiz_id = int(parts[1])
    selected_option = parts[2]

    q = next((item for item in GRAMMAR_QUIZ if item["id"] == quiz_id), None)
    if not q:
        await callback.answer("Savol topilmadi.", show_alert=True)
        return

    is_correct = (selected_option == q["correct"])
    await callback.answer()

    if is_correct:
        res_header = f"🎉 **Ajoyib! To'g'ri javob: {q['correct']}**\n\n"
    else:
        res_header = f"❌ **Afsuski noto'g'ri.** To'g'ri javob: **{q['correct']}**\n\n"

    explanation_text = (
        f"{res_header}"
        f"💡 **Tushuntirish va Qoida:**\n{q['explanation']}\n\n"
        f"Keyingi savolga o'tish uchun pastdagi tugmani bosing:"
    )

    next_markup = get_quiz_keyboard(quiz_id)
    await callback.message.edit_text(explanation_text, parse_mode="Markdown", reply_markup=next_markup)


@router.callback_query(F.data == "quiz_next")
async def callback_quiz_next(callback: CallbackQuery):
    """Keyingi tasodifiy savolga o'tish."""
    q = random.choice(GRAMMAR_QUIZ)
    options_text = "\n".join(q["options"])
    text = (
        f"🎯 **Ingliz Tili Grammatika Quizi:**\n\n"
        f"❓ **Savol #{q['id']}:**\n"
        f"{q['question']}\n\n"
        f"{options_text}\n\n"
        f"To'g'ri variantni tanlang: 👇"
    )
    await callback.answer()
    await callback.message.edit_text(text, reply_markup=get_quiz_keyboard(q["id"]))


# =========================================================================
# 5. Audio Talaffuz (Pronunciation Voice Callback)
# =========================================================================

@router.callback_query(F.data.startswith("voice:"))
async def callback_pronounce_voice(callback: CallbackQuery, bot: Bot):
    """Yechim ichidagi inglizcha gapni audio qilib yuborish."""
    parts = callback.data.split(":")
    task_id = int(parts[1])
    user_id = callback.from_user.id

    task = await get_task_by_id(task_id, user_id)
    if not task:
        await callback.answer("Vazifa topilmadi.", show_alert=True)
        return

    await callback.answer("🔊 Audio talaffuz tayyorlanmoqda...")
    audio_text = f"{task['question']} {task['solution']}"
    audio_path = tts_service.generate_audio(audio_text, filename_prefix=f"task_{task_id}")

    if audio_path and Path(audio_path).exists():
        try:
            voice_file = FSInputFile(audio_path)
            await callback.message.answer_voice(
                voice_file,
                caption=f"🔊 **Inglizcha talaffuz** (Vazifa #{task_id})"
            )
        except Exception as e:
            logger.error(f"Voice yuborishda xatolik: {e}")
            await callback.message.answer("Audio yuborishda xatolik yuz berdi.")
    else:
        await callback.message.answer("Audio hosil qilib bo'lmadi.")


# =========================================================================
# 6. AI Kalit Sozlash (/setkey)
# =========================================================================

@router.message(Command("setkey"))
@router.message(F.text == "⚙️ AI Kalit sozlash")
async def cmd_set_key(message: Message, state: FSMContext):
    """API kalitini sozlash yoki qo'llanma ko'rsatish."""
    # Agar buyruq bilan birga kalit kelsa: `/setkey AIzaSy...`
    if message.text and message.text.startswith("/setkey") and len(message.text.split()) > 1:
        key_value = message.text.split(maxsplit=1)[1].strip()
        await save_api_key_logic(message, key_value)
        return

    await state.set_state(HomeworkStates.waiting_for_api_key)
    guide_text = (
        "⚙️ **Sun'iy Intellekt (AI) API Kalitini Sozlash:**\n\n"
        "Botda savollarni yanada chuqur tahlil qilish va rasmdagi topshiriqlarni o'qish (Vision) "
        "uchun **Google Gemini** yoki **Groq** bepul API kalitini ulashingiz mumkin.\n\n"
        "🌟 **Qanday qilib 1 daqiqada bepul kalit olish mumkin?**\n"
        "1️⃣ **Google Gemini (Tavsiya etiladi - Matn va Rasm):**\n"
        "   👉 https://aistudio.google.com saytiga kiring\n"
        "   👉 «Get API key» tugmasini bosing va kalitni nusxalang.\n\n"
        "2️⃣ **Groq Cloud (O'ta tezkor):**\n"
        "   👉 https://console.groq.com saytiga kiring va kalit oling.\n\n"
        "👇 *Olingan kalitni shu yerga xabar qilib yuboring:*"
    )
    await safe_reply(message, guide_text, reply_markup=get_cancel_keyboard())


@router.message(HomeworkStates.waiting_for_api_key, F.text)
async def handle_api_key_input(message: Message, state: FSMContext):
    """Kiritilgan API kalitini saqlash."""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=get_main_keyboard())
        return

    key_value = message.text.strip()
    await state.clear()
    await save_api_key_logic(message, key_value)


async def save_api_key_logic(message: Message, key_value: str):
    """Kalit turini aniqlab saqlash."""
    env_file = BASE_DIR / ".env"
    env_content = env_file.read_text(encoding="utf-8") if env_file.exists() else ""

    if key_value.startswith("AIza"):
        # Google Gemini
        ai_service.update_keys(gemini_key=key_value)
        if "GEMINI_API_KEY=" in env_content:
            env_content = re.sub(r'GEMINI_API_KEY=.*', f'GEMINI_API_KEY={key_value}', env_content)
        else:
            env_content += f"\nGEMINI_API_KEY={key_value}\n"
        env_file.write_text(env_content, encoding="utf-8")
        await message.answer(
            "✅ **Google Gemini API kaliti muvaffaqiyatli ulandi!**\n\n"
            "Endi siz matnli va rasmli (kitob/daftar fotosurati) barcha vazifalarni "
            "Gemini 2.0 Flash orqali eng yuqori aniqlikda yechishingiz mumkin! 🚀",
            reply_markup=get_main_keyboard()
        )

    elif key_value.startswith("gsk_"):
        # Groq
        ai_service.update_keys(groq_key=key_value)
        if "GROQ_API_KEY=" in env_content:
            env_content = re.sub(r'GROQ_API_KEY=.*', f'GROQ_API_KEY={key_value}', env_content)
        else:
            env_content += f"\nGROQ_API_KEY={key_value}\n"
        env_file.write_text(env_content, encoding="utf-8")
        await message.answer(
            "✅ **Groq Cloud API kaliti muvaffaqiyatli ulandi!**\n\n"
            "Llama 3.3 70B modeli faollashdi — vazifalar bir zumda yechiladi!",
            reply_markup=get_main_keyboard()
        )

    elif key_value.startswith("sk-"):
        # OpenAI
        ai_service.update_keys(openai_key=key_value)
        if "OPENAI_API_KEY=" in env_content:
            env_content = re.sub(r'OPENAI_API_KEY=.*', f'OPENAI_API_KEY={key_value}', env_content)
        else:
            env_content += f"\nOPENAI_API_KEY={key_value}\n"
        env_file.write_text(env_content, encoding="utf-8")
        await message.answer(
            "✅ **OpenAI API kaliti muvaffaqiyatli ulandi!**",
            reply_markup=get_main_keyboard()
        )

    else:
        # Noma'lum kalit, lekin Gemini deb belgilaymiz
        ai_service.update_keys(gemini_key=key_value)
        await message.answer(
            f"✅ API kalit saqlandi: `{key_value[:8]}...`",
            reply_markup=get_main_keyboard()
        )


# =========================================================================
# 7. Rasm orqali vazifani yechish (Photo Homework)
# =========================================================================

@router.message(F.text == "📷 Rasm orqali vazifa yechish")
async def cmd_photo_prompt(message: Message):
    """Rasm yuborish taklifi."""
    await safe_reply(
        message,
        "📷 **Rasm orqali vazifa yechish:**\n\n"
        "Ingliz tili kitobingiz yoki daftaringizdagi mashqni sifatli rasmga olib yuboring.\n"
        "Sun'iy intellekt mashqni o'qib oladi va uni qadamma-qadam yechib beradi!"
    )


@router.message(F.photo)
async def handle_photo_homework(message: Message, state: FSMContext, bot: Bot):
    """Foydalanuvchi vazifa rasmini yuborganda (Multimodal Vision)."""
    user = message.from_user
    await add_user(user.id, user.full_name, user.username)
    current_subj = await get_user_subject(user.id)

    wait_msg = await safe_reply(
        message,
        "📷 *Rasm qabul qilindi. AI tasvirni o'qimoqda va mashqlarni yechmoqda...*"
    )

    try:
        photo = message.photo[-1]
        file_stream = await bot.download(photo)
        image_bytes = file_stream.read()

        caption = message.caption or ""
        solution = await ai_service.solve_photo(image_bytes=image_bytes, caption=caption)

        task_id = await save_task(user.id, current_subj, f"[Rasm topshirig'i]: {caption}", solution)

        try:
            await wait_msg.delete()
        except Exception:
            pass

        chunks = chunk_text(f"🇬🇧 **Rasm bo'yicha yechim:**\n\n" + solution, max_chars=3800)
        for idx, chunk in enumerate(chunks):
            if idx == len(chunks) - 1:
                await safe_reply(message, chunk, reply_markup=get_solution_inline_keyboard(task_id))
            else:
                await safe_reply(message, chunk)

    except Exception as e:
        logger.error(f"Rasm tahlilida xatolik: {e}")
        try:
            await wait_msg.delete()
        except Exception:
            pass
        await message.answer(
            "❌ Rasmni tahlil qilishda xatolik yuz berdi.\n"
            "Iltimos, mashq matnini oddiy yozuv ko'rinishida yuboring."
        )


# =========================================================================
# 8. Asosiy Matnli Vazifalarni Qabul Qilish (Catch-all)
# =========================================================================

@router.message(HomeworkStates.waiting_for_question, F.text)
@router.message(F.text & ~F.text.startswith("/") & ~F.text.in_(MENU_BUTTONS))
async def handle_homework_question(message: Message, state: FSMContext, bot: Bot):
    """Vazifa matnini qabul qilib, yechim tayyorlash."""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=get_main_keyboard())
        return

    text = message.text.strip()
    is_group = message.chat.type in ["group", "supergroup"]

    # Guruh chatlari uchun tekshiruv
    if is_group:
        bot_info = await bot.get_me()
        bot_tag = f"@{bot_info.username}".lower()
        is_reply_to_bot = bool(message.reply_to_message and message.reply_to_message.from_user.id == bot_info.id)
        is_mentioned = bot_tag in text.lower()

        if not (is_mentioned or is_reply_to_bot):
            return

        if is_mentioned:
            text = re.sub(re.escape(bot_tag), "", text, flags=re.IGNORECASE).strip()

    if len(text) < 2:
        if not is_group:
            await message.answer("Iltimos, vazifa matnini to'liqroq yozing.")
        return

    user = message.from_user
    await add_user(user.id, user.full_name, user.username)
    current_subj = await get_user_subject(user.id)
    await state.clear()

    await process_question(message, text, current_subj, bot)


async def process_question(message: Message, question_text: str, subject: str, bot: Bot):
    """Savolni yechish va foydalanuvchiga yetkazish."""
    user = message.from_user
    await bot.send_chat_action(message.chat.id, "typing")
    wait_msg = await safe_reply(
        message,
        "🧠 *AI vazifani tahlil qilmoqda va qadamma-qadam yechim tayyorlamoqda...*"
    )

    try:
        solution = await ai_service.solve_homework(question_text, subject, mode="standard")
        task_id = await save_task(user.id, subject, question_text, solution)

        header = f"🎓 **Fan:** {subject}\n👤 **So'rovchi:** {user.full_name}\n\n"
        full_text = header + solution

        chunks = chunk_text(full_text, max_chars=3800)

        try:
            await wait_msg.delete()
        except Exception:
            pass

        for idx, chunk in enumerate(chunks):
            if idx == len(chunks) - 1:
                await safe_reply(
                    message,
                    chunk,
                    reply_markup=get_solution_inline_keyboard(task_id)
                )
            else:
                await safe_reply(message, chunk)

    except Exception as e:
        logger.error(f"Xatolik yuz berdi: {e}")
        try:
            await wait_msg.delete()
        except Exception:
            pass
        await message.answer(
            "❌ Yechim tayyorlashda kutilmagan xatolik yuz berdi.\n"
            "Iltimos, savolni soddaroq qilib qayta yuboring."
        )


# =========================================================================
# 9. Rejimni O'zgartirish (Oddiyroq / Qisqa xulosa)
# =========================================================================

@router.callback_query(F.data.startswith("mode:"))
async def callback_change_solution_mode(callback: CallbackQuery):
    """Yechim usulini o'zgartirish (Oddiyroq tushuntirish yoki qisqa xulosa)."""
    parts = callback.data.split(":")
    if len(parts) < 3:
        await callback.answer("Xatolik.")
        return

    mode = parts[1]
    task_id = int(parts[2])
    user_id = callback.from_user.id

    task = await get_task_by_id(task_id, user_id)
    if not task:
        await callback.answer("Vazifa topilmadi.", show_alert=True)
        return

    mode_label = "Oddiyroq tushuntirish" if mode == "simple" else "Qisqa xulosa"
    await callback.answer(f"{mode_label} tayyorlanmoqda...")

    wait_msg = await safe_reply(callback.message, f"⏳ *{mode_label} tayyorlanmoqda...*")
    try:
        new_solution = await ai_service.solve_homework(
            question=task["question"],
            subject=task["subject"],
            mode=mode
        )
        try:
            await wait_msg.delete()
        except Exception:
            pass

        chunks = chunk_text(f"📌 **Rejim: {mode_label}**\n\n" + new_solution, max_chars=3800)
        for chunk in chunks:
            await safe_reply(callback.message, chunk)
    except Exception as e:
        try:
            await wait_msg.delete()
        except Exception:
            pass
        await callback.message.answer(f"Xatolik: {e}")
