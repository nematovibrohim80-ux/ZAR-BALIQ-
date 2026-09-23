import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from config import BOT_TOKEN
from database.db import init_db, get_all_admin_ids
from handlers.user_handlers import router as user_router
from handlers.order_handlers import router as order_router
from handlers.admin_handlers import router as admin_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("ZAR_BALIQ_BOT")

async def set_default_commands(bot: Bot):
    """Foydalanuvchi uchun menyu buyruqlarini o'rnatish"""
    commands = [
        BotCommand(command="start", description="Botni ishga tushirish"),
        BotCommand(command="somsa", description="🥟 Somsa narxlari"),
        BotCommand(command="baliq", description="🐟 Baliq narxlari"),
        BotCommand(command="manzil", description="📍 Choyxona manzili"),
        BotCommand(command="aloqa", description="📞 Bog'lanish (Telefon)"),
        BotCommand(command="myid", description="Telegram ID raqamingizni ko'rish"),
        BotCommand(command="setadmin", description="Adminlik huquqini olish"),
        BotCommand(command="admin", description="Admin paneli")
    ]
    await bot.set_my_commands(commands)

async def main():
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error(
            "\n"
            "===========================================================\n"
            "XATOLIK: BOT_TOKEN aniqlanmadi!\n"
            "Iltimos, .env fayliga Telegram @BotFather dan olingan tokenni kiriting.\n"
            "Masalan: BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ\n"
            "==========================================================="
        )
        return

    # Ma'lumotlar bazasini ishga tushirish
    logger.info("Ma'lumotlar bazasi tekshirilmoqda va ishga tushirilmoqda...")
    await init_db()
    logger.info("Ma'lumotlar bazasi tayyor!")

    # Bot va Dispatcher yaratish
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Routerlarni ulash
    dp.include_router(admin_router)
    dp.include_router(order_router)
    dp.include_router(user_router)

    bot_info = None
    for attempt in range(10):
        try:
            bot_info = await bot.get_me()
            break
        except Exception as e:
            logger.warning(f"Telegramga ulanish urinishi {attempt + 1}/10: {e}. 2 soniyadan so'ng qayta uriniladi...")
            await asyncio.sleep(2)

    if not bot_info:
        logger.error("Telegram serverlariga ulanib bo'lmadi.")
        return

    logger.info(f"Bot muvaffaqiyatli ishga tushdi: @{bot_info.username}")

    async def post_startup():
        try:
            await set_default_commands(bot)
        except Exception:
            pass
        try:
            admins = await get_all_admin_ids()
            for admin_id in admins:
                try:
                    await bot.send_message(
                        chat_id=admin_id,
                        text="🚀 <b>ZAR BALIQ boti muvaffaqiyatli ishga tushirildi!</b>",
                        parse_mode=ParseMode.HTML
                    )
                except Exception:
                    pass
        except Exception:
            pass

    asyncio.create_task(post_startup())

    while True:
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            logger.info("Xabarlar qabul qilish (polling) boshlandi...")
            await dp.start_polling(bot)
            break
        except (KeyboardInterrupt, SystemExit):
            break
        except Exception as e:
            logger.error(f"Ulanish uzildi: {e}. 5 soniyadan so'ng qayta ulanmoqda...")
            await asyncio.sleep(5)
    
    await bot.session.close()
    logger.info("Bot to'xtatildi.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot foydalanuvchi tomonidan to'xtatildi.")
