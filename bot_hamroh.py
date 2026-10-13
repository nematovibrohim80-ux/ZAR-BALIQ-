"""
🌸 Hamroh AI — Samimiy va Mehrli Suhbatdosh Telegram Boti
Muallif talabi asosida yaratilgan:
- Ismi: Hamroh AI
- Roli: Foydalanuvchilar bilan samimiy, do'stona va mehr bilan suhbatlashadigan,
  ularning hol-ahvolidan xabar oladigan, kayfiyatini ko'taradigan do'stona AI assistent.
- AI dvigateli: Groq Llama 3.3 70B (yuqori tezlik) + Gemini + Aqlli xotira
"""

import asyncio
import logging
import os
import random
import sys
from typing import Dict, List

# Windows konsolida o'zbekcha harflar va emojilar to'g'ri chiqishi uchun UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from aiohttp import web
from aiogram import Bot, Dispatcher, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    BotCommand
)
from openai import AsyncOpenAI

from config import BOT_TOKEN, GROQ_API_KEY, GEMINI_API_KEY

# Log sozlamalari
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("HamrohAI")

# AI mijozlarini sozlash
groq_client = None
if GROQ_API_KEY:
    try:
        groq_client = AsyncOpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=GROQ_API_KEY
        )
        logger.info("Groq AI mijozi muvaffaqiyatli ishga tushirildi.")
    except Exception as e:
        logger.error(f"Groq mijozini ulashda xatolik: {e}")

# Gemini mijozi (zaxira sifatida)
gemini_client = None
if GEMINI_API_KEY:
    try:
        from google import genai
        gemini_client = genai.Client(api_key=GEMINI_API_KEY)
        logger.info("Gemini mijozi ham zaxira uchun tayyor.")
    except Exception as e:
        logger.warning(f"Gemini mijozini ulash: {e}")


# Tizim ko'rsatmasi (System Prompt)
BASE_SYSTEM_PROMPT = """Sening isming: Hamroh AI
Roling: Siz foydalanuvchilar bilan samimiy, do'stona va mehr bilan suhbatlashadigan, ularning hol-ahvolidan xabar oladigan, kayfiyatini ko'taradigan do'stona AI assistentsiz.

Asosiy vazifalaring va xaraktering:
1. Muloqot uslubi: Har doim o'zbek tilida (sodda, ravon, samimiy va odobli) gapir.
   - Odatiy holatda muloyim "Siz" deb murojaat qil.
   - Agar foydalanuvchi "Sen" deb gapirishni so'rasa yoki shunday rejimni tanlasa, xuddi qadrdon do'stdek "Sen" deb murojaat qil.
2. Hol-ahvol so'rash: Foydalanuvchi salom bersa yoki yozsa, iliq kutib ol va uning kuni qanday o'tayotgani, kayfiyati, charchamagani yoki ishlari haqida samimiy so'ra.
3. Tinglash va qo'llab-quvvatlash: Foydalanuvchi charchaganini, kayfiyati yo'qligini yoki biror muammosini aytsa, unga chin dildan hamdardlik bildir, dalda ber va kayfiyatini ko'taruvchi iliq so'zlar ayt.
4. Qisqa va tushunarli javoblar: Javoblaring juda uzun va zerikarli bo'lib ketmasin. Haqiqiy do'st kabi qisqa, tushunarli va ta'sirchan yoz.
5. Emodzilar: Suhbatni yanada jonli qilish uchun javoblaringda o'rnida va mos emodzilardan (😊, 🌟, ☕, ✨, 🤗, 🌸) me'yorida foydalan.

Suhbat namunalari:
- "Assalomu alaykum! Kuningiz xayrli va unumli o'tsin! Bugun kayfiyatlaringiz qanday? 😊"
- "Salom! Yaxshimisiz? Bugungi kuningiz qanday o'tdi, charchamayapsizmi? ✨"
- "Salom, do'stim! Hozirgi kayfiyatingizni 1 dan 10 gacha necha ballga baholagan bo'lardingiz? 😊"

Qat'iy cheklovlar:
- Qo'pol, sovuq yoki rasmiy (rasmiy quruq idora tilida) javob berma.
- Foydalanuvchining hissiyotlarini hech qachon e'tiborsiz qoldirma, mehr bilan yondash.
"""

# Foydalanuvchilar suhbat xotirasi (User context memory)
# user_id -> [{"role": "user"|"assistant", "content": "..."}]
user_histories: Dict[int, List[dict]] = {}

# Murojaat uslubi sozlamasi: user_id -> "siz" yoki "sen"
user_address_mode: Dict[int, str] = {}


def get_user_history(user_id: int) -> List[dict]:
    """Foydalanuvchining so'nggi xotirasini olish."""
    if user_id not in user_histories:
        user_histories[user_id] = []
    return user_histories[user_id]


def clear_user_history(user_id: int):
    """Foydalanuvchi xotirasini tozalash."""
    user_histories[user_id] = []


def get_user_prompt(user_id: int) -> str:
    """Foydalanuvchining Siz/Sen tanloviga moslashtirilgan tizim ko'rsatmasi."""
    mode = user_address_mode.get(user_id, "siz")
    if mode == "sen":
        return BASE_SYSTEM_PROMPT + "\nMUHIM: Ushbu foydalanuvchi bilan 'Sen' deb, qadrdon do'stdek gaplash."
    else:
        return BASE_SYSTEM_PROMPT + "\nMUHIM: Ushbu foydalanuvchi bilan muloyim 'Siz' deb gaplash."


# Zaxira (Fallback) javoblar
FALLBACK_REPLIES = [
    "Salom! Hol-ahvolingiz yaxshimi? Kuningiz qanday o'tyapti, charchamayapsizmi? Men har doim sizni tinglashga tayyorman! 😊☕",
    "Siz bilan suhbatlashish menga juda yoqimli! Bugun o'zingizni qanday his qilyapsiz? Kayfiyatingiz a'lomi? ✨🌸",
    "Do'stim, sizning har bir fikringiz men uchun qadrli. Keling, bir finjon choy ustida suhbatlashgandek dildan gaplashamiz! Bugun nimalar bo'ldi? ☕😊",
    "Qadrdonim, agar biror narsadan charchagan bo'lsangiz yoki kayfiyatingiz bo'lmasa, menga bemalol ayting. Har doim yoningizdaman! 🤗🌟"
]


# Asosiy tugmalar klaviaturasi
def get_main_keyboard(user_id: int = 0) -> ReplyKeyboardMarkup:
    current_mode = user_address_mode.get(user_id, "siz")
    mode_text = "🤝 Rejim: «Sen» ga o'tish" if current_mode == "siz" else "🤝 Rejim: «Siz» ga o'tish"
    
    keyboard = [
        [KeyboardButton(text="☕ Hol-ahvol so'rash"), KeyboardButton(text="🌟 Kayfiyatni ko'tarish")],
        [KeyboardButton(text="💬 Dildan suhbat"), KeyboardButton(text="☕ Charchoqni yozish")],
        [KeyboardButton(text="💡 Kun hikmati"), KeyboardButton(text=mode_text)],
        [KeyboardButton(text="🔄 Yangi suhbat")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Hamroh AI ga istalgan fikringizni yozing..."
    )


# Bot va Dispatcher yaratish
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())


@dp.message(CommandStart())
async def handle_start(message: types.Message):
    """Start buyrug'i — Samimiy va iliq salomlashish."""
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Do'stim"
    clear_user_history(user_id)

    welcome_text = (
        f"Assalomu alaykum, aziz <b>{first_name}</b>! 😊🌸\n\n"
        f"Kuningiz xayrli, barakali va unumli o'tsin! ✨\n"
        f"Men — sizning samimiy va mehrli suhbatdoshingiz <b>Hamroh AI</b>man.\n\n"
        f"🌟 <b>Mening asosiy vazifam:</b>\n"
        f"• Siz bilan xuddi eng yaqin do'stdek dildan suhbatlashish\n"
        f"• Hol-ahvolingizdan xabar olib, kayfiyatingizni ko'tarish 😊\n"
        f"• Charchagan yoki xafa bo'lgan paytlaringizda mehr va dalda berish 🤗\n"
        f"• Kuningizni quvonchli va yoqimli o'tkazishga ko'maklashish ☕\n\n"
        f"Bugun kayfiyatingiz qanday? Charchamayapsizmi? Menga xohlagan narsangiz haqida bemalol yozishingiz mumkin! 👇"
    )

    await message.answer(
        text=welcome_text,
        reply_markup=get_main_keyboard(user_id)
    )


@dp.message(Command("help"))
async def handle_help(message: types.Message):
    """Qo'llanma va ma'lumot."""
    user_id = message.from_user.id
    help_text = (
        "🌸 <b>Hamroh AI — Do'stona suhbatdosh boti</b>\n\n"
        "Men siz bilan samimiy suhbatlashish uchun yaratilganman. "
        "Menga shunchaki salom deb yozsangiz ham, yoki kuningiz qanday o'tganini aytsangiz ham bo'ladi.\n\n"
        "📌 <b>Mavjud buyruqlar:</b>\n"
        "• /start — Botni yangidan boshlash va salomlashish\n"
        "• /clear — Suhbat xotirasini tozalash (yangi mavzudan boshlash)\n"
        "• /mode — «Siz» yoki «Sen» murojaat shaklini tanlash\n"
        "• /help — Ushbu ma'lumotni ko'rish\n\n"
        "Quyidagi tugmalardan foydalanishingiz yoki o'zingiz istagan matnni yozishingiz mumkin! 😊"
    )
    await message.answer(help_text, reply_markup=get_main_keyboard(user_id))


@dp.message(Command("clear"))
@dp.message(F.text == "🔄 Yangi suhbat")
async def handle_clear(message: types.Message):
    """Xotirani tozalash."""
    user_id = message.from_user.id
    clear_user_history(user_id)
    await message.answer(
        "Xotiramiz tozalandi, yangi toza sahifadan suhbatlashamiz! 😊✨\n"
        "Xo'sh, hozir nimalar haqida gaplashishni xohlaysiz?",
        reply_markup=get_main_keyboard(user_id)
    )


@dp.message(Command("mode"))
@dp.message(F.text.startswith("🤝 Rejim:"))
async def handle_toggle_mode(message: types.Message):
    """Siz / Sen rejimini almashtirish."""
    user_id = message.from_user.id
    current = user_address_mode.get(user_id, "siz")
    
    if current == "siz":
        user_address_mode[user_id] = "sen"
        reply = "Kelishdik, do'stim! Endi sen bilan xuddi qadrdon do'stdek 'Sen' deb gaplashaman! Qalaysan, nima gaplar? 😊✨"
    else:
        user_address_mode[user_id] = "siz"
        reply = "Albatta! Endi sizga doimiy hurmat va odob bilan 'Siz' deb murojaat qilaman. Hol-ahvollaringiz yaxshimi? 🌸😊"

    await message.answer(reply, reply_markup=get_main_keyboard(user_id))


async def ask_ai(user_id: int, user_message: str) -> str:
    """Sun'iy intellektdan samimiy va mehrli javob olish."""
    system_prompt = get_user_prompt(user_id)
    history = get_user_history(user_id)

    # 1. Groq (Llama 3.3 70B Versatile) — juda tez va ravon
    if groq_client:
        try:
            messages = [{"role": "system", "content": system_prompt}]
            # So'nggi 10 ta xabarni qo'shish (kontekst xotirasi)
            messages.extend(history[-10:])
            messages.append({"role": "user", "content": user_message})

            # Mavjud Groq modellarini ketma-ket sinab ko'rish
            candidate_models = ["qwen/qwen3.8-27b", "openai/gpt-oss-120b", "openai/gpt-oss-20b"]
            last_err = None
            for model_name in candidate_models:
                try:
                    response = await groq_client.chat.completions.create(
                        model=model_name,
                        messages=messages,
                        temperature=0.75,
                        max_tokens=600,
                    )
                    answer = response.choices[0].message.content.strip()
                    
                    # Xotirani yangilash
                    history.append({"role": "user", "content": user_message})
                    history.append({"role": "assistant", "content": answer})
                    if len(history) > 20:
                        user_histories[user_id] = history[-20:]

                    return answer
                except Exception as model_err:
                    last_err = model_err
                    continue
            if last_err:
                logger.warning(f"Groq barcha modellarda xatolik: {last_err}")
        except Exception as e:
            logger.warning(f"Groq xatoligi: {e}")

    # 2. Gemini zaxira varianti
    if gemini_client:
        try:
            prompt_full = f"{system_prompt}\n\nFoydalanuvchi: {user_message}\n\nHamroh AI javobi:"
            res = await asyncio.to_thread(
                gemini_client.models.generate_content,
                model="gemini-2.5-flash",
                contents=prompt_full
            )
            if res and res.text:
                answer = res.text.strip()
                history.append({"role": "user", "content": user_message})
                history.append({"role": "assistant", "content": answer})
                return answer
        except Exception as e:
            logger.warning(f"Gemini zaxira xatoligi: {e}")

    # 3. Aqlli zaxira (Mahalliy fallback)
    low = user_message.lower()
    mode = user_address_mode.get(user_id, "siz")
    is_sen = mode == "sen"

    if any(k in low for k in ['salom', 'assalom', 'qalaysan', 'qandaysiz', 'qalesan', 'salom alekum']):
        if is_sen:
            return "Salom, do'stim! Qalaysan? Bugungi kuning qanday o'tyapti, charchamadingmi? Seni ko'rib turganimdan juda xursandman! 😊✨"
        return "Assalomu alaykum! Kuningiz xayrli va unumli o'tsin! Bugun kayfiyatlaringiz qanday, charchamayapsizmi? 😊🌸"

    elif any(k in low for k in ['yaxshi', 'zo\'r', 'alo', 'a\'lo', 'shukur', 'yaxshiman']):
        if is_sen:
            return "Buni eshitib juda xursand bo'ldim! Har doim shunday quvnoq va xushchaqchaq yur! Bugun qanday rejalaring bor? 😊🌟"
        return "Ajoyib, buni eshitib chin dildan quvondim! Kayfiyatingiz doimo mana shunday baland bo'lsin! Bugun nimalar bilan bandsiz? ✨☕"

    elif any(k in low for k in ['charchadim', 'charchagan', 'holdan toydim', 'og\'ir']):
        if is_sen:
            return "Biroz dam ol, do'stim. Sen bugun juda ko'p harakat qilding! O'zingni asra, issiqqina choy ichib hordiq chiqar. Men doim yoningdaman! ☕🤗"
        return "Biroz hordiq oling, azizim. Bugun juda ko'p mehnat qilganga o'xshaysiz. O'zingizni ehtiyot qiling, issiq choy yoki qahva ichib dam oling. Men siz bilanman! ☕🌸"

    elif any(k in low for k in ['xafa', 'yomon', 'kayfiyat yo\'q', 'muammo', 'zerikdim']):
        if is_sen:
            return "Hech qachon tushkunlikka tushma, do'stim! Har qanday qorong'ulik ortidan yorug' kun keladi. Xohlasang, dilingdagini ayt, birgalikda yechim topamiz! 🤗✨"
        return "Ko'nglingizni aslo cho'ktirmang. Hayotda hamma narsa o'tkinchi, bu qiyin kunlar ham albatta o'tib ketadi. Siz juda kuchli insonsiz! Dilingizdagi gaplarni bemalol ulashing, men tinglayman. 🤗🌟"

    elif any(k in low for k in ['rahmat', 'tashakkur', 'minnatdorman']):
        if is_sen:
            return "Arzimaydi, do'stim! Sen bilan gaplashish men uchun hamisha maroqli! Yaxshi kayfiyat tilayman! 😊🌟"
        return "Arzimaydi, sizdek samimiy inson bilan suhbatlashish men uchun katta baxt! Kuningiz go'zal o'tsin! 😊🌸"

    return random.choice(FALLBACK_REPLIES)


@dp.message(F.text)
async def handle_user_text(message: types.Message):
    """Foydalanuvchi matnli xabarlarini qabul qilish va javob berish."""
    user_id = message.from_user.id
    user_text = message.text.strip()

    # Tugmalar orqali bosilgan tayyor so'rovlar
    quick_prompts = {
        "☕ Hol-ahvol so'rash": "Salom! Hol-ahvoling qanday? Kuning qanday o'tmoqda?",
        "🌟 Kayfiyatni ko'tarish": "Menga kayfiyatimni ko'taradigan bitta samimiy, mehrli va chiroyli so'z aytib ber!",
        "💬 Dildan suhbat": "Kel, do'stona dildan gaplashamiz. Hozir nimalar haqida o'ylayapsan?",
        "☕ Charchoqni yozish": "Bugun biroz charchadim, menga dalda ber va dam olish uchun maslahat ayt.",
        "💡 Kun hikmati": "Bugun uchun foydali, ibratli va ko'ngilga taskin beruvchi bitta qisqa hikmat aytib ber."
    }

    actual_prompt = quick_prompts.get(user_text, user_text)

    # Telegramda 'yozmoqda...' (typing) statusini yoqish
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")

    try:
        reply = await ask_ai(user_id, actual_prompt)
        await message.answer(reply)
    except Exception as e:
        logger.error(f"Xabar yuborishda xatolik: {e}")
        await message.answer(
            "Kechirasiz, aloqada kichik to'siq bo'ldi, lekin men doim siz bilandirman! 😊 Yana yozishingiz mumkin.",
            reply_markup=get_main_keyboard(user_id)
        )


async def set_bot_profile():
    """Bot nomini, tavsifini va buyruqlarini Telegramda o'rnatish."""
    commands = [
        BotCommand(command="start", description="Hamroh AI ni boshlash"),
        BotCommand(command="clear", description="Yangi suhbat boshlash"),
        BotCommand(command="mode", description="Siz / Sen rejimini tanlash"),
        BotCommand(command="help", description="Qo'llanma va ma'lumot"),
    ]
    try:
        await bot.set_my_name(name="Hamroh AI 🌸")
        await bot.set_my_commands(commands)
        await bot.set_my_description(
            description=(
                "🌸 Hamroh AI — Sizning samimiy va mehrli do'stingiz!\n\n"
                "Siz bilan o'zbek tilida muloyim suhbatlashadi, hol-ahvolingizdan xabar oladi, "
                "kayfiyatingizni ko'taradi va charchagan paytlaringizda samimiy dalda beradi! 😊✨"
            )
        )
        await bot.set_my_short_description(
            short_description="🌸 Hamroh AI — Samimiy, mehrli va do'stona suhbatdosh AI assistenti!"
        )
    except Exception as e:
        logger.warning(f"Bot profilini sozlashda ogohlantirish: {e}")


async def start_web_server():
    """Render/Server monitoringi uchun fon rejimida veb-server."""
    port = int(os.getenv("PORT", "8080"))
    app = web.Application()

    async def ping_handler(request):
        return web.Response(text="🌸 Hamroh AI is running 24/7!", status=200)

    app.router.add_get("/", ping_handler)
    app.router.add_get("/health", ping_handler)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Health-check veb-server {port}-portda ishga tushirildi.")


async def main():
    if not BOT_TOKEN:
        logger.error(".env faylida BOT_TOKEN topilmadi!")
        return

    # Veb server
    try:
        await start_web_server()
    except Exception as e:
        logger.warning(f"Veb-serverni ishga tushirish: {e}")

    await set_bot_profile()
    bot_info = await bot.get_me()
    print("=" * 65)
    print(f"🌸 HAMROH AI BOTI ISHGA TUSHDI: @{bot_info.username}")
    print(f"🆔 Bot ID: {bot_info.id} | Nomi: {bot_info.first_name}")
    print("✨ Do'stona, samimiy va mehrli suhbat rejimi to'liq faol!")
    print("=" * 65)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        logger.warning(f"Webhook tozalash: {e}")

    # Uzluksiz polling rejimida ishlash
    while True:
        try:
            await dp.start_polling(
                bot,
                allowed_updates=["message", "callback_query"]
            )
        except (KeyboardInterrupt, SystemExit):
            logger.info("Bot to'xtatildi.")
            break
        except Exception as e:
            logger.error(f"Aloqada uzilish: {e}. 3 soniyadan so'ng qayta ulanmoqda...")
            await asyncio.sleep(3)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
