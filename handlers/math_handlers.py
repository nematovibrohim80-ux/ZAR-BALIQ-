"""
Matematika Boti xabarlar, rasmlar va buyruqlar ishlovchisi (Handlers).
Barcha javoblar o'zbek tilida, qadamma-qadam va qotishlarsiz taqdim etiladi.
Qo'llab-quvvatlaydi:
- Matnli matematik ifodalar va tenglamalar (0.01s SymPy dvigateli)
- Rasm orqali misol yechish (F.photo Vision AI)
- Matnli masalalar (Word problems)
- Barcha menyu va shpargalka tugmalari
"""

import io
import base64
import asyncio
import logging
import re
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from openai import AsyncOpenAI

from keyboards.math_keyboards import (
    get_math_main_keyboard,
    get_formulas_inline_keyboard,
    get_examples_inline_keyboard,
    get_solution_action_keyboard
)
from services.math_engine import (
    solve_general_math,
    solve_quadratic_equation,
    solve_linear_equation,
    solve_fraction_expression,
    solve_derivative,
    solve_integral,
    calculate_geometry,
    is_likely_math
)
from config import POLLINATIONS_API_KEY, GEMINI_API_KEY

logger = logging.getLogger(__name__)
router = Router()

# AI Client for Word Problems and Vision
ai_client = AsyncOpenAI(
    api_key=POLLINATIONS_API_KEY or GEMINI_API_KEY or "dummy_key",
    base_url="https://text.pollinations.ai/openai"
)

# /start buyrug'i
@router.message(CommandStart())
async def cmd_start(message: Message):
    logger.info(f"[/start] Foydalanuvchi: {message.from_user.id} (@{message.from_user.username})")
    text = (
        "Assalomu alaykum! 📐 <b>MATEMATIKA UY VAZIFASI BOTIGA XUSH KELIBSIZ!</b>\n\n"
        "Men matematikadan har qanday misol, tenglama va topshiriqlarni <b>nuqsonsiz, "
        "qotishlarsiz va qadamma-qadam</b> yechib beraman.\n\n"
        "⚡ <b>Nimani yechib bera olaman:</b>\n"
        "• <b>Tenglamalar:</b> <code>2x + 8 = 20</code> yoki <code>x² - 5x + 6 = 0</code>\n"
        "• <b>Kasrlar:</b> <code>3/4 + 5/6 - 1/2</code>\n"
        "• <b>Arifmetika:</b> <code>(25 * 4 - 20) / 8 + 3^3</code>\n"
        "• <b>Qavslarni ochish:</b> <code>(x + 5)^2</code> yoki <code>x^2 - 16</code>\n"
        "• <b>Hosilalar:</b> <code>hosila 3x^3 - 5x^2 + 2x</code>\n"
        "• <b>Integrallar:</b> <code>integral 3x^2 + 4x</code>\n"
        "• <b>Tenglamalar sistemasi:</b> <code>2x + y = 10, x - y = 2</code>\n"
        "• <b>Geometriya:</b> Yuzalar, perimetr, Pifagor va doira\n"
        "• <b>📷 Rasm orqali:</b> Daftardagi misolni rasmga olib yuboring!\n\n"
        "👇 <i>Misolni yozing yoki quyidagi tugmalardan birini bosing:</i>"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=get_math_main_keyboard())


# /help yoki Yordam
@router.message(Command("help"))
@router.message(F.text == "❓ Yordam & Misollar")
async def cmd_help(message: Message):
    text = (
        "❓ <b>BOTDAN FOYDALANISH VA MISOLLAR:</b>\n\n"
        "Botdan foydalanish nihoyatda oson. Shunchaki misolni klaviaturada qanday bo'lsa, "
        "shunday yozib yuboring:\n\n"
        "📌 <b>Misollar:</b>\n"
        "1) <code>2x + 7 = 19</code> (chiziqli tenglama)\n"
        "2) <code>x^2 - 7x + 12 = 0</code> (kvadrat tenglama)\n"
        "3) <code>3/4 + 2/5</code> (kasrlar)\n"
        "4) <code>(x + 4)^2</code> (qisqa ko'paytirish)\n"
        "5) <code>hosila 4x^3 - 6x</code> (hosila)\n"
        "6) <code>integral 6x^2 + 2x</code> (integral)\n\n"
        "Quyidagi tugmalardan birini bosib tezkor sinab ko'rishingiz mumkin:"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=get_examples_inline_keyboard())


# Formulalar shpargalkasi
@router.message(Command("formulas"))
@router.message(F.text == "📖 Matematika Shpargalkasi")
async def cmd_formulas(message: Message):
    text = (
        "📖 <b>MATEMATIKA FORMULALARI VA SHPARGALKA:</b>\n\n"
        "O'zingizga kerakli formulalar bo'limini tanlang:"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=get_formulas_inline_keyboard())


# Bo'lim tugmalari
@router.message(F.text == "🧮 Ifodalar / Kalkulyator")
async def btn_calc(message: Message):
    text = (
        "🧮 <b>ARIFMETIK IFODA VA KALKULYATOR</b>\n\n"
        "Istalgan ifodani yuboring. Qo'llab-quvvatlanadi: <code>+</code>, <code>-</code>, "
        "<code>*</code>, <code>/</code>, <code>^</code> (daraja), <code>sqrt</code> (ildiz).\n\n"
        "Misol: <code>(15 + 25) * 4 / 2 + sqrt(144)</code>"
    )
    await message.answer(text, parse_mode="HTML")


@router.message(F.text == "📐 Tenglamani Yechish")
async def btn_equation(message: Message):
    text = (
        "📐 <b>CHIZIQLI TENGLAMANI YECHISH</b>\n\n"
        "Tenglamangizni yuboring. Bot uni qadamma-qadam tushuntirib, tekshirib beradi.\n\n"
        "Misol: <code>3x + 15 = 45</code> yoki <code>5(x - 2) = 20</code>"
    )
    await message.answer(text, parse_mode="HTML")


@router.message(F.text == "📊 Kvadrat Tenglama (D)")
async def btn_quadratic(message: Message):
    text = (
        "📊 <b>KVADRAT TENGLAMALARNI YECHISH</b>\n\n"
        "Kvadrat tenglamangizni yuboring. Bot <b>Diskriminant (D)</b> va <b>Viet teoremasi</b> "
        "bo'yicha to'liq bosqichma-bosqich yechib beradi.\n\n"
        "Misol: <code>x^2 - 5x + 6 = 0</code> yoki <code>2x^2 + 5x - 3 = 0</code>"
    )
    await message.answer(text, parse_mode="HTML")


@router.message(F.text == "🔢 Kasrlar bilan Amallar")
async def btn_fractions(message: Message):
    text = (
        "🔢 <b>KASRLAR BILAN AMALLAR</b>\n\n"
        "Oddiy yoki o'nli kasrlar ifodasini yuboring. Bot umumiy maxrajga keltirib, "
        "aniq qisqarmas kasr va aralash kasr ko'rinishida yechib beradi.\n\n"
        "Misol: <code>3/4 + 5/6 - 1/3</code> yoki <code>(2/3) * (9/4)</code>"
    )
    await message.answer(text, parse_mode="HTML")


@router.message(F.text == "📈 Hosila va Integral")
async def btn_calculus(message: Message):
    text = (
        "📈 <b>HOSILA VA INTEGRAL HISOBLASH</b>\n\n"
        "Funksiyaning hosilasi yoki integralini topish uchun:\n\n"
        "• <b>Hosila:</b> <code>hosila 3x^3 - 4x^2 + 7x</code>\n"
        "• <b>Integral:</b> <code>integral 3x^2 + 2x - 5</code>"
    )
    await message.answer(text, parse_mode="HTML")


@router.message(F.text == "📐 Geometriya Hisoblagich")
async def btn_geometry(message: Message):
    text = (
        "📐 <b>GEOMETRIK SHAKLLARNI HISOBLASH</b>\n\n"
        "Shakllar yuzi, perimetri va parametrlarini hisoblash uchun quyidagi formatda yozing:\n\n"
        "• <b>Uchburchak:</b> <code>uchburchak a=6 b=8 c=10</code>\n"
        "• <b>Aylana/Doira:</b> <code>doira r=5</code>\n"
        "• <b>To'rtburchak:</b> <code>tortburchak a=4 b=7</code>"
    )
    await message.answer(text, parse_mode="HTML")


# Eski bot tugmalariga javob (orqaga moslik)
@router.message(F.text.in_({"✏️ Yangi vazifa yechish", "📚 Fanlar", "📚 Boshqa fanlar", "🇬🇧 Ingliz tili vazifasi", "📷 Rasm orqali vazifa yechish"}))
async def btn_legacy(message: Message):
    await message.answer(
        "📐 <b>Matematika rejimidasiz!</b>\n\n"
        "Istalgan misol, tenglama yoki ifodangizni yuboring (yoki misol rasmini tashlang):",
        parse_mode="HTML",
        reply_markup=get_math_main_keyboard()
    )


# RASM ORQALI VAZIFA YECHISH (F.photo)
@router.message(F.photo)
async def handle_math_photo(message: Message, bot: Bot):
    logger.info(f"[PHOTO] Foydalanuvchi: {message.from_user.id} rasm yubordi.")
    wait_msg = await message.answer("📷 <i>Rasm qabul qilindi. Sun'iy intellekt misolni o'qimoqda va yechmoqda... ⏳</i>", parse_mode="HTML")

    try:
        # Eng katta sifatli rasmni yuklab olish
        photo = message.photo[-1]
        file_io = io.BytesIO()
        await bot.download(photo, destination=file_io)
        file_bytes = file_io.getvalue()
        b64_img = base64.b64encode(file_bytes).decode('utf-8')

        caption = message.caption or "Ushbu rasmdagi matematika topshirig'ini aniqlang va uni o'zbek tilida qadamma-qadam to'liq yechib bering."

        prompt_messages = [
            {
                "role": "system",
                "content": (
                    "Siz O'zbekistondagi eng kuchli matematika o'qituvchisisiz. "
                    "Rasmdagi har bir matematik misol, tenglama yoki masalani aniqlang va "
                    "uni O'ZBEK TILIDA, qadamma-qadam, qoidalar, formulalar va tekshiruvi bilan "
                    "chiroyli va to'liq yechib bering."
                )
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": caption},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
                ]
            }
        ]

        response = await ai_client.chat.completions.create(
            model="openai",
            messages=prompt_messages,
            timeout=25
        )

        ans = response.choices[0].message.content
        await wait_msg.delete()
        await message.answer(ans, reply_markup=get_solution_action_keyboard())

    except Exception as e:
        logger.error(f"Rasm tahlilida xatolik: {e}")
        await wait_msg.edit_text(
            "⚠️ <i>Rasmdagi misolni avtomatik o'qishda xatolik yuz berdi. "
            "Iltimos, misolni matn ko'rinishida yozib yuboring (masalan: <code>2x + 8 = 20</code>).</i>",
            parse_mode="HTML"
        )


# Callback query: Formulalar ko'rish
@router.callback_query(F.data.startswith("formula_"))
async def callback_formula(call: CallbackQuery):
    data = call.data
    text = ""

    if data == "formula_short_mult":
        text = (
            "📐 <b>QISQA KO'PAYTIRISH FORMULALARI:</b>\n\n"
            "1. Yig'indining kvadrati:\n"
            "   <code>(a + b)² = a² + 2ab + b²</code>\n\n"
            "2. Ayirmaning kvadrati:\n"
            "   <code>(a - b)² = a² - 2ab + b²</code>\n\n"
            "3. Kvadratlar ayirmasi:\n"
            "   <code>a² - b² = (a - b)(a + b)</code>\n\n"
            "4. Yig'indining kubi:\n"
            "   <code>(a + b)³ = a³ + 3a²b + 3ab² + b³</code>\n\n"
            "5. Ayirmaning kubi:\n"
            "   <code>(a - b)³ = a³ - 3a²b + 3ab² - b³</code>\n\n"
            "6. Kublar yig'indisi:\n"
            "   <code>a³ + b³ = (a + b)(a² - ab + b²)</code>\n\n"
            "7. Kublar ayirmasi:\n"
            "   <code>a³ - b³ = (a - b)(a² + ab + b²)</code>"
        )
    elif data == "formula_quadratic":
        text = (
            "📊 <b>KVADRAT TENGLAMA VA VIET TEOREMASI:</b>\n\n"
            "Tenglama ko'rinishi: <code>ax² + bx + c = 0</code>\n\n"
            "📌 <b>Diskriminant:</b>\n"
            "<code>D = b² - 4ac</code>\n\n"
            "• Agar <code>D > 0</code>: 2 ta haqiqiy ildiz:\n"
            "  <code>x₁,₂ = (-b ± √D) / (2a)</code>\n"
            "• Agar <code>D = 0</code>: 1 ta ildiz:\n"
            "  <code>x = -b / (2a)</code>\n"
            "• Agar <code>D < 0</code>: Haqiqiy ildiz yo'q (∅)\n\n"
            "📌 <b>Viet teoremasi (a = 1 bo'lganda):</b>\n"
            "<code>x₁ + x₂ = -b</code>\n"
            "<code>x₁ · x₂ = c</code>"
        )
    elif data == "formula_geometry":
        text = (
            "🔺 <b>GEOMETRIYA YUZALARI VA FORMULALARI:</b>\n\n"
            "1. <b>Uchburchak yuzi:</b>\n"
            "   • <code>S = (a · h) / 2</code>\n"
            "   • Geron formulasi: <code>S = √(p(p-a)(p-b)(p-c))</code>\n"
            "   • Pifagor teoremasi: <code>c² = a² + b²</code>\n\n"
            "2. <b>To'g'ri to'rtburchak:</b>\n"
            "   • Yuzi: <code>S = a · b</code>\n"
            "   • Perimetri: <code>P = 2(a + b)</code>\n\n"
            "3. <b>Doira va Aylana:</b>\n"
            "   • Yuzi: <code>S = πR²</code>\n"
            "   • Aylana uzunligi: <code>L = 2πR</code>\n\n"
            "4. <b>Trapetsiya:</b>\n"
            "   • <code>S = ((a + b) / 2) · h</code>"
        )
    elif data == "formula_trig":
        text = (
            "🌐 <b>ASOSIY TRIGONOMETRIYA FORMULALARI:</b>\n\n"
            "1. Asosiy ayniyat:\n"
            "   <code>sin²α + cos²α = 1</code>\n\n"
            "2. Tangens va Kotangens:\n"
            "   <code>tg α = sin α / cos α</code>\n"
            "   <code>ctg α = cos α / sin α</code>\n"
            "   <code>tg α · ctg α = 1</code>\n\n"
            "3. Mashhur burchaklar qiymati:\n"
            "   • <code>sin 30° = 1/2</code>, <code>cos 30° = √3/2</code>\n"
            "   • <code>sin 45° = √2/2</code>, <code>cos 45° = √2/2</code>\n"
            "   • <code>sin 60° = √3/2</code>, <code>cos 60° = 1/2</code>\n"
            "   • <code>tg 45° = 1</code>"
        )
    elif data == "formula_calculus":
        text = (
            "📈 <b>HOSILA VA INTEGRAL JADVALI:</b>\n\n"
            "📌 <b>Hosilalar:</b>\n"
            "• <code>(C)' = 0</code>\n"
            "• <code>(x)' = 1</code>\n"
            "• <code>(xⁿ)' = n · xⁿ⁻¹</code>\n"
            "• <code>(sin x)' = cos x</code>\n"
            "• <code>(cos x)' = -sin x</code>\n"
            "• <code>(eˣ)' = eˣ</code>\n"
            "• <code>(ln x)' = 1/x</code>\n\n"
            "📌 <b>Integrallar:</b>\n"
            "• <code>∫ xⁿ dx = (xⁿ⁺¹) / (n+1) + C</code>\n"
            "• <code>∫ cos x dx = sin x + C</code>\n"
            "• <code>∫ sin x dx = -cos x + C</code>\n"
            "• <code>∫ (1/x) dx = ln|x| + C</code>"
        )

    await call.message.edit_text(text, parse_mode="HTML", reply_markup=get_formulas_inline_keyboard())
    await call.answer()


# Callback query: Misollarni ko'rish
@router.callback_query(F.data == "show_math_examples")
async def callback_examples(call: CallbackQuery):
    await call.message.edit_text(
        "💡 <b>Sinab ko'rish uchun misollardan birini tanlang:</b>",
        parse_mode="HTML",
        reply_markup=get_examples_inline_keyboard()
    )
    await call.answer()


@router.callback_query(F.data == "open_formulas")
async def callback_open_formulas(call: CallbackQuery):
    await call.message.answer(
        "📖 <b>MATEMATIKA FORMULALARI VA SHPARGALKA:</b>",
        parse_mode="HTML",
        reply_markup=get_formulas_inline_keyboard()
    )
    await call.answer()


# Callback query: Tayyor misol yechish
@router.callback_query(F.data.startswith("ex_"))
async def callback_solve_example(call: CallbackQuery):
    ex_type = call.data
    sample_text = ""

    if ex_type == "ex_linear":
        sample_text = "2x + 8 = 20"
    elif ex_type == "ex_quad":
        sample_text = "x^2 - 5x + 6 = 0"
    elif ex_type == "ex_fraction":
        sample_text = "3/4 + 5/6 - 1/2"
    elif ex_type == "ex_expand":
        sample_text = "(x + 3)^2"
    elif ex_type == "ex_derivative":
        sample_text = "hosila 3x^3 - 5x^2 + 2x"
    elif ex_type == "ex_integral":
        sample_text = "integral 3x^2 + 4x"

    if sample_text:
        res = solve_general_math(sample_text)
        if res:
            await call.message.answer(res, parse_mode="HTML", reply_markup=get_solution_action_keyboard(sample_text))
    await call.answer()


# UNIVERSAL MATEMATIKA VA MATNLI MASALALAR ISHLOVCHISI
@router.message(F.text)
async def handle_math_message(message: Message):
    raw_text = message.text.strip()
    logger.info(f"[MSG] Foydalanuvchi {message.from_user.id} (@{message.from_user.username}): '{raw_text}'")

    # Salomlashish yoki tabriklar
    if raw_text.lower() in ["salom", "assalom", "assalomu alaykum", "qalaysiz", "start", "/start", "hello"]:
        await cmd_start(message)
        return

    # 1. Geometriya tekshiruvi (uchburchak a=6 b=8 c=10)
    low = raw_text.lower()
    if any(s in low for s in ['uchburchak', 'doira', 'aylana', 'tortburchak']) and '=' in raw_text:
        parts = raw_text.split()
        shape = parts[0]
        params = {}
        for p in parts[1:]:
            if '=' in p:
                k, v = p.split('=', 1)
                try:
                    params[k.strip().lower()] = float(v.strip())
                except ValueError:
                    pass
        geo_res = calculate_geometry(shape, params)
        await message.answer(geo_res, parse_mode="HTML", reply_markup=get_solution_action_keyboard())
        return

    # 2. Mahalliy SymPy dvigateli orqali hisoblash (0.01 soniya, 100% qotishlarsiz)
    if is_likely_math(raw_text):
        solution = await asyncio.to_thread(solve_general_math, raw_text)
        if solution:
            await message.answer(
                solution,
                parse_mode="HTML",
                reply_markup=get_solution_action_keyboard(raw_text)
            )
            return

    # 3. Agar matnli masala bo'lsa (masalan: "Hovuzga 2 ta quvur ulangan...", "Tezlik masalasi..."):
    # AI orqali 0 qotish bilan yechib berish
    if len(raw_text) > 8:
        wait_msg = await message.answer("🤔 <i>Masala tahlil qilinmoqda va yechilmoqda... ⏳</i>", parse_mode="HTML")
        try:
            res = await ai_client.chat.completions.create(
                model="openai",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Siz tajribali matematika ustozi (AI Math Tutor)siz. "
                            "Berilgan matematika masalasi yoki topshiriqni O'ZBEK TILIDA qadamma-qadam, "
                            "formulalar va tushuntirishlar bilan aniq va chiroyli qilib yechib bering."
                        )
                    },
                    {"role": "user", "content": raw_text}
                ],
                timeout=15
            )
            ans = res.choices[0].message.content
            await wait_msg.delete()
            await message.answer(ans, reply_markup=get_solution_action_keyboard())
            return
        except Exception as e:
            logger.warning(f"AI yechishda timeout yoki xatolik: {e}")
            await wait_msg.delete()

    # 4. Yordam ko'rsatish
    hint_text = (
        "🔍 <b>Misolni qanday yozish kerak:</b>\n\n"
        "• Tenglama: <code>2x + 8 = 20</code> yoki <code>x^2 - 5x + 6 = 0</code>\n"
        "• Ifoda: <code>(15 + 25) * 4 / 2</code>\n"
        "• Kasr: <code>3/4 + 5/6</code>\n"
        "• Hosila: <code>hosila 3x^2 - 5x</code>\n"
        "• Integral: <code>integral 4x^3 + 2x</code>\n"
        "• Rasm: Daftaringizdagi misolni rasmga olib yuborishingiz ham mumkin!\n\n"
        "💡 <i>Misolni yuboring yoki quyidagi misollardan birini tanlang:</i>"
    )
    await message.answer(hint_text, parse_mode="HTML", reply_markup=get_examples_inline_keyboard())
