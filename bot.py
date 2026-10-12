"""
«VAZIFA BAJARADI» (@uy_vazifa_bot) — Asosiy ishga tushirish fayli.
aiogram 3.x asosidagi Ingliz tili va barcha fanlar bo'yicha Sun'iy Intellektli Uy Vazifasi Boti.
"""

import asyncio
import logging
import os
import sys

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from config import BOT_TOKEN
from database.db import init_db

from handlers.common_handlers import router as common_router
from handlers.subject_handlers import router as subject_router
from handlers.stats_handlers import router as stats_router
from handlers.admin_handlers import router as admin_router
from handlers.homework_handlers import router as homework_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


async def set_default_commands(bot: Bot):
    """Telegram menyu buyruqlari va bot profil ma'lumotlarini o'rnatish."""
    commands = [
        BotCommand(command="start", description="Botni ishga tushirish"),
        BotCommand(command="solve", description="Ingliz tili vazifasini yechish"),
        BotCommand(command="essay", description="Insho yozish / tekshirish"),
        BotCommand(command="rules", description="Qoidalar & Noto'g'ri fe'llar"),
        BotCommand(command="quiz", description="Grammatika testi (Quiz)"),
        BotCommand(command="setkey", description="AI API kalitini sozlash"),
        BotCommand(command="top", description="O'quvchilar reytingi (Top-10)"),
        BotCommand(command="stats", description="Bilim ko'rsatkichlari & statistika"),
        BotCommand(command="history", description="Yechilgan vazifalar tarixi"),
        BotCommand(command="share", description="Do'stlarga va guruhlarga ulashish"),
        BotCommand(command="help", description="Qo'llanma va yordam"),
    ]
    try:
        await bot.set_my_commands(commands)
        await bot.set_my_description(
            description=(
                "🇬🇧 «VAZIFA BAJARADI» — Ingliz Tili va Fanlardan Shaxsiy Uy Vazifasi Yordamchingiz!\n\n"
                "📚 Ingliz tili grammatika mashqlari, qavslarni ochish, testlar, insho (essay) yozish va tekshirish, "
                "audio talaffuz, noto'g'ri fe'llar, rasm orqali yechish va boshqa barcha fanlardan topshiriqlarni "
                "o'zbek tilida qadamma-qadam, chiroyli va tushunarli yechib beradi."
            )
        )
        await bot.set_my_short_description(
            short_description="🇬🇧 Ingliz Tili Uy Vazifasi Yordamchisi 📚 Mashqlarni qadamma-qadam yechib beradi!"
        )
    except Exception as e:
        logger.warning(f"Profil ma'lumotlarini o'rnatishda ogohlantirish: {e}")


async def start_web_server():
    """Render Web Service yoki monitoring uchun fon rejimida portni tinglash."""
    port = int(os.getenv("PORT", "8080"))
    app = web.Application()

    async def ping_handler(request):
        return web.Response(text="Bot is running 24/7!", status=200)

    app.router.add_get("/", ping_handler)
    app.router.add_get("/health", ping_handler)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Render health-check veb-server {port}-portda muvaffaqiyatli ishga tushirildi.")


async def main():
    if not BOT_TOKEN:
        logger.error(".env faylida BOT_TOKEN ko'rsatilmagan!")
        return

    # Render uchun veb-serverni ishga tushirish (agar PORT mavjud bo'lsa)
    try:
        await start_web_server()
    except Exception as e:
        logger.warning(f"Web-serverni ishga tushirishda ogohlantirish: {e}")

    # Ma'lumotlar bazasini tayyorlash
    logger.info("Ma'lumotlar bazasi initsializatsiya qilinmoqda...")
    await init_db()

    # Bot va Dispatcher yaratish
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Routerlarni tartib bilan ulash
    dp.include_router(common_router)
    dp.include_router(subject_router)
    dp.include_router(stats_router)
    dp.include_router(admin_router)
    dp.include_router(homework_router)  # catch-all vazifa xabarlari oxirida

    # Buyruqlarni ro'yxatdan o'tkazish
    await set_default_commands(bot)

    bot_info = await bot.get_me()
    logger.info(f"Bot muvaffaqiyatli ishga tushdi: @{bot_info.username} ({bot_info.first_name})")

    try:
        await bot.delete_webhook(drop_pending_updates=False)
    except Exception as e:
        logger.warning(f"Webhook tozalashda ogohlantirish: {e}")

    # Uzluksiz ishlash va avtomatik qayta ulanish sikli (Auto-reconnect)
    while True:
        try:
            await dp.start_polling(
                bot,
                polling_timeout=20,
                handle_signals=False,
                close_bot_session=False
            )
        except (KeyboardInterrupt, SystemExit):
            logger.info("Bot to'xtatildi.")
            break
        except Exception as e:
            logger.warning(f"Telegram tarmoq uzilishi: {e}. 3 soniyadan so'ng qayta ulanadi...")
            await asyncio.sleep(3)
        finally:
            if not dp.is_polling():
                break

    try:
        await bot.session.close()
    except Exception:
        pass


if __name__ == "__main__":
    while True:
        try:
            asyncio.run(main())
            break
        except (KeyboardInterrupt, SystemExit):
            logger.info("Bot to'liq to'xtatildi.")
            break
        except Exception as e:
            logger.error(f"Kutilmagan xatolik: {e}. 5 soniyadan so'ng qayta ishga tushadi...")
            import time
            time.sleep(5)
