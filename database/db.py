"""
Ma'lumotlar bazasi moduli (aiosqlite).
Foydalanuvchilar, ularning tanlagan fanlari, yechilgan uy vazifalari va statistikalarini saqlaydi.
"""

import aiosqlite
import logging
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from config import DB_PATH

logger = logging.getLogger(__name__)


async def init_db():
    """Jadvallarni yaratish va bazani ishga tushirish."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA journal_mode=WAL;")
        await db.execute("PRAGMA synchronous=NORMAL;")
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                full_name TEXT,
                username TEXT,
                current_subject TEXT DEFAULT '🌐 Umumiy savollar',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                subject TEXT,
                question TEXT,
                solution TEXT,
                status TEXT DEFAULT 'completed',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        await db.execute("CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at)")
        await db.commit()
    logger.info("Uy Vazifa AI ma'lumotlar bazasi muvaffaqiyatli ishga tushirildi.")


async def add_user(user_id: int, full_name: str, username: Optional[str] = None):
    """Foydalanuvchini bazaga qo'shish yoki yangilash."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO users (user_id, full_name, username)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                full_name = excluded.full_name,
                username = excluded.username
        """, (user_id, full_name, username))
        await db.commit()


async def set_user_subject(user_id: int, subject: str):
    """Foydalanuvchi hozir o'rganayotgan/yechayotgan fanni yangilash."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE users SET current_subject = ? WHERE user_id = ?
        """, (subject, user_id))
        await db.commit()


async def get_user_subject(user_id: int) -> str:
    """Foydalanuvchining hozirgi tanlagan fanini olish."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT current_subject FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row and row[0]:
                return row[0]
            return "🌐 Umumiy savollar"


async def save_task(user_id: int, subject: str, question: str, solution: str) -> int:
    """Yechilgan vazifani bazaga saqlash."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO tasks (user_id, subject, question, solution)
            VALUES (?, ?, ?, ?)
        """, (user_id, subject, question, solution))
        await db.commit()
        return cursor.lastrowid


async def get_user_stats(user_id: int) -> Dict[str, Any]:
    """Foydalanuvchining shaxsiy statistikasini hisoblash."""
    today_str = date.today().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        # Jami vazifalar
        async with db.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            total_tasks = row[0] if row else 0

        # Bugungi vazifalar
        async with db.execute(
            "SELECT COUNT(*) FROM tasks WHERE user_id = ? AND date(created_at) = ?",
            (user_id, today_str)
        ) as cursor:
            row = await cursor.fetchone()
            today_tasks = row[0] if row else 0

        # Fanlar bo'yicha taqsimot
        async with db.execute("""
            SELECT subject, COUNT(*) as cnt 
            FROM tasks 
            WHERE user_id = ? 
            GROUP BY subject 
            ORDER BY cnt DESC
        """, (user_id,)) as cursor:
            subject_rows = await cursor.fetchall()
            subjects = {r[0]: r[1] for r in subject_rows}

        return {
            "total_tasks": total_tasks,
            "today_tasks": today_tasks,
            "subjects": subjects
        }


async def get_user_history(user_id: int, limit: int = 5, offset: int = 0) -> List[Dict[str, Any]]:
    """Foydalanuvchining yechilgan vazifalar tarixini olish."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT id, subject, question, solution, created_at
            FROM tasks
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ? OFFSET ?
        """, (user_id, limit, offset)) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]


async def get_user_history_count(user_id: int) -> int:
    """Foydalanuvchi bajargan vazifalar soni."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0


async def get_task_by_id(task_id: int, user_id: int) -> Optional[Dict[str, Any]]:
    """Aniq bir vazifani ID bo'yicha olish."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT id, subject, question, solution, created_at
            FROM tasks
            WHERE id = ? AND user_id = ?
        """, (task_id, user_id)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def clear_user_history(user_id: int) -> int:
    """Foydalanuvchining barcha vazifalar tarixini tozalash."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("DELETE FROM tasks WHERE user_id = ?", (user_id,))
        await db.commit()
        return cursor.rowcount


async def get_admin_stats() -> Dict[str, Any]:
    """Admin uchun umumiy tizim statistikasi."""
    today_str = date.today().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        # Jami foydalanuvchilar
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            users_count = (await cursor.fetchone())[0]

        # Jami yechilgan vazifalar
        async with db.execute("SELECT COUNT(*) FROM tasks") as cursor:
            tasks_count = (await cursor.fetchone())[0]

        # Bugun yechilgan vazifalar
        async with db.execute("SELECT COUNT(*) FROM tasks WHERE date(created_at) = ?", (today_str,)) as cursor:
            today_tasks = (await cursor.fetchone())[0]

        # Eng ommabop fanlar
        async with db.execute("""
            SELECT subject, COUNT(*) as cnt 
            FROM tasks 
            GROUP BY subject 
            ORDER BY cnt DESC 
            LIMIT 5
        """) as cursor:
            top_subjects = await cursor.fetchall()

        return {
            "total_users": users_count,
            "total_tasks": tasks_count,
            "today_tasks": today_tasks,
            "top_subjects": top_subjects
        }


async def get_all_user_ids() -> List[int]:
    """Barcha foydalanuvchilar ID ro'yxati (xabar yuborish uchun)."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT user_id FROM users") as cursor:
            rows = await cursor.fetchall()
            return [r[0] for r in rows]


async def get_leaderboard(limit: int = 10) -> List[Dict[str, Any]]:
    """Eng faol o'quvchilar reytingi (Top foydalanuvchilar)."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT u.user_id, u.full_name, u.username, COUNT(t.id) as task_count
            FROM users u
            JOIN tasks t ON u.user_id = t.user_id
            GROUP BY u.user_id
            HAVING task_count > 0
            ORDER BY task_count DESC
            LIMIT ?
        """, (limit,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]


async def get_user_rank(user_id: int) -> int:
    """Foydalanuvchining umumiy reytingdagi o'rni."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT COUNT(*) + 1
            FROM (
                SELECT user_id, COUNT(id) as task_count
                FROM tasks
                GROUP BY user_id
            )
            WHERE task_count > (
                SELECT COUNT(*) FROM tasks WHERE user_id = ?
            )
        """, (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 1

