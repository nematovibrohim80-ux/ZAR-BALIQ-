"""
Administrator paneli handleri (/admin, /stat, /broadcast).
"""

import asyncio
import logging
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config import is_admin
from database.db import get_admin_stats, get_all_user_ids
from states.homework_states import AdminStates
from utils.formatters import format_admin_stats
from keyboards.homework_keyboards import get_cancel_keyboard, get_main_keyboard

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("admin"))
@router.message(Command("stat"))
async def cmd_admin_panel(message: Message):
    """Admin statistika paneli."""
    if not is_admin(message.from_user.id):
        await message.answer("⛔️ Bu buyruq faqat bot administratorlari uchun ruxsat etilgan.")
        return

    stats = await get_admin_stats()
    text = format_admin_stats(stats)
    text += (
        "\n\n⚙️ **Admin buyruqlari:**\n"
        "• /broadcast — Barcha foydalanuvchilarga xabar yuborish\n"
        "• /stat — Statistikani qayta ko'rish"
    )
    await message.answer(text, parse_mode="Markdown")


@router.message(Command("broadcast"))
async def cmd_broadcast_start(message: Message, state: FSMContext):
    """Barcha bot foydalanuvchilariga xabar yuborishni boshlash."""
    if not is_admin(message.from_user.id):
        await message.answer("⛔️ Ruxsat berilmagan.")
        return

    await state.set_state(AdminStates.waiting_for_broadcast_message)
    await message.answer(
        "📢 **Ommaviy xabar yuborish:**\n\n"
        "Barcha o'quvchilarga yubormoqchi bo'lgan xabaringizni yozing (matn, havola yoki rasm bilan):\n\n"
        "Bekor qilish uchun pastdagi tugmani bosing.",
        reply_markup=get_cancel_keyboard()
    )


@router.message(AdminStates.waiting_for_broadcast_message)
async def process_broadcast_message(message: Message, state: FSMContext, bot: Bot):
    """Ommaviy xabarni barcha foydalanuvchilarga yuborish."""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Xabar yuborish bekor qilindi.", reply_markup=get_main_keyboard())
        return

    await state.clear()
    user_ids = await get_all_user_ids()
    total = len(user_ids)

    if total == 0:
        await message.answer("Bazada foydalanuvchilar mavjud emas.", reply_markup=get_main_keyboard())
        return

    status_msg = await message.answer(f"⏳ Xabar yuborilmoqda: 0/{total}...")

    sent = 0
    failed = 0

    for idx, uid in enumerate(user_ids, 1):
        try:
            await message.copy_to(chat_id=uid)
            sent += 1
            await asyncio.sleep(0.05)  # Telegram flood limitidan qochish
        except Exception as e:
            failed += 1
            logger.debug(f"Foydalanuvchiga yuborib bo'lmadi {uid}: {e}")

        if idx % 20 == 0 or idx == total:
            try:
                await status_msg.edit_text(f"⏳ Xabar yuborilmoqda: {idx}/{total}...")
            except Exception:
                pass

    await message.answer(
        f"✅ **Ommaviy xabar yakunlandi!**\n\n"
        f"👥 Jami: {total} nafar\n"
        f"📨 Yetkazildi: {sent} nafar\n"
        f"❌ Xatolik (botni bloklaganlar): {failed} nafar",
        reply_markup=get_main_keyboard()
    )
