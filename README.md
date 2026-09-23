# 🐟 ZAR BALIQ Choyxonasi — Rasmiy Telegram Boti 🥟

**"ZAR BALIQ"** choyxonasi uchun maxsus ishlab chiqilgan, 100% sof va tushunarli o'zbek tilidagi rasmiy Telegram boti.

Bot Python dasturlash tilida, zamonaviy va asinxron **aiogram 3.x** hamda **aiosqlite** ma'lumotlar bazasi asosida yaratilgan.

---

## 🌟 Asosiy Bo'limlar va Imkoniyatlar

### 1. Asosiy Menyu (Tugmalar ko'rinishida)
* **🥟 Somsa narxlari** — ZAR BALIQning mashhur maxsus baliqli somsasi, go'shtli tandir somsa, pishloqli va qatlama somsalar menyusi va narxlari.
* **🐟 Baliq narxlari** — Qarsildoq qovurilgan Sazan (zog'ora baliq), parhezbop Sudak, shirin Oq Amur, sara Forel hamda katta davralar uchun shohona "ZAR BALIQ Assorti" patnislari narxlari.
* **📍 Manzil** — Choyxona joylashgan aniq manzil, mo'ljal, ish vaqti, bepul avtoturargoh ma'lumotlari hamda Telegram xarita lokatsiyasi (Yandex Xarita / Google Maps tugmalari).
* **📞 Bog'lanish** — Bog'lanish telefon raqami (`33-355-87-77`), bir bosishda qo'ng'iroq qilish tugmasi va buyurtma berish.
* **🛒 Buyurtma berish** — Taomni va miqdorini tanlash, yetkazib berish yoki olib ketishni belgilash, buyurtmani rasmiylashtirish.
* **ℹ️ Biz haqimizda** — Choyxona tarixi va taomlar tayyorlanishi haqida ma'lumot.

---

### 2. Start Xabari
`/start` bosilganda bot chiroyli va samimiy kutib olish xabarini chiqaradi:
> *"Assalomu alaykum! 'ZAR BALIQ' choyxonasining rasmiy botiga xush kelibsiz! 🐟🥟"*

---

### 3. Taomlar va Narxlar Ro'yxati (Boshlang'ich Menyusi)

#### 🥟 Somsalar:
* **🥟 Maxsus Baliqli Somsa** — 20 000 so‘m / dona
* **🥩 Go'shtli Tandir Somsa** — 18 000 so‘m / dona
* **🧀 Pishloqli va Tovuqli Somsa** — 16 000 so‘m / dona
* **🥟 Qatlama Tandir Somsa** — 15 000 so‘m / dona

#### 🐟 Baliq Taomlari:
* **🐟 Sazan (Zog'ora baliq)** — 90 000 so‘m (1 kg)
* **🐟 Sudak (Oq baliq)** — 120 000 so‘m (1 kg)
* **🐟 Oq Amur (Tolstolob)** — 85 000 so‘m (1 kg)
* **🐟 Forel (Xonbaliq)** — 75 000 so‘m (1 dona)
* **👑 ZAR BALIQ Assorti (Patnis)** — 350 000 so‘m (katta davralar uchun)

---

### 4. Administrator Imkoniyatlari
* **Avtomatik birinchi admin:** Botga birinchi bo'lib `/start` yoki `/setadmin` yuborgan foydalanuvchi avtomatik ravishda bosh administrator bo'ladi.
* **Yangi buyurtmalar nazorati:** Har bir mijoz buyurtma berganda, admin(lar)ga darhol bildirishnoma boradi. Unda:
  - `✅ Qabul qilish` va `❌ Rad etish` tugmalari
  - Mijoz bilan bir bosishda bog'lanish (Telegram profil yoki Telefon)
* **Admin Panel (`/admin`):**
  - Taomlar narxini o'zgartirish, yangi taom qo'shish, faolsizlantirish.
  - Telefon raqami, manzil va yetkazib berish narxini bot ichidan o'zgartirish.
  - Barcha mijozlarga ommaviy reklama / xabar tarqatish (Broadcast).
  - Statistika ko'rish (mijozlar soni, buyurtmalar soni va jami tushum).

---

## 🚀 Botni Ishga Tushirish

### 1. Talablar
Kompyuterda **Python 3.10+** o'rnatilgan bo'lishi kerak.

Kutubxonalarni o'rnatish:
```bash
py -m pip install -r requirements.txt
```

### 2. Sozlamalar (.env)
`.env` faylida barcha sozlamalar kiritilgan:
```env
BOT_TOKEN=8665630444:AAFzII6PrF5M4osOOaN9yjOgN13935xgFGg
PHONE_NUMBER=33-355-87-77
ADDRESS_TEXT=Toshkent viloyati, Yangiyo'l tumani, Katta O'zbekiston trakti bo'yida ("ZAR BALIQ" choyxonasi)\nMo'ljal: Katta yo'l yoqasida, "ZAR BALIQ" yorqin stendi va baliq ramzi yonida
DEFAULT_DELIVERY_PRICE=20000
```

### 3. Mantiqiy testlarni tekshirish
```bash
py test_bot_logic.py
```

### 4. Botni ishga tushirish
```bash
py bot.py
```

Bot ishga tushgach, Telegram qidiruvidan o'z botingizni oching va `/start` bosing!
