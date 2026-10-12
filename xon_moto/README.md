# 🏎️ XON_MOTO — Mashinalar va Mototsikllar Bozori

**XON_MOTO** — O'zbekistondagi zamonaviy, tezkor va hashamatli avto-moto savdo platformasi. 

Bu yerda:
- 👑 **Qimmatbaho mashinalar (Luxury)**: Mercedes-Benz G63 AMG, Porsche 911 Turbo S, BMW M5 CS, Rolls-Royce Cullinan, Li Auto L9 va boshqalar.
- 💰 **Hamyonbop xalqona mashinalar (Budget)**: Chevrolet Cobalt, Gentra, Onix, Tracker, BYD Chazor va boshqalar.
- 🏍️ **Mototsikllar & Skuterlar (Moto)**: Kawasaki Ninja ZX-10R, BMW S1000RR, Yamaha R1, Ducati Panigale, Harley-Davidson, Vespa.
- 📝 **E'lon berish formasi**: Foydalanuvchilar o'z mashina va motosikllarini rasmlari, narxi va tafsilotlari bilan sotuvga qo'yishi mumkin.
- 🧮 **Avtokredit kalkulyatori**: Boshlang'ich to'lov, foiz va muddat bo'yicha oylik to'lovni avtomatik hisoblash.
- 🛡️ **Admin boshqaruv paneli**: Barcha e'lonlarni ko'rish va o'chirish.

---

## 🚀 Ishga tushirish

1. `xon_moto` papkasiga o'ting.
2. `run_xon_moto.bat` faylini ikki marta bosing yoki terminalda:
```powershell
cd xon_moto
py app.py
```
3. Brauzerda oching: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 📂 Loyiha tuzilishi

- `app.py` — Flask backend, yo'nalishlar (routes) va API
- `database.py` — SQLite ma'lumotlar bazasi va dastlabki boyitilgan e'lonlar
- `templates/` — HTML shablonlar (Jinja2):
  - `base.html` — Asosiy zamonaviy qora-oltin mavzudagi navigatsiya va footer
  - `index.html` — Bosh sahifa (qidiruv, bo'limlar, ko'rgazma zali)
  - `catalog.html` — To'liq filtrli katalog
  - `detail.html` — Mashina/moto batafsil sahifasi va xarid formasi
  - `add_listing.html` — O'z mashinasini sotish uchun e'lon berish formasi
  - `calculator.html` — Kredit kalkulyatori
  - `contact.html` — Aloqa va manzil
  - `admin.html` — Moderatsiya paneli
- `static/` — CSS, JS va yuklangan fayllar:
  - `css/style.css` — Maxsus luxury avtosalon stillari
  - `js/main.js` — Kredit kalkulyatori logikasi, AJAX va prevyular
  - `uploads/` — Foydalanuvchilar yuklagan fotosuratlar
