"""
📐 MATEMATIKA UY VAZIFASI BOTI — Asosiy Ishga Tushirish Fayli.
aiogram 3.x va SymPy asosidagi yuqori aniqlikdagi va qotishlarsiz Matematika Boti.
Barcha yechimlar va tushuntirishlar o'zbek tilida, qadamma-qadam taqdim etiladi.
"""

import asyncio
import logging
import sys

# Windows konsolida o'zbekcha harflar va emojilar to'g'ri chiqishi uchun UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from config import BOT_TOKEN
from handlers.math_handlers import router as math_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


async def set_default_commands(bot: Bot):
    """Telegram menyu buyruqlari va bot ma'lumotlarini o'rnatish."""
    commands = [
        BotCommand(command="start", description="Botni ishga tushirish"),
        BotCommand(command="formulas", description="Matematika shpargalkasi & formulalar"),
        BotCommand(command="help", description="Qo'llanma va misollar"),
    ]
    try:
        await bot.set_my_commands(commands)
        await bot.set_my_description(
            description=(
                "📐 MATEMATIKA UY VAZIFASI YORDAMCHISI!\n\n"
                "Ushbu bot maktab, litsey va universitet talabalari uchun matematika fanidan har qanday "
                "topshiriq, tenglama, ifoda, kasr, hosila va integrallarni o'zbek tilida nuqsonsiz va "
                "qadamma-qadam yechib beradi."
            )
        )
        await bot.set_my_short_description(
            short_description="📐 Matematika Uy Vazifasi Boti ⚡ Qadamma-qadam aniq yechimlar!"
        )
    except Exception as e:
        logger.warning(f"Buyruqlarni o'rnatishda ogohlantirish: {e}")


async def main():
    if not BOT_TOKEN:
        logger.error(".env faylida BOT_TOKEN ko'rsatilmagan!")
        return

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Matematika routerini ulash
    dp.include_router(math_router)

    # Buyruqlarni ro'yxatdan o'tkazish
    await set_default_commands(bot)

    bot_info = await bot.get_me()
    print("==============================================================")
    print(f"🚀 MATEMATIKA BOTI ISHGA TUSHDI: @{bot_info.username} ({bot_info.first_name})")
    print("⚡ Barcha matematik yechimlar 0.01 soniyada tayyor bo'ladi!")
    print("==============================================================")

    try:
        await bot.delete_webhook(drop_pending_updates=False)
    except Exception as e:
        logger.warning(f"Webhook tozalash: {e}")

    # Uzluksiz ishlash va avtomatik qayta ulanish sikli (Auto-reconnect)
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
        print("\nBot muvaffaqiyatli to'xtatildi.")
