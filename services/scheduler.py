"""
Fon vazifasi: yangiliklar keshini avtomatik yangilab turish
hamda agar Telegram kanal ulangan bo'lsa (CHANNEL_ID), unga yangi xabarlarni avtomatik joylash.
"""

import asyncio
import logging
from aiogram import Bot
from config import CHANNEL_ID, AUTO_POST_INTERVAL_MINUTES
from services.news_service import news_service
from database.db import is_news_posted, mark_news_posted
from keyboards.news_keyboards import get_news_detail_keyboard
from utils.formatters import format_single_news

logger = logging.getLogger(__name__)


async def auto_post_loop(bot: Bot):
    """Orqa fonda doimiy ishlovchi vazifa."""
    logger.info("Avtoposting va kesh yangilovchi fon vazifasi boshlandi.")
    while True:
        try:
            # 1. Keshni yangilash
            await news_service.refresh_all_news()

            # 2. Agar kanal ulangan bo'lsa, yangi jahon xabarini kanalga yuborish
            if CHANNEL_ID:
                world_items = await news_service.get_world_news(limit=5)
                for item in world_items:
                    already_sent = await is_news_posted(item.link)
                    if not already_sent:
                        text = format_single_news(item)
                        keyboard = get_news_detail_keyboard(item.link, item.category)

                        try:
                            if item.image_url:
                                await bot.send_photo(
                                    chat_id=CHANNEL_ID,
                                    photo=item.image_url,
                                    caption=text,
                                    reply_markup=keyboard,
                                    parse_mode="HTML"
                                )
                            else:
                                await bot.send_message(
                                    chat_id=CHANNEL_ID,
                                    text=text,
                                    reply_markup=keyboard,
                                    parse_mode="HTML"
                                )

                            await mark_news_posted(item.link, item.title, item.source)
                            logger.info(f"Yangi xabar kanalga joylandi: {item.title}")
                            # Bir safarda ko'pi bilan 1 ta xabar joylab to'xtash (kanal to'lib ketmasligi uchun)
                            break
                        except Exception as post_err:
                            logger.error(f"Kanalga yuborishda xatolik: {post_err}")
                            break

        except Exception as e:
            logger.error(f"Avtoposting fon vazifasida xatolik: {e}")

        # Belgilangan vaqt kutish (masalan 20 daqiqa)
        await asyncio.sleep(AUTO_POST_INTERVAL_MINUTES * 60)
