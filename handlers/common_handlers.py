"""
Asosiy umumiy buyruqlar va xabarlar handleri (/start, /help, bot haqida).
Ingliz tili va fanlardan uy vazifasini oson yechish yordamchisi.
"""

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from database.db import add_user, get_user_subject, set_user_subject
from keyboards.homework_keyboards import get_main_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Start buyrug'i — foydalanuvchini kutib olish."""
    await state.clear()
    user = message.from_user
    await add_user(user.id, user.full_name, user.username)

    # Standart fanni Ingliz tili qilib belgilaymiz
    await set_user_subject(user.id, "🇬🇧 Ingliz tili")

    welcome_text = (
        f"Assalomu alaykum, **{user.full_name}**! 👋🇬🇧\n\n"
        f"🤖 Men sizning shaxsiy **Ingliz Tili Uy Vazifasi Yordamchingizman** (@uy_vazifa_bot)!\n\n"
        f"📚 **Men sizga qanday yordam bera olaman?**\n"
        f"• ✍️ **Grammatika mashqlari:** Qavslarni ochish, to'g'ri zamonni qo'yish, testlar (A, B, C, D)\n"
        f"• 📝 **Insho & Esse:** Har qanday mavzuda insho yozish yoki o'zingiz yozgan inshoni tekshirib xatolarini tuzatish\n"
        f"• 🔊 **Ovozli talaffuz:** Gap va so'zlarning to'g'ri audio talaffuzini eshitish\n"
        f"• 📖 **Qoidalar & Noto'g'ri fe'llar:** 12 ta zamon, 150+ Irregular verbs, predloglar (in/on/at), artikllar\n"
        f"• 🎯 **Grammatika Quizi:** Bilimingizni sinash uchun interaktiv testlar\n"
        f"• 📷 **Rasm orqali yechish:** Kitob yoki daftaringizdagi mashq rasmini yuboring\n\n"
        f"🚀 **Boshlash uchun:** Inglizcha mashq, gap yoki savolingizni to'g'ridan-to'g'ri yozib yuboring, "
        f"yoki quyidagi menyu tugmalaridan foydalaning!"
    )

    await message.answer(welcome_text, reply_markup=get_main_keyboard(), parse_mode="Markdown")


@router.message(Command("help"))
@router.message(F.text == "❓ Yordam")
async def cmd_help(message: Message):
    """Botdan foydalanish bo'yicha qo'llanma."""
    help_text = (
        "📖 **Ingliz Tili Boti bo'yicha qo'llanma:**\n\n"
        "1️⃣ **Vazifani yechish:**\n"
        "• Mashq matnini yuboring. Masalan: `She (go) to school yesterday` yoki `Present Perfect qoidasi nima?`\n"
        "• Bot qadamma-qadam qoidasi bilan to'g'ri javobni yechib beradi.\n\n"
        "2️⃣ **Ovozli talaffuz (Audio):**\n"
        "• Yechim chiqqandan so'ng pastdagi **«🔊 Talaffuzni eshitish»** tugmasini bosing — bot toza inglizcha audio yuboradi.\n\n"
        "3️⃣ **Insho va Esse (Writing):**\n"
        "• «📝 Insho / Esse yordamchisi» tugmasini bosing.\n"
        "• Mavzu bersangiz insho yozib beradi, yoki o'zingiz yozgan matnni yuborsangiz xatolarini tekshiradi.\n\n"
        "4️⃣ **Noto'g'ri fe'llar (Irregular verbs):**\n"
        "• Shunchaki fe'lning istalgan shaklini yozing: `wrote`, `buy`, `bormoq`. Bot 3 ta shaklini chiqarib beradi.\n\n"
        "5️⃣ **Rasm orqali vazifa yechish:**\n"
        "• Darslik yoki daftardagi inglizcha mashq rasmini botga yuboring.\n\n"
        "6️⃣ **Asosiy buyruqlar:**\n"
        "• /start — Botni ishga tushirish\n"
        "• /solve — Yangi vazifa yechish\n"
        "• /quiz — Grammatika testini boshlash\n"
        "• /rules — Qoidalar va formulalar\n"
        "• /setkey — AI API kalitini o'rnatish\n"
        "• /help — Qo'llanma"
    )
    await message.answer(help_text, parse_mode="Markdown")


@router.message(F.text == "ℹ️ Bot haqida")
async def cmd_about(message: Message):
    """Bot haqida ma'lumot."""
    about_text = (
        "🤖 **«VAZIFA BAJARADI» — Ingliz Tili AI Yordamchisi**\n\n"
        "O'quvchi va talabalarga ingliz tili darslarini a'lo baholarga o'zlashtirish, "
        "CEFR va IELTS imtihonlariga tayyorlanish hamda uy vazifalarini chuqur tushunib yechishda yordam beradi.\n\n"
        "🌟 **Afzalliklari:**\n"
        "• ⚡️ Qadamma-qadam o'zbek tilida tushuntirish\n"
        "• 🔊 Native inglizcha audio talaffuz (TTS)\n"
        "• 📚 Irregular verbs va barcha 12 zamon qoidalari\n"
        "• 📷 Multimodal Vision (rasmdagi vazifalarni yechish)\n"
        "• 🧠 Google Gemini 2.0 Flash & Llama-3.3 sun'iy intellekti\n\n"
        "Manzil: @uy_vazifa_bot"
    )
    await message.answer(about_text, parse_mode="Markdown")


@router.message(F.text == "❌ Bekor qilish")
async def cmd_cancel(message: Message, state: FSMContext):
    """Amalni bekor qilish va asosiy menyuga qaytish."""
    await state.clear()
    await message.answer("Amal bekor qilindi.", reply_markup=get_main_keyboard())
