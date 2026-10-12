"""
Matnlarni chiroyli formatlash va yordamchi utilitlar.
"""

from typing import Dict, Any, List


def make_progress_bar(current: int, total: int, length: int = 10) -> str:
    """Vizual progress bar yasash (masalan: [████░░░░░░] 40%)."""
    if total <= 0:
        return "[░░░░░░░░░░] 0%"
    percent = min(100, int((current / total) * 100))
    filled_len = int(length * percent / 100)
    bar = "█" * filled_len + "░" * (length - filled_len)
    return f"[{bar}] {percent}%"


def calculate_level(total_tasks: int) -> str:
    """Yechilgan vazifalar soniga qarab foydalanuvchi darajasini hisoblash."""
    if total_tasks == 0:
        return "🌱 Yangi boshlovchi"
    elif total_tasks < 5:
        return "🥉 Tirishqoq o'quvchi (1-daraja)"
    elif total_tasks < 15:
        return "🥈 Faol izlanuvchi (2-daraja)"
    elif total_tasks < 35:
        return "🥇 Bilimdon talaba (3-daraja)"
    elif total_tasks < 70:
        return "🏆 Fan professori (4-daraja)"
    else:
        return "👑 Daho va Mutaxassis (5-daraja)"


def format_user_stats(stats: Dict[str, Any], full_name: str) -> str:
    """Foydalanuvchi uchun shaxsiy statistika va hisobot matnini tuzish."""
    total = stats.get("total_tasks", 0)
    today = stats.get("today_tasks", 0)
    subjects = stats.get("subjects", {})
    level = calculate_level(total)

    text_parts = [
        f"📊 **{full_name}**, sizning ta'lim hisobotingiz:\n",
        f"🎯 **Jami yechilgan vazifalar:** {total} ta",
        f"📅 **Bugungi faollik:** {today} ta vazifa",
        f"🎖 **Sizning unvoningiz:** {level}\n",
        "📚 **Fanlar bo'yicha taqsimot:**"
    ]

    if not subjects:
        text_parts.append("_(Hozircha hech qaysi fandan vazifa yechilmagan)_")
    else:
        for subj, count in subjects.items():
            bar = make_progress_bar(count, total, length=8)
            text_parts.append(f"• **{subj}:** {count} ta {bar}")

    text_parts.append("\n💡 *Maslahat: Har kuni kamida 3-5 ta vazifa yechib, bilim darajangizni oshiring!*")
    return "\n".join(text_parts)


def format_leaderboard(top_students: List[Dict[str, Any]], user_rank: int, current_user_id: int) -> str:
    """O'quvchilar reytingi (Top-10) matnini shakllantirish."""
    parts = [
        "🏆 **Eng Faol O'quvchilar Reytingi (Top-10)**\n",
        "Bot orqali eng ko'p vazifa yechgan bilimdon o'quvchilar:\n"
    ]
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    if not top_students:
        parts.append("_(Hozircha reyting mavjud emas. Birinchi bo'lib vazifa yeching!)_")
    else:
        for idx, student in enumerate(top_students):
            icon = medals[idx] if idx < len(medals) else f"{idx + 1}."
            name = student.get("full_name") or "O'quvchi"
            tasks = student.get("task_count", 0)
            is_me = " (Siz)" if student.get("user_id") == current_user_id else ""
            parts.append(f"{icon} **{name}**{is_me} — {tasks} ta vazifa")

    parts.append(f"\n📍 **Sizning o'rningiz:** #{user_rank}-o'rin")
    parts.append("\n💡 *Ko'proq vazifa yechib, 1-o'ringa ko'tariling va do'stlaringiz bilan bellashing!*")
    return "\n".join(parts)


def format_admin_stats(stats: Dict[str, Any]) -> str:
    """Admin uchun tizim umumiy hisoboti."""
    users_count = stats.get("total_users", 0)
    tasks_count = stats.get("total_tasks", 0)
    today_tasks = stats.get("today_tasks", 0)
    top_subjects = stats.get("top_subjects", [])

    text_parts = [
        "👑 **Uy Vazifa AI — Tizim Statistikasi**\n",
        f"👥 **Jami foydalanuvchilar:** {users_count:,} nafar",
        f"📝 **Jami yechilgan vazifalar:** {tasks_count:,} ta",
        f"⚡️ **Bugun yechilgan vazifalar:** {today_tasks:,} ta\n",
        "🏆 **Eng faol o'rganilayotgan fanlar:**"
    ]

    if not top_subjects:
        text_parts.append("_(Ma'lumotlar yo'q)_")
    else:
        for idx, (subj, count) in enumerate(top_subjects, 1):
            text_parts.append(f"{idx}. {subj} — {count} ta yechim")

    return "\n".join(text_parts)


def chunk_text(text: str, max_chars: int = 4000) -> List[str]:
    """Uzun matnni Telegram xabar hajmiga qarab bo'laklarga ajratish."""
    if len(text) <= max_chars:
        return [text]

    chunks = []
    current_chunk = []
    current_len = 0

    paragraphs = text.split("\n\n")
    for para in paragraphs:
        if len(para) > max_chars:
            # Agar bitta paragrafning o'zi max_chars dan katta bo'lsa
            if current_chunk:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = []
                current_len = 0
            for i in range(0, len(para), max_chars):
                chunks.append(para[i:i + max_chars])
            continue

        if current_len + len(para) + 2 <= max_chars:
            current_chunk.append(para)
            current_len += len(para) + 2
        else:
            if current_chunk:
                chunks.append("\n\n".join(current_chunk))
            current_chunk = [para]
            current_len = len(para)

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return chunks
