import aiosqlite
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any
from config import (
    DB_PATH, PHONE_NUMBER, TELEGRAM_GROUP_LINK, DEFAULT_DELIVERY_PRICE,
    ADDRESS_TEXT, LOCATION_LAT, LOCATION_LON
)

@asynccontextmanager
async def get_db():
    """Ma'lumotlar bazasi ulanishini xavfsiz ochish va yopish"""
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = await aiosqlite.connect(DB_PATH)
    conn.row_factory = aiosqlite.Row
    try:
        yield conn
    finally:
        await conn.close()

async def init_db():
    """Baza jadvallarini yaratish va boshlang'ich ma'lumotlarni kiritish"""
    async with get_db() as conn:
        # 1. Foydalanuvchilar jadvali
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                phone TEXT,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 2. Mahsulotlar jadvali
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT DEFAULT 'somsa',
                name TEXT NOT NULL,
                description TEXT,
                price_unit INTEGER NOT NULL,
                photo_file_id TEXT,
                is_active INTEGER DEFAULT 1
            )
        """)

        # category ustunini tekshirish (agar mavjud bo'lmasa qo'shish)
        cursor = await conn.execute("PRAGMA table_info(products)")
        columns = [col[1] for col in await cursor.fetchall()]
        if "category" not in columns:
            await conn.execute("ALTER TABLE products ADD COLUMN category TEXT DEFAULT 'somsa'")

        # 3. Buyurtmalar jadvali
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                product_price INTEGER NOT NULL,
                delivery_price INTEGER NOT NULL,
                total_price INTEGER NOT NULL,
                customer_name TEXT NOT NULL,
                customer_phone TEXT NOT NULL,
                order_type TEXT NOT NULL,
                address TEXT,
                latitude REAL,
                longitude REAL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 4. Tizim sozlamalari jadvali
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)

        # Boshlang'ich sozlamalarni kiritish yoki yangilash
        default_settings = [
            ("phone_number", PHONE_NUMBER),
            ("telegram_group_link", TELEGRAM_GROUP_LINK),
            ("delivery_price", str(DEFAULT_DELIVERY_PRICE)),
            ("address_text", ADDRESS_TEXT),
            ("work_hours", "Har kuni 10:00 dan 23:00 gacha (dam olish kunlarisiz)"),
            ("location_lat", str(LOCATION_LAT)),
            ("location_lon", str(LOCATION_LON)),
            ("delivery_info", "🚚 <b>Yetkazib berish xizmati:</b>\n\n• Yetkazib berish vaqti: 30 - 60 daqiqa\n• Yetkazib berish hududi: Shahar va viloyat bo'ylab\n• Har bir buyurtma maxsus termobokslarda, issiq va yangi yetkaziladi!"),
            ("about_text", "🐟 <b>\"ZAR BALIQ\" Choyxonasi</b> — yangi, mazali va betakror SOMSA hamda sara BALIQ taomlarini tayyorlash bo‘yicha sevimli maskaningiz!\n\nBiz har kuni faqat eng sifatli va toza mahsulotlardan, maxsus ziravorlar va qarsildoq xamir bilan haqiqiy SOMSA va yangi qovurilgan BALIQ pishiramiz.\n\n✨ <i>Har bir luqmada betakror ta'm va yuqori sifat!</i>")
        ]

        for key, val in default_settings:
            await conn.execute("""
                INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)
            """, (key, val))

        # Doimo telefon raqam, manzil va lokatsiyani so'nggi config bilan yangilab qo'yish
        await conn.execute("UPDATE settings SET value = ? WHERE key = 'phone_number'", (PHONE_NUMBER,))
        await conn.execute("UPDATE settings SET value = ? WHERE key = 'address_text'", (ADDRESS_TEXT,))
        await conn.execute("UPDATE settings SET value = ? WHERE key = 'location_lat'", (str(LOCATION_LAT),))
        await conn.execute("UPDATE settings SET value = ? WHERE key = 'location_lon'", (str(LOCATION_LON),))

        # Mavjud somsalar narxini 8 000 so'm, baliq narxini 85 000 so'mga yangilash
        await conn.execute("UPDATE products SET price_unit = 8000 WHERE category = 'somsa' OR name LIKE '%somsa%'")
        await conn.execute("UPDATE products SET price_unit = 85000 WHERE (category = 'baliq' OR name LIKE '%baliq%') AND name NOT LIKE '%somsa%' AND name NOT LIKE '%assorti%'")

        # Boshlang'ich mahsulotlar (Somsa va Baliq taomlari) ni kiritish
        cursor = await conn.execute("SELECT COUNT(*) FROM products")
        count = (await cursor.fetchone())[0]

        if count <= 1:
            await conn.execute("DELETE FROM products")

            initial_dishes = [
                # SOMSALAR (category = 'somsa', narxi: 8 000 so'm)
                (
                    "🥟 Mazali Tandir Somsa",
                    "Yangi mol go'shti, mayin piyoz va xushxo'r ziravorlar bilan qarsildoq tandirda pishirilgan somsa.",
                    8000,
                    "somsa"
                ),
                (
                    "🥟 Maxsus Baliqli Somsa",
                    "ZAR BALIQning oshpazlik siri: toza suyaklarsiz yangi baliq filesi va shirin piyoz bilan tayyorlangan tandir somsa.",
                    8000,
                    "somsa"
                ),
                (
                    "🥟 Qatlama Tandir Somsa",
                    "Mayin va qarsildoq qatlama xamirdan tayyorlangan an'anaviy mazali somsa.",
                    8000,
                    "somsa"
                ),

                # BALIQ TAOMLARI (category = 'baliq', narxi: 85 000 so'm)
                (
                    "🐟 Mazali Qovurilgan Baliq",
                    "Maxsus yog'da qarsildoq qovurilgan, shirali va betakror xushta'm baliq. (1 kg)",
                    85000,
                    "baliq"
                ),
                (
                    "🐟 Sazan (Zog'ora baliq)",
                    "Daryo zog'ora balig'i, maxsus ziravorlar bilan qovurilgan, xushta'm va shirali. (1 kg)",
                    85000,
                    "baliq"
                ),
                (
                    "🐟 Sudak (Oq baliq)",
                    "Suyaksiz, mayin oq go'shtli, parhezbop va qarsildoq qovurilgan baliq. (1 kg)",
                    85000,
                    "baliq"
                ),
                (
                    "👑 ZAR BALIQ Assorti (Patnis)",
                    "Katta davralar uchun shohona patnis: qovurilgan baliqlar, somsa, maxsus sarimsoqli sous, limon va barra sabzavotlar.",
                    350000,
                    "baliq"
                ),
            ]

            for name, desc, price, cat in initial_dishes:
                await conn.execute("""
                    INSERT INTO products (name, description, price_unit, category, photo_file_id, is_active)
                    VALUES (?, ?, ?, ?, NULL, 1)
                """, (name, desc, price, cat))

        await conn.commit()

# --- Foydalanuvchilar ---
async def add_or_update_user(user_id: int, username: Optional[str], full_name: str, phone: Optional[str] = None):
    async with get_db() as conn:
        if phone:
            await conn.execute("""
                INSERT INTO users (id, username, full_name, phone)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    username = excluded.username,
                    full_name = excluded.full_name,
                    phone = excluded.phone
            """, (user_id, username, full_name, phone))
        else:
            await conn.execute("""
                INSERT INTO users (id, username, full_name)
                VALUES (?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    username = excluded.username,
                    full_name = excluded.full_name
            """, (user_id, username, full_name))
        await conn.commit()

async def get_user(user_id: int) -> Optional[dict]:
    async with get_db() as conn:
        cursor = await conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None

async def get_all_users() -> List[dict]:
    async with get_db() as conn:
        cursor = await conn.execute("SELECT * FROM users")
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]

# --- Sozlamalar ---
async def get_setting(key: str, default: Any = None) -> Any:
    async with get_db() as conn:
        cursor = await conn.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = await cursor.fetchone()
        return row[0] if row else default

async def set_setting(key: str, value: str):
    async with get_db() as conn:
        await conn.execute("""
            INSERT INTO settings (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """, (key, value))
        await conn.commit()

async def get_all_admin_ids() -> List[int]:
    """Konfiguratsiya va bazadagi barcha haqiqiy admin ID larini olish"""
    from config import ADMIN_IDS
    ids = set()
    for a in ADMIN_IDS:
        if a != 123456789: # Namuna/placeholder ID ni hisobga olmaslik
            ids.add(a)

    db_admins = await get_setting("admin_ids", "")
    if db_admins:
        for a in str(db_admins).split(","):
            a = a.strip()
            if a.isdigit() and int(a) != 123456789:
                ids.add(int(a))
    return list(ids)

async def add_admin_id(user_id: int):
    """Yangi administrator ID sini bazaga qo'shish"""
    current = await get_setting("admin_ids", "")
    ids = set()
    if current:
        for a in str(current).split(","):
            a = a.strip()
            if a.isdigit() and int(a) != 123456789:
                ids.add(int(a))
    ids.add(user_id)
    await set_setting("admin_ids", ",".join(str(i) for i in ids))

# --- Mahsulotlar ---
async def get_products(only_active: bool = True) -> List[dict]:
    async with get_db() as conn:
        query = "SELECT * FROM products"
        if only_active:
            query += " WHERE is_active = 1"
        query += " ORDER BY id ASC"
        cursor = await conn.execute(query)
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]

async def get_products_by_category(category: str, only_active: bool = True) -> List[dict]:
    """Kategoriya bo'yicha mahsulotlarni olish ('somsa' yoki 'baliq')"""
    async with get_db() as conn:
        query = "SELECT * FROM products WHERE (category = ? OR (? = 'somsa' AND name LIKE '%somsa%') OR (? = 'baliq' AND name NOT LIKE '%somsa%'))"
        if only_active:
            query += " AND is_active = 1"
        query += " ORDER BY id ASC"
        cursor = await conn.execute(query, (category, category, category))
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]

async def get_product_by_id(product_id: int) -> Optional[dict]:
    async with get_db() as conn:
        cursor = await conn.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None

async def get_main_product() -> Optional[dict]:
    """Asosiy mahsulot (SOMSA BALIQ) ni olish"""
    async with get_db() as conn:
        cursor = await conn.execute("SELECT * FROM products WHERE name LIKE '%SOMSA%' AND is_active = 1 LIMIT 1")
        row = await cursor.fetchone()
        if not row:
            cursor = await conn.execute("SELECT * FROM products WHERE is_active = 1 LIMIT 1")
            row = await cursor.fetchone()
        return dict(row) if row else None

async def add_product(name: str, description: str, price_unit: int, category: str = "somsa", photo_file_id: Optional[str] = None) -> int:
    async with get_db() as conn:
        cursor = await conn.execute("""
            INSERT INTO products (name, description, price_unit, category, photo_file_id, is_active)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (name, description, price_unit, category, photo_file_id))
        await conn.commit()
        return cursor.lastrowid

async def update_product(product_id: int, **kwargs):
    valid_fields = ["name", "description", "price_unit", "category", "photo_file_id", "is_active"]
    updates = []
    values = []
    for k, v in kwargs.items():
        if k in valid_fields:
            updates.append(f"{k} = ?")
            values.append(v)
    if not updates:
        return
    values.append(product_id)
    async with get_db() as conn:
        await conn.execute(f"UPDATE products SET {', '.join(updates)} WHERE id = ?", values)
        await conn.commit()

# --- Buyurtmalar ---
async def create_order(
    user_id: int,
    product_name: str,
    quantity: int,
    product_price: int,
    delivery_price: int,
    total_price: int,
    customer_name: str,
    customer_phone: str,
    order_type: str,
    address: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None
) -> int:
    async with get_db() as conn:
        cursor = await conn.execute("""
            INSERT INTO orders (
                user_id, product_name, quantity, product_price, delivery_price, total_price,
                customer_name, customer_phone, order_type, address, latitude, longitude, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
        """, (
            user_id, product_name, quantity, product_price, delivery_price, total_price,
            customer_name, customer_phone, order_type, address, latitude, longitude
        ))
        await conn.commit()
        return cursor.lastrowid

async def get_order(order_id: int) -> Optional[dict]:
    async with get_db() as conn:
        cursor = await conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None

async def update_order_status(order_id: int, status: str):
    async with get_db() as conn:
        await conn.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
        await conn.commit()

async def get_recent_orders(limit: int = 10) -> List[dict]:
    async with get_db() as conn:
        cursor = await conn.execute("SELECT * FROM orders ORDER BY id DESC LIMIT ?", (limit,))
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]

async def get_pending_orders() -> List[dict]:
    async with get_db() as conn:
        cursor = await conn.execute("SELECT * FROM orders WHERE status = 'pending' ORDER BY id DESC")
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]

async def get_statistics() -> dict:
    async with get_db() as conn:
        # Foydalanuvchilar soni
        c_users = await conn.execute("SELECT COUNT(*) FROM users")
        total_users = (await c_users.fetchone())[0]

        # Buyurtmalar soni
        c_orders = await conn.execute("SELECT COUNT(*) FROM orders")
        total_orders = (await c_orders.fetchone())[0]

        # Kutilayotgan buyurtmalar
        c_pending = await conn.execute("SELECT COUNT(*) FROM orders WHERE status = 'pending'")
        pending_orders = (await c_pending.fetchone())[0]

        # Qabul qilingan buyurtmalar
        c_accepted = await conn.execute("SELECT COUNT(*) FROM orders WHERE status = 'accepted'")
        accepted_orders = (await c_accepted.fetchone())[0]

        # Jami tushum (faqat accepted buyurtmalardan)
        c_revenue = await conn.execute("SELECT COALESCE(SUM(total_price), 0) FROM orders WHERE status = 'accepted'")
        total_revenue = (await c_revenue.fetchone())[0]

        return {
            "total_users": total_users,
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "accepted_orders": accepted_orders,
            "total_revenue": total_revenue
        }
