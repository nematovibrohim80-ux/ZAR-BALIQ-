"""
«VAZIFA BAJARADI» (@uy_vazifa_bot) Ingliz Tili Uy Vazifasi tizimini to'liq tekshirish testi.
"""

import sys
import asyncio
import os
from pathlib import Path

# UTF-8 konsol chiqishi
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from config import BOT_TOKEN, DB_PATH
import database.db as db
from services.ai_service import ai_service
from services.english_service import english_service, GRAMMAR_QUIZ
from services.tts_service import tts_service
from utils.formatters import (
    make_progress_bar,
    calculate_level,
    format_user_stats,
    format_admin_stats,
    format_leaderboard,
    chunk_text
)
from keyboards.homework_keyboards import (
    get_main_keyboard,
    get_subjects_inline_keyboard,
    get_history_keyboard,
    get_solution_inline_keyboard,
    get_english_rules_keyboard,
    get_irregular_pagination_keyboard,
    get_quiz_keyboard,
    get_share_inline_keyboard
)


async def run_tests():
    print("==================================================")
    print("🚀 INGLIZ TILI UY VAZIFASI BOTINI TESTDAN O'TKAZISH")
    print("==================================================")

    # 1. Config & Token
    print("\n1. Sozlamalar va Bot Tokeni tekshiruvi...")
    assert BOT_TOKEN, "BOT_TOKEN bo'sh bo'lmasligi kerak!"
    assert "8823777209:" in BOT_TOKEN, "Bot tokeni to'g'ri o'rnatilgan bo'lishi kerak!"
    print(f"✅ Bot Tokeni to'g'ri: {BOT_TOKEN[:15]}...")

    # 2. Database testlari
    print("\n2. Ma'lumotlar bazasi testlari...")
    test_db_path = Path("database/test_uy_vazifa.db")
    db.DB_PATH = test_db_path
    if test_db_path.exists():
        test_db_path.unlink()

    await db.init_db()
    print("✅ Baza muvaffaqiyatli yaratildi.")

    test_user_id = 999888777
    await db.add_user(test_user_id, "Test Foydalanuvchi", "test_user")
    print("✅ Foydalanuvchi qo'shildi.")

    await db.set_user_subject(test_user_id, "🇬🇧 Ingliz tili")
    new_subj = await db.get_user_subject(test_user_id)
    assert new_subj == "🇬🇧 Ingliz tili"
    print(f"✅ Standart fan Ingliz tili: {new_subj}")

    # Vazifalarni saqlash
    t1 = await db.save_task(test_user_id, "🇬🇧 Ingliz tili", "She (go) to school yesterday", "went")
    t2 = await db.save_task(test_user_id, "🇬🇧 Ingliz tili", "Present Perfect qoidasi", "have/has + V3")
    t3 = await db.save_task(test_user_id, "📐 Matematika", "2x + 8 = 20", "x = 6")
    assert t1 and t2 and t3
    print(f"✅ 3 ta vazifa bazaga saqlandi (IDs: {t1}, {t2}, {t3}).")

    # Statistika testi
    stats = await db.get_user_stats(test_user_id)
    assert stats["total_tasks"] == 3
    assert stats["today_tasks"] == 3
    assert stats["subjects"]["🇬🇧 Ingliz tili"] == 2
    print("✅ Shaxsiy statistika hisoblash to'g'ri ishladi.")

    # 3. Ingliz tili maxsus moduli testlari (EnglishService)
    print("\n3. Ingliz tili moduli (EnglishService) testi...")

    # Noto'g'ri fe'llar qidiruvi
    verbs_by_v2 = english_service.search_irregular_verb("wrote")
    assert verbs_by_v2 and verbs_by_v2[0]["v1"] == "write"
    print(f"✅ V2 'wrote' qidiruvi muvaffaqiyatli: {verbs_by_v2[0]['v1']} - {verbs_by_v2[0]['uz']}")

    verbs_by_uz = english_service.search_irregular_verb("bormoq")
    assert verbs_by_uz and verbs_by_uz[0]["v1"] == "go"
    print(f"✅ O'zbekcha 'bormoq' qidiruvi muvaffaqiyatli: {verbs_by_uz[0]['v1']} - {verbs_by_uz[0]['v2']} - {verbs_by_uz[0]['v3']}")

    # Noto'g'ri fe'llar ro'yxati varaqlash
    irreg_text, total_pages = english_service.get_all_irregular_verbs_text(page=1)
    assert "Irregular Verbs" in irreg_text and total_pages >= 5
    print(f"✅ Noto'g'ri fe'llar jadvali to'g'ri shakllandi (Jami {total_pages} sahifa).")

    # Qavslarni ochish tahlili (Past Simple)
    bracket_res1 = english_service.solve_open_brackets("She (go) to school yesterday.")
    assert bracket_res1 and "went" in bracket_res1
    print(f"✅ Qavslarni ochish (Past Simple): Topildi -> went")

    # Qavslarni ochish tahlili (Present Perfect)
    bracket_res2 = english_service.solve_open_brackets("They (live) in Tashkent since 2018.")
    assert bracket_res2 and "have lived" in bracket_res2
    print(f"✅ Qavslarni ochish (Present Perfect): Topildi -> have lived")

    # Grammatika qoidasi olish
    rule_tenses = english_service.get_rule_by_key("tenses_simple")
    assert rule_tenses and "Present Simple" in rule_tenses
    print("✅ Grammatika qoidalari ma'lumotnomasi to'g'ri ishlamoqda.")

    # Grammatika quizi
    assert len(GRAMMAR_QUIZ) >= 5
    print(f"✅ Grammatika quizi savollari soni: {len(GRAMMAR_QUIZ)} ta.")

    # 4. Audio Talaffuz (TTS) testi
    print("\n4. Audio Talaffuz (TTS Service) testi...")
    extracted_text = tts_service.extract_english_sentence("Vazifa javobi: `She went to school yesterday`.")
    assert "She went to school yesterday" in extracted_text
    print(f"✅ Matndan inglizcha gap ajratib olindi: «{extracted_text}»")

    audio_file = tts_service.generate_audio("She went to school yesterday.", filename_prefix="test_voice")
    assert audio_file and Path(audio_file).exists()
    print(f"✅ MP3 audio fayli muvaffaqiyatli yaratildi ({os.path.getsize(audio_file)} bayt).")

    # 5. AI Service mahalliy va hisoblash testi
    print("\n5. AI Service (Lokal yechish) testi...")
    ai_eng_sol = ai_service._solve_locally("She (go) to school yesterday", "🇬🇧 Ingliz tili")
    assert ai_eng_sol and "went" in ai_eng_sol
    print("✅ AI Service lokal ingliz tili yechuvchisi to'g'ri ishladi.")

    math_sol = ai_service._solve_locally("25 * 4 + 10", "📐 Matematika")
    assert math_sol and "110" in math_sol
    print(f"✅ Lokal arifmetika hisoblagich natijasi: {math_sol.splitlines()[-1]}")

    # 6. Klaviaturalar tekshiruvi
    print("\n6. Klaviaturalar tekshiruvi...")
    main_kb = get_main_keyboard()
    assert len(main_kb.keyboard) >= 4
    sol_kb = get_solution_inline_keyboard(t1)
    # 1-tugma audio talaffuz bo'lishi kerak
    assert "voice:" in sol_kb.inline_keyboard[0][0].callback_data
    rules_kb = get_english_rules_keyboard()
    assert len(rules_kb.inline_keyboard) >= 4
    quiz_kb = get_quiz_keyboard(1)
    assert len(quiz_kb.inline_keyboard) >= 3
    print("✅ Barcha asosiy, yechim, audio, qoidalar va quiz klaviaturalari muvaffaqiyatli tekshirildi.")

    # Tozalash
    if test_db_path.exists():
        test_db_path.unlink()
    if audio_file and Path(audio_file).exists():
        try:
            Path(audio_file).unlink()
        except Exception:
            pass

    print("\n==================================================")
    print("🎉 BARCHA TESTLAR 100% MUVAFFAQIYATLI O'TDI!")
    print("==================================================")


if __name__ == "__main__":
    asyncio.run(run_tests())
