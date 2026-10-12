"""
Fanlarni tanlash va almashtirish handleri.
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database.db import set_user_subject, get_user_subject
from keyboards.homework_keyboards import get_subjects_inline_keyboard
from states.homework_states import HomeworkStates

router = Router()

SUBJECT_MAP = {
    "english": "🇬🇧 Ingliz tili",
    "matem": "📐 Matematika",
    "physics": "⚛️ Fizika",
    "chem": "🧪 Kimyo",
    "uzbek": "📚 Ona tili & Adabiyot",
    "it": "💻 IT & Dasturlash",
    "history": "🌍 Tarix & Geografiya",
    "bio": "🧬 Biologiya",
    "general": "🌐 Barcha fanlar (Umumiy)",
}


@router.message(Command("subjects"))
@router.message(F.text == "📚 Fanlar")
@router.message(F.text == "📚 Boshqa fanlar")
async def cmd_subjects(message: Message):
    """Fanlar ro'yxatini chiqarish."""
    user_id = message.from_user.id
    current_subj = await get_user_subject(user_id)

    text = (
        f"📚 **Uy vazifasi fanini tanlang:**\n\n"
        f"Hozirda tanlangan: **{current_subj}**\n\n"
        f"Kerakli fanni tanlasangiz, AI aynan shu fanga moslashib, "
        f"qoidalar va formulalar asosida eng aniq yechimni taqdim etadi:"
    )
    await message.answer(text, reply_markup=get_subjects_inline_keyboard())


@router.callback_query(F.data.startswith("sub:"))
async def callback_select_subject(callback: CallbackQuery, state: FSMContext):
    """Fan tanlanganda uni saqlash va yangi savol kutish."""
    key = callback.data.split("sub:")[1]
    subject_name = SUBJECT_MAP.get(key, "🌐 Barcha fanlar (Umumiy)")
    user_id = callback.from_user.id

    await set_user_subject(user_id, subject_name)
    await state.set_state(HomeworkStates.waiting_for_question)

    await callback.answer(f"Tanlandi: {subject_name}")
    await callback.message.edit_text(
        f"✅ Fan o'zgartirildi: **{subject_name}**\n\n"
        f"Endi ushbu fan bo'yicha vazifangizni, misol yoki savolingizni yozib yuboring! 👇"
    )
