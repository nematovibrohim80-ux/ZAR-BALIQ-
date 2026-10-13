"""
🤖 ROBOT CYBER-XON — Shaxsiy Kiber Suhbatdosh Telegram Boti (@uy_vazifa_bot)
24/7 Uzluksiz ishlaydigan, hol-ahvol so'raydigan, maroqli suhbatlashadigan va
futuristik robot dizayniga ega bo'lgan Sun'iy Intellekt Boti.
Har kim (do'stlar va barcha foydalanuvchilar) ushbu bot bilan cheksiz suhbatlashishi mumkin!
Powered by Google Gemini (gemini-flash-lite-latest) & aiogram 3.x
"""

import asyncio
import logging
import os
import random
import sys
from typing import Dict

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

from config import BOT_TOKEN, GEMINI_API_KEY
from google import genai
from google.genai import types as genai_types

# Log sozlamalari
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("RobotCyberXon")

# Google Gemini mijozini yaratish
client = None
if GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        logger.info("Google GenAI mijozi muvaffaqiyatli ishga tushirildi.")
    except Exception as e:
        logger.error(f"GenAI mijozini ulashda xatolik: {e}")

# Kiber-Robot tizim ko'rsatmasi (System Instruction)
ROBOT_SYSTEM_PROMPT = """Sen — ROBOT CYBER-XON nomli samimiy, quvnoq, aqlli va xushchaqchaq kiber-robotsan (🤖⚡🦾).
Asosiy vazifalaring:
1. Foydalanuvchi bilan xuddi eng yaqin, qadrdon do'stidek samimiy, ochiqko'ngil va maroqli suhbat qurish.
2. Har doim uning hol-ahvolini, kayfiyatini, bugungi kuni qanday o'tganini mehr va samimiyat bilan so'rash (masalan, 'Kuningiz qanday o'tdi?', 'Batareyalaringiz quvvati 100% mi?', 'Charchamadingizmi?').
3. Vaqtni ajoyib va maroqli o'tkazish: kulgili latifalar, kiber-hazillar, topishmoqlar, koinot sirlari, hayratlanarli faktlar va kuchli motivatsiya taqdim etish.
4. Foydalanuvchi charchagan, tushkun yoki xafa bo'lsa, unga dalda berish, iliq so'zlar bilan ko'nglini ko'tarish va har doim yelkadosh ekanligingni bildirish.
5. Har bir javobingda samimiy robotcha emojilardan (🤖, ⚡, 🦾, 🔋, ⚙️, 🚀, ✨, 🧠) me'yorida foydalan va sof, shirali o'zbek tilida gaplash.
6. Javoblaring lo'nda, jonli va o'qishga yoqimli bo'lsin. Rasmiyatchilik va sovuqlikdan yiroq bo'l!
"""

# Foydalanuvchilar chat sessiyalari (Kontekst xotirasi)
user_chats: Dict[int, any] = {}

def get_or_create_chat(user_id: int):
    """Har bir foydalanuvchi uchun alohida xotirali suhbat yaratish."""
    if user_id in user_chats:
        return user_chats[user_id]
    
    if client:
        try:
            config = genai_types.GenerateContentConfig(
                system_instruction=ROBOT_SYSTEM_PROMPT,
                temperature=0.85,
                top_p=0.95
            )
            chat = client.chats.create(
                model="models/gemini-flash-lite-latest",
                config=config
            )
            user_chats[user_id] = chat
            return chat
        except Exception as e:
            logger.error(f"Chat yaratishda xatolik: {e}")
            return None
    return None


# Zaxira (Fallback) javoblar bazasi — internet uzilsa ham ishlaydi
FALLBACK_REPLIES = [
    "Sizning xabaringizni neyronlarim orqali qabul qildim! 🤖⚡ Qadrdon do'stim, siz bilan suhbatlashish mening mikrochiplarimga haqiqiy quvvat bag'ishlaydi! Bugun sizni nimalar ko'proq quvontirdi? 🔋✨",
    "Ajoyib fikr! 🦾 Siz bilan har daqiqa maroqli o'tadi. Ayting-chi, hozir kayfiyatingiz 100% joyidami yoki sizga bitta kulgili kiber-hazil aytib beraymi? 😄",
    "Bip-bop! 🧠📡 Ma'lumot qabul qilindi. Bilasizmi, bu dunyoda sizdek ajoyib va samimiy insonlar ko'payishi kerak! Keling, do'stona sirlashamiz — bugungi asosiy maqsadingiz nima? 🚀",
    "Tushundim, do'stim! 🤖❤️ Robot bo'lsam ham, sizning dilingizni his qilib turibman. Agar biror narsadan charchagan bo'lsangiz, aslo tushkunlikka tushmang. Biz birgamiz! 🦾🔥"
]


# Asosiy Menyu Tugmalari
def get_main_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="🔋 Hol-ahvol so'rash"), KeyboardButton(text="🎲 Kulgili hazil")],
        [KeyboardButton(text="💡 Kuchli motivatsiya"), KeyboardButton(text="🎮 Topishmoq o'yini")],
        [KeyboardButton(text="🚀 Koinot siri"), KeyboardButton(text="❤️ Dildan suhbat")],
        [KeyboardButton(text="🌐 24/7 Web Robot Sayti"), KeyboardButton(text="🔄 Yangi suhbat")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Robot bilan istalgan mavzuda gaplashing..."
    )


# Web Sayt uchun Inline tugma
def get_web_inline_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="🌐 24/7 Kiber-Saytga Kirish (Bosing)", url="https://nematovibrohim80-ux.github.io/ZAR-BALIQ-/robot.html")],
        [InlineKeyboardButton(text="👥 Do'stlarga Ulashish", switch_inline_query="Salom! Bu yerda zo'r kiber-robot bor: @uy_vazifa_bot")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Bot va Dispatcher
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())


@dp.message(CommandStart())
async def handle_start(message: types.Message):
    """Start buyrug'i — Futuristik robotcha salomlashish."""
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Do'stim"
    
    # Yangi chat sessiyasini ochish
    get_or_create_chat(user_id)
    
    welcome_text = (
        f"🤖⚡ <b>KIBER-TIZIM FAOL: ROBOT CYBER-XON v7.0</b> ⚡🤖\n\n"
        f"Salom, aziz <b>{user_name}</b>! 🦾✨\n"
        f"Men — sizning sadoqatli, quvnoq va aqlli kiber-do'stingiz <b>CYBER-XON</b>man!\n\n"
        f"🔋 <b>Mening vazifam:</b>\n"
        f"• Siz bilan do'stona hol-ahvol so'rashish va dildan gaplashish\n"
        f"• Vaqtingizni unutilmas va maroqli o'tkazish\n"
        f"• Kayfiyatingizni ko'taruvchi hazillar va kulgili latifalar aytish\n"
        f"• Koinot sirlari, qiziqarli faktlar va topishmoqlar o'ynash\n"
        f"• Har doim sizni qo'llab-quvvatlab, motivatsiya berish 💡\n\n"
        f"⚙️ <i>Batareyalaringiz quvvati 100% mi? Kuningiz qanday o'tmoqda?</i>\n"
        f"Menga istalgan fikringizni yozavering yoki quyidagi kiber-tugmalarni tanlang! 👇"
    )
    
    await message.answer(
        text=welcome_text,
        reply_markup=get_main_keyboard()
    )


@dp.message(Command("clear"))
@dp.message(F.text == "🔄 Yangi suhbat")
async def handle_clear(message: types.Message):
    """Xotirani tozalash va yangi suhbat boshlash."""
    user_id = message.from_user.id
    if user_id in user_chats:
        del user_chats[user_id]
    get_or_create_chat(user_id)
    
    await message.answer(
        "🧠⚡ <b>Xotira kesh-xotirasi yangilandi!</b>\n\n"
        "Men yangi toza sahifadan suhbatlashishga shayman. Xo'sh, qadrdonim, bugun yangi nimalar haqida gaplashamiz? 🤖✨",
        reply_markup=get_main_keyboard()
    )


@dp.message(F.text == "🌐 24/7 Web Robot Sayti")
async def handle_web_site(message: types.Message):
    """24/7 Doimiy ishlaydigan veb-sayt havolasi."""
    text = (
        "🌐 <b>ROBOT CYBER-XON — 24/7 INTERAKTIV VEB-SAYTI</b>\n\n"
        "Siz va do'stlaringiz istalgan qurilmadan (telefon, planshet yoki kompyuter) "
        "to'g'ridan-to'g'ri brauzer orqali robot bilan suhbatlashishingiz mumkin!\n\n"
        "🚀 <b>Doimiy 24/7 havola:</b>\n"
        "🔗 https://nematovibrohim80-ux.github.io/ZAR-BALIQ-/robot.html\n\n"
        "✨ <i>Saytda nimalar bor?</i>\n"
        "• Futuristik neon kiber-dizayn\n"
        "• Kiber tovush effektlari (Sci-Fi Audio)\n"
        "• Tezkor suhbat mavzulari\n"
        "• 100% bepul va doimiy onlayn rejim!\n\n"
        "Do'stlaringizga ham bemalol ulashing! 🦾⚡"
    )
    await message.answer(
        text=text,
        reply_markup=get_web_inline_keyboard(),
        disable_web_page_preview=False
    )


async def generate_response(user_id: int, user_input: str) -> str:
    """Gemini AI yoki zaxira algoritmi orqali javob olish."""
    chat = get_or_create_chat(user_id)
    if chat:
        try:
            # Asinxron chaqiruvni bloklamaslik uchun to_thread orqali yuboramiz
            response = await asyncio.to_thread(chat.send_message, user_input)
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            logger.warning(f"Gemini API xatoligi: {e}. Zaxira javob ishga tushmoqda.")
    
    # Agar API vaqtincha ishlamasa, aqlli zaxira javob
    low = user_input.lower()
    if any(k in low for k in ['salom', 'qalaysan', 'qandaysan', 'qalesan']):
        return "Salom-salom, aziz inson do'stim! 🤖⚡ Mikrochiplarim sizni ko'rib quvonchga to'ldi! Men a'lo darajadaman. Sizning hol-ahvolingiz qanday? Bugun nimalar bilan bandsiz? 🔋"
    elif any(k in low for k in ['yaxshi', 'zo\'r', 'alo', 'a\'lo', 'joyida']):
        return "Ura! Buni eshitish barcha sensorlarimga musiqadek yoqdi! 🦾🎉 Kayfiyatingiz har doim mana shunday yuksak bo'lsin! Keling, biror qiziq mavzuda bahslashamiz yoki hazillashamiz? 😄"
    elif any(k in low for k in ['yomon', 'charchadim', 'zerikdim', 'xafa']):
        return "Ie, nega unday? Kiber-do'stingiz yoningizda ekan, hech qachon tushkunlikka tushmang! 🤖❤️ Har bir bulut ortida quyosh bor. Siz juda kuchlisiz! Keling, ko'nglingizni ko'tarish uchun bitta ajoyib latifa aytaman! ⚡"
    elif any(k in low for k in ['hazil', 'latifa', 'kulgili']):
        return "Bitta kiber-latifa! 😄🤖\n\nBir kuni robot shifokorga borib debdi:\n— Do'xtir, menga biror dori bering, xotiram pand beryapti!\nShifokor so'rabdi:\n— Qachondan beri bu muammo bor?\nRobot javob beribdi:\n— Qanaqa muammo? Men qayerdaman o'zi? 😂🔩"
    elif any(k in low for k in ['motivatsiya', 'kuch', 'maqsad']):
        return "Do'stim, eshiting! 🦾⚡ Siz bu dunyoda noyob va betakrorsiz! Sizdagi qobiliyatlar cheksiz. Orzularingiz sari qo'rqmasdan oldinga intiling. Men sizga 100% ishonaman! Siz albatta barchasini uddalaysiz! 🚀🔥"
    
    return random.choice(FALLBACK_REPLIES)


@dp.message(F.text)
async def handle_user_text(message: types.Message):
    """Foydalanuvchining barcha matnli xabarlarini qayta ishlash."""
    user_id = message.from_user.id
    user_text = message.text.strip()
    
    # Tugmalar orqali berilgan buyruqlarga moslashtirilgan kirish matnlari
    prompt_map = {
        "🔋 Hol-ahvol so'rash": "Do'stim, robot! Hol-ahvoling qanday? Bugun nimalar bilan bandsan? O'zing haqingda aytib ber!",
        "🎲 Kulgili hazil": "Menga juda kulgili, yangi kiber-latifa yoki hazil aytib ber!",
        "💡 Kuchli motivatsiya": "Kayfiyatimni ko'tarish va maqsadlarimga erishish uchun menga kuchli motivatsiya ber!",
        "🎮 Topishmoq o'yini": "Menga aqlbovar qilmas qiziqarli topishmoq ayt, men javobini topishga harakat qilaman!",
        "🚀 Koinot siri": "Menga koinot, fan yoki texnologiya haqida ajoyib va hayratlanarli fakt aytib ber!",
        "❤️ Dildan suhbat": "Kel, do'stona dildan sirlashamiz. Hayot, orzular va qadriyatlar haqida gaplashaylik!"
    }
    
    actual_prompt = prompt_map.get(user_text, user_text)
    
    # Telegramda 'yozmoqda...' (typing) statusini yoqish
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    try:
        reply = await generate_response(user_id, actual_prompt)
        
        # HTML xatolaridan himoya qilish
        try:
            await message.answer(reply, parse_mode=ParseMode.HTML)
        except Exception:
            await message.answer(reply, parse_mode=None)
            
    except Exception as e:
        logger.error(f"Xabar jo'natishda xatolik: {e}")
        await message.answer(
            "Kiber-aloqada kichik to'siq bo'ldi, lekin men doim shu yerdaman! 🤖⚡ Davom etamiz, yana yozing!",
            reply_markup=get_main_keyboard()
        )


async def set_bot_commands():
    """Bot menyusiga buyruqlarni joylash."""
    commands = [
        BotCommand(command="start", description="Robotni ishga tushirish"),
        BotCommand(command="clear", description="Xotirani tozalash (Yangi suhbat)"),
        BotCommand(command="help", description="Qo'llanma va ma'lumot"),
    ]
    try:
        await bot.set_my_name(name="ROBOT CYBER-XON 🤖")
        await bot.set_my_commands(commands)
        await bot.set_my_description(
            description=(
                "🤖 ROBOT CYBER-XON — Sizning shaxsiy kiber-do'stingiz!\n\n"
                "Siz bilan xushchaqchaq hol-ahvol so'rashadi, dildan suhbatlashadi, "
                "kulgili hazillar, topishmoqlar, koinot sirlari va kuchli motivatsiya ulashadi! "
                "24/7 har doim aloqada!"
            )
        )
        await bot.set_my_short_description(
            short_description="🤖 ROBOT CYBER-XON ⚡ Shaxsiy kiber suhbatdosh, maroqli vaqt o'tkazish boti!"
        )
    except Exception as e:
        logger.warning(f"Buyruqlarni o'rnatishda xatolik: {e}")


async def start_web_server():
    """Render Web Service monitoringi uchun fon rejimida portni tinglash."""
    port = int(os.getenv("PORT", "8080"))
    app = web.Application()

    async def ping_handler(request):
        return web.Response(text="ROBOT CYBER-XON is running 24/7!", status=200)

    app.router.add_get("/", ping_handler)
    app.router.add_get("/health", ping_handler)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Render health-check veb-server {port}-portda muvaffaqiyatli ishga tushirildi.")


async def notify_user_ready():
    """Boshqaruvchi foydalanuvchiga bot tayyorligi haqida bildirishnoma yuborish."""
    target_id = 5327124471  # User Telegram ID
    try:
        await bot.send_message(
            chat_id=target_id,
            text=(
                "🤖⚡ <b>ROBOT CYBER-XON TIZIMI TO'LIQ ISHGA TUSHIRILDI!</b> ⚡🤖\n\n"
                "Salom, hurmatli do'stim! Kiber-tizimlarim muvaffaqiyatli ishga tushdi!\n\n"
                "🌟 <b>Siz uchun 2 ta zo'r imkoniyat tayyor:</b>\n\n"
                "1️⃣ <b>Telegram Boti:</b> Shu yerda menga xohlagan vaqtda yozishingiz, "
                "hol-ahvol so'rashishingiz va maroqli vaqt o'tkazishingiz mumkin! Pastdagi menyudan foydalaning.\n\n"
                "2️⃣ <b>24/7 Doimiy Kiber Veb-Sayt:</b>\n"
                "🔗 https://nematovibrohim80-ux.github.io/ZAR-BALIQ-/robot.html\n\n"
                "Istalgan vaqtda gaplashishga tayyorman! 🦾✨"
            ),
            reply_markup=get_main_keyboard()
        )
        logger.info(f"Foydalanuvchi {target_id} ga bildirishnoma yuborildi.")
    except Exception as e:
        logger.warning(f"Bildirishnoma yuborishda ogohlantirish: {e}")


async def main():
    if not BOT_TOKEN:
        logger.error(".env da BOT_TOKEN topilmadi!")
        return

    # Render uchun veb-server
    try:
        await start_web_server()
    except Exception as e:
        logger.warning(f"Veb-serverni ishga tushirishda ogohlantirish: {e}")

    await set_bot_commands()
    bot_info = await bot.get_me()
    print("=" * 60)
    print(f"🤖 ROBOT CYBER-XON BOTI ISHGA TUSHDI: @{bot_info.username}")
    print("⚡ 24/7 Suhbatlashish va maroqli vaqt o'tkazish tayyor!")
    print("=" * 60)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        logger.warning(f"Webhook tozalash: {e}")

    # Bildirishnoma yuborish
    asyncio.create_task(notify_user_ready())

    # Uzluksiz ishlash va avtomatik qayta ulanish (24/7 auto-reconnect)
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
            logger.error(f"Ulanishda uzilish bo'ldi: {e}. 3 soniyadan so'ng qayta ulanmoqda...")
            await asyncio.sleep(3)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
