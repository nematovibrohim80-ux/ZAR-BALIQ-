"""
Dunyo Yangiliklari boti uchun avtomatlashtirilgan testlar.
Barcha xizmatlar, baza, formatlash va klaviaturalarni tekshiradi.
"""

import asyncio
import sys
from pathlib import Path

# UTF-8 chiqish
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from database.db import init_db, add_user, get_users_count, is_news_posted, mark_news_posted
from services.news_service import news_service
from utils.formatters import format_news_list, format_single_news
from keyboards.news_keyboards import (
    get_main_keyboard,
    get_categories_keyboard,
    get_news_list_keyboard,
    get_news_detail_keyboard
)


async def run_tests():
    print("==========================================")
    print("DUNYO YANGILIKLARI BOTI TESTLARI BOSHLANDI")
    print("==========================================")

    # 1. Ma'lumotlar bazasi testi
    print("\n[1] Ma'lumotlar bazasi tekshirilmoqda...")
    await init_db()
    test_uid = 999999999
    await add_user(test_uid, "Test Foydalanuvchi", "testuser")
    count = await get_users_count()
    assert count >= 1, "Foydalanuvchilar soni kamida 1 bo'lishi kerak!"
    print(f"  -> Bazadagi foydalanuvchilar soni: {count}")

    import time
    test_link = f"https://kun.uz/news/test-post-{int(time.time())}"
    assert not await is_news_posted(test_link), "Boshida yangilik yuborilmagan bo'lishi kerak"
    await mark_news_posted(test_link, "Test Yangilik", "Kun.uz")
    assert await is_news_posted(test_link), "Yangilik bazada saqlangan bo'lishi kerak"
    print("  -> Baza testlari muvaffaqiyatli o'tdi! [OK]")

    # 2. Yangiliklar xizmati (RSS, Kesh, Filtr) testi
    print("\n[2] Yangiliklar xizmati tekshirilmoqda...")
    items = await news_service.refresh_all_news()
    assert len(items) > 0, "Yangiliklar yuklanmadi!"
    print(f"  -> Yuklangan umumiy yangiliklar: {len(items)} ta")

    world_news = await news_service.get_world_news(limit=5)
    assert len(world_news) > 0, "Dunyo yangiliklari topilmadi!"
    print(f"  -> Dunyo yangiliklari soni: {len(world_news)} ta")
    print(f"  -> Namunaviy sarlavha: {world_news[0].title}")

    # Qidiruv testi
    search_res = await news_service.search_news("AQSH", limit=3)
    print(f"  -> 'AQSH' qidiruv natijalari: {len(search_res)} ta topildi")

    # 3. Formatlash testi
    print("\n[3] Matn formatlash tekshirilmoqda...")
    formatted_list = format_news_list(world_news, "🌍 Dunyo Yangiliklari")
    assert "Dunyo Yangiliklari" in formatted_list
    assert len(formatted_list) > 100
    print("  -> Yangiliklar ro'yxati matni to'g'ri shakllandi [OK]")

    formatted_card = format_single_news(world_news[0])
    assert "Manba:" in formatted_card
    print("  -> Bitta yangilik kartochkasi to'g'ri shakllandi [OK]")

    # 4. Tugmalar (Keyboards) testi
    print("\n[4] Tugmalar tekshirilmoqda...")
    main_kb = get_main_keyboard()
    assert len(main_kb.keyboard) >= 3
    print(f"  -> Asosiy menyu qatorlari soni: {len(main_kb.keyboard)} [OK]")

    cat_kb = get_categories_keyboard()
    assert len(cat_kb.inline_keyboard) >= 4
    print(f"  -> Kategoriya tugmalari soni: {len(cat_kb.inline_keyboard)} [OK]")

    list_kb = get_news_list_keyboard(world_news, "world")
    assert len(list_kb.inline_keyboard) >= 2
    print("  -> Raqamli navigatsiya tugmalari to'g'ri shakllandi [OK]")

    detail_kb = get_news_detail_keyboard(world_news[0].link, "world")
    assert len(detail_kb.inline_keyboard) == 2
    print("  -> Tafsilot tugmalari to'g'ri shakllandi [OK]")

    print("\n==========================================")
    print("BARCHA TESTLAR 100% MUVAFFAQISHLI O'TDI! 🎉")
    print("==========================================")


if __name__ == "__main__":
    asyncio.run(run_tests())
