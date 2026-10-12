import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(__file__), 'xon_moto.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vehicles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        category TEXT NOT NULL, /* 'luxury', 'budget', 'moto' */
        brand TEXT NOT NULL,
        model TEXT NOT NULL,
        year INTEGER NOT NULL,
        price INTEGER NOT NULL, /* in USD */
        mileage INTEGER NOT NULL, /* in km */
        engine TEXT NOT NULL,
        fuel_type TEXT NOT NULL,
        transmission TEXT NOT NULL,
        drive_type TEXT DEFAULT 'AWD',
        color TEXT NOT NULL,
        body_type TEXT NOT NULL,
        description TEXT,
        image_url TEXT NOT NULL,
        additional_images TEXT DEFAULT '[]',
        seller_name TEXT NOT NULL,
        seller_phone TEXT NOT NULL,
        seller_telegram TEXT,
        city TEXT NOT NULL,
        is_featured INTEGER DEFAULT 0,
        views INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS inquiries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_id INTEGER,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        message TEXT,
        inquiry_type TEXT DEFAULT 'xarid', /* 'xarid', 'test-drive', 'kredit' */
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE SET NULL
    )
    ''')

    # Boshlang'ich ma'lumotlar bor-yo'qligini tekshirish
    cursor.execute('SELECT COUNT(*) FROM vehicles')
    count = cursor.fetchone()[0]

    if count == 0:
        sample_vehicles = [
            # 1. QIMMATBAHO (LUXURY) MASHINALAR
            (
                "Mercedes-Benz G63 AMG Edition 1",
                "luxury",
                "Mercedes-Benz",
                "G63 AMG",
                2024,
                248000,
                3500,
                "4.0L V8 Biturbo (585 ot kuchi)",
                "Benzin",
                "9G-Tronic Avtomat",
                "To'liq (4WD)",
                "Matte Black (Qora matviy)",
                "SUV / Krossover",
                "Eng so'nggi rusumdagi Mercedes-Benz G63 AMG. Karbon paket, Burmester 3D audio tizimi, qizil nappa charm salon, tungi yoritgichlar, to'liq zirhli plyonka bilan himoyalangan. Holati a'lo darajada.",
                "https://images.unsplash.com/photo-1520050206274-a1ae44613e6d?auto=format&fit=crop&w=1200&q=80",
                json.dumps([
                    "https://images.unsplash.com/photo-1541348263662-e0c8de4259ba?auto=format&fit=crop&w=1200&q=80",
                    "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=80"
                ]),
                "XON_MOTO VIP Salon",
                "+998 90 777 00 01",
                "@xon_moto_vip",
                "Toshkent shahri",
                1,
                1420
            ),
            (
                "Porsche 911 Turbo S Coupe",
                "luxury",
                "Porsche",
                "911 Turbo S",
                2024,
                265000,
                1800,
                "3.8L Boxer Twin-Turbo (650 ot kuchi)",
                "Benzin",
                "8-bosqichli PDK",
                "AWD",
                "GT Silver Metallic",
                "Kupe / Sportkar",
                "Tezlanish: 0-100 km/soat 2.7 soniyada! Keramika tormozlar (PCCB), Sport Chrono to'plami, karbon tom, Sport exhaust tizimi. Haqiqiy sport avtomobili ishqibozlari uchun.",
                "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=80",
                json.dumps([
                    "https://images.unsplash.com/photo-1614162692292-7ac56d7f7f1e?auto=format&fit=crop&w=1200&q=80"
                ]),
                "XON_MOTO Exclusive",
                "+998 90 777 00 02",
                "@xon_moto_vip",
                "Toshkent shahri",
                1,
                1190
            ),
            (
                "BMW M5 CS Competition F90",
                "luxury",
                "BMW",
                "M5 CS",
                2023,
                142000,
                8200,
                "4.4L V8 M TwinPower (635 ot kuchi)",
                "Benzin",
                "M Steptronic 8-tezlik",
                "M xDrive (AWD/RWD)",
                "Frozen Deep Green",
                "Sedan",
                "Cheklangan seriyali BMW M5 CS. Karbon o'rindiqlar, oltinrang diska va tormoz supportlari, Harman Kardon audio, maksimal tezlik 305 km/soat. Butun O'zbekistonda sanoqli nusxalardan biri.",
                "https://images.unsplash.com/photo-1555215695-3004980ad54e?auto=format&fit=crop&w=1200&q=80",
                json.dumps([]),
                "Sardor Rahimov",
                "+998 97 123 45 67",
                "@sardor_m5",
                "Toshkent shahri",
                1,
                980
            ),
            (
                "Rolls-Royce Cullinan Black Badge",
                "luxury",
                "Rolls-Royce",
                "Cullinan",
                2023,
                510000,
                4200,
                "6.75L V12 Twin-Turbo (600 ot kuchi)",
                "Benzin",
                "8-tezlikli ZF Avtomat",
                "AWD",
                "Dark Diamond Black",
                "Premium SUV",
                "Dunyoning eng hashamatli yo'ltanlamasi. Yulduzli osmon shifti (Starlight Headliner), muzlatgich, shampan qadahlar jamlanmasi, massaj va shamollatishga ega individual orqa o'rindiqlar.",
                "https://images.unsplash.com/photo-1631295868223-63265b40d9e4?auto=format&fit=crop&w=1200&q=80",
                json.dumps([]),
                "XON_MOTO Elite Club",
                "+998 99 999 00 09",
                "@xon_moto_vip",
                "Toshkent shahri",
                1,
                2450
            ),
            (
                "Li Auto L9 Ultra Max",
                "luxury",
                "Li Auto",
                "L9 Ultra",
                2024,
                59500,
                1200,
                "1.5T Range Extender + 2x Elektromotor (449 ot kuchi)",
                "Gibrid",
                "Elektro-reduktor",
                "AWD",
                "Oltinrang kumush",
                "Krossover / Miniven",
                "Oilaviy premium gibrid krossover. 1315 km yurish masofasi (CLTC), pnevmatik podveska, OLED katta ekranlar, orqa qator kinoteatr ekrani va muzlatgich. To'liq ruslashtirilgan.",
                "https://images.unsplash.com/photo-1508974239320-0a029497e820?auto=format&fit=crop&w=1200&q=80",
                json.dumps([]),
                "Azizbek Auto",
                "+998 93 450 11 22",
                "@aziz_cars",
                "Samarqand shahri",
                1,
                860
            ),

            # 2. HAMYONBOP MASHINALAR (BUDGET & ECONOMY)
            (
                "Chevrolet Cobalt GX Style AT",
                "budget",
                "Chevrolet",
                "Cobalt",
                2024,
                13400,
                12000,
                "1.5L DOHC (106 ot kuchi)",
                "Benzin",
                "6-bosqichli Avtomat",
                "Oldi (FWD)",
                "GK2 Oq (Choco ichki bezak)",
                "Sedan",
                "Yangi avlod Cobalt 4-pozitsiya Style. Konditsioner, audio tizim, quyuq qoraytirilgan oynalar (tonirovka ruxsatnomasi bilan), yangi yumshoq shinalar o'rnatilgan. Xarajati yo'q, ideal holatda.",
                "https://images.unsplash.com/photo-1549399542-7e3f8b79c341?auto=format&fit=crop&w=1200&q=80",
                json.dumps([]),
                "Botirjon Aliyev",
                "+998 90 345 88 99",
                "@botir_cobalt",
                "Toshkent shahri",
                0,
                640
            ),
            (
                "Chevrolet Gentra (Lacetti) Elegance Plus CDX",
                "budget",
                "Chevrolet",
                "Gentra",
                2023,
                14100,
                24000,
                "1.5L DOHC (107 ot kuchi)",
                "Gaz-Benzin (4-avlod)",
                "Avtomat",
                "Oldi (FWD)",
                "Qora (Black Sapphire)",
                "Sedan",
                "Gentra 3-pozitsiya lyukli, ABS, magnitola, yangi 4-avlod propan gaz baloni o'rnatilgan. Kraskasi toza, hech qanday udar bo'lmagan. Hamyonbop va tejamkor avtomobil.",
                "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?auto=format&fit=crop&w=1200&q=80",
                json.dumps([]),
                "Jamshid Xoliqov",
                "+998 91 555 33 22",
                "@jamshid_gentra",
                "Farg'ona shahri",
                0,
                750
            ),
            (
                "Chevrolet Onix Premier 2 Turbo",
                "budget",
                "Chevrolet",
                "Onix",
                2024,
                16900,
                9000,
                "1.2L Turbo (132 ot kuchi)",
                "Benzin",
                "6-bosqichli Avtomat",
                "Oldi (FWD)",
                "Kumushrang metallik",
                "Sedan",
                "Premier maksimal komplektatsiya: simsiz quvvatlagich, yarim avtomatik parkovka, lyuk, kruiz nazorati, charm salon, o'rindiqlar isitgichi. Juda chaqqon va zamonaviy tejamkor avto.",
                "https://images.unsplash.com/photo-1542282088-72c9c27ed0cd?auto=format&fit=crop&w=1200&q=80",
                json.dumps([]),
                "Diyorbek Rustamov",
                "+998 94 620 40 40",
                "@diyor_onix",
                "Andijon shahri",
                0,
                530
            ),
            (
                "Chevrolet Tracker Premier Redline",
                "budget",
                "Chevrolet",
                "Tracker",
                2024,
                20900,
                15000,
                "1.2L Turbo (132 ot kuchi)",
                "Benzin",
                "6-bosqichli Avtomat",
                "Oldi (FWD)",
                "Muzdek oq (Summit White)",
                "Krossover",
                "Panoramali tom lyuki, LED optika, ko'rinmas hududlar datchigi, Redline maxsus qizil detallari. Shahar va sayohatlar uchun ajoyib qulay krossover.",
                "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?auto=format&fit=crop&w=1200&q=80",
                json.dumps([]),
                "Olimjon Qosimov",
                "+998 93 111 22 33",
                "@olim_tracker",
                "Namangan shahri",
                0,
                610
            ),
            (
                "BYD Chazor 05 DM-i Champion",
                "budget",
                "BYD",
                "Chazor 05",
                2024,
                18700,
                8000,
                "1.5L DM-i Super Hybrid (180 ot kuchi)",
                "Gibrid",
                "E-CVT",
                "Oldi (FWD)",
                "Kulrang (Space Gray)",
                "Sedan",
                "100 km masofaga atigi 3.8 litr sarflaydigan eng ommabop gibrid sedan. To'liq quvvat va bak bilan 1200+ km yuradi. 12.8 dyuym aylanuvchi ekran, DiPilot avtopilot tizimi.",
                "https://images.unsplash.com/photo-1580273916550-e323be2ae537?auto=format&fit=crop&w=1200&q=80",
                json.dumps([]),
                "Shaxzod Bekchanov",
                "+998 90 888 77 66",
                "@shaxzod_byd",
                "Toshkent shahri",
                0,
                890
            ),

            # 3. MOTOTSIKLLAR (MOTORCYCLES)
            (
                "Kawasaki Ninja ZX-10R KRT Edition",
                "moto",
                "Kawasaki",
                "Ninja ZX-10R",
                2024,
                19800,
                1200,
                "998cc 4-silindrli DOHC (203 ot kuchi)",
                "Benzin",
                "6-tezlikli Quickshifter bilan",
                "Orqa (Zanjirli)",
                "Lime Green / Ebony (Yashil-Qora)",
                "Sportbayk",
                "WorldSBK chempioni texnologiyasiga ega super mototsikl. Brembo Stylema tormoz tizimi, Showa Balance Free podveska, TFT rangli displey, Bluetooth ulanish, kruiz nazorati. O'ta yuqori dinamika!",
                "https://images.unsplash.com/photo-1558981806-ec527fa84c39?auto=format&fit=crop&w=1200&q=80",
                json.dumps([]),
                "XON_MOTO SuperBikes",
                "+998 90 777 00 03",
                "@xon_moto_bikes",
                "Toshkent shahri",
                1,
                1120
            ),
            (
                "BMW S 1000 RR M Sport Package",
                "moto",
                "BMW",
                "S 1000 RR",
                2024,
                24500,
                900,
                "999cc ShiftCam 4-silindrli (210 ot kuchi)",
                "Benzin",
                "6-tezlikli Pro Quickshifter",
                "Orqa (Zanjirli)",
                "Lightwhite / M Motorsport",
                "Sportbayk",
                "M Karbon diskalar, Akrapovic titan glushitel, Dynamic Damping Control (DDC), Race Pro rejimlari, aerodinamik qanotlar (winglets). Shahar va trek uchun eng mukammal sport moto.",
                "https://images.unsplash.com/photo-1568772585407-9361f9bf3a87?auto=format&fit=crop&w=1200&q=80",
                json.dumps([]),
                "Javohir Moto",
                "+998 97 700 88 99",
                "@javohir_bmwmoto",
                "Toshkent shahri",
                1,
                1340
            ),
            (
                "Yamaha YZF-R1 Monster Energy",
                "moto",
                "Yamaha",
                "YZF-R1",
                2023,
                18500,
                3400,
                "998cc Crossplane CP4 (200 ot kuchi)",
                "Benzin",
                "6-tezlikli Mexanika",
                "Orqa (Zanjirli)",
                "Monster Energy Black/Blue",
                "Sportbayk",
                "MotoGP texnologiyasiga asoslangan krosspleyn dvigatel. Quloqni qomatga keltiruvchi ovoz, yuqori burchakli tezlik nazorati, launch control, ABS va slayder himoyalari bilan to'liq jihozlangan.",
                "https://images.unsplash.com/photo-1558981403-c5f9899a28bc?auto=format&fit=crop&w=1200&q=80",
                json.dumps([]),
                "Temur Karimov",
                "+998 93 300 44 55",
                "@temur_r1",
                "Samarqand shahri",
                0,
                920
            ),
            (
                "Harley-Davidson Fat Boy 114",
                "moto",
                "Harley-Davidson",
                "Fat Boy 114",
                2023,
                22900,
                4100,
                "1868cc Milwaukee-Eight 114 V-Twin (94 ot kuchi)",
                "Benzin",
                "6-tezlikli Cruise Drive",
                "Orqa (Remenli)",
                "Vivid Black (Yaltiroq qora)",
                "Kruizer / Chopper",
                "Afsonaviy 'Terminator' uslubidagi Harley-Davidson Fat Boy! Keng 240mm orqa g'ildirak, xrom detallar, gumburlagan V-Twin drayvi, Vance & Hines ovoz tizimi. Haqiqiy xarakter egasi uchun.",
                "https://images.unsplash.com/photo-1558980664-769d59546b3d?auto=format&fit=crop&w=1200&q=80",
                json.dumps([]),
                "XON_MOTO Cruisers",
                "+998 90 777 00 04",
                "@xon_moto_bikes",
                "Toshkent shahri",
                0,
                880
            ),
            (
                "Ducati Panigale V4 S",
                "moto",
                "Ducati",
                "Panigale V4 S",
                2024,
                31500,
                1500,
                "1103cc Desmosedici Stradale V4 (215.5 ot kuchi)",
                "Benzin",
                "6-tezlikli Ducati Quick Shift (DQS) EVO 2",
                "Orqa (Zanjirli)",
                "Ducati Red (Afsonaviy qizil)",
                "Superbayk",
                "Italiya muhandisligining durdonasi. Ohlins elektron boshqariladigan podveska, Marchesini alyuminiy diskalar, aerodinamik paketi. 100 km/soat ga 2.9 soniya.",
                "https://images.unsplash.com/photo-1609630875171-b1321377ee65?auto=format&fit=crop&w=1200&q=80",
                json.dumps([]),
                "XON_MOTO VIP Salon",
                "+998 90 777 00 01",
                "@xon_moto_vip",
                "Toshkent shahri",
                1,
                1670
            ),
            (
                "Vespa GTS SuperTech 300 HPE",
                "moto",
                "Vespa",
                "GTS SuperTech 300",
                2024,
                8200,
                500,
                "278cc 4-taktli HPE (24 ot kuchi)",
                "Benzin",
                "Avtomat Variator (CVT)",
                "Orqa",
                "Grigio Ottanio (Nafis Kulrang-Moviy)",
                "Premium Skuter",
                "Italiyaning premium shahar skuteri. TFT rangli displey, navigatsiya, ABS va ASR (tortishish nazorati), yangi to'liq LED faralar, qulay charm o'rindiq. Shahar tirbandliklarida eng nafis tanlov.",
                "https://images.unsplash.com/photo-1568772585407-9361f9bf3a87?auto=format&fit=crop&w=1200&q=80",
                json.dumps([]),
                "Shahnoza Karimova",
                "+998 91 234 56 78",
                "@shahnoza_vespa",
                "Toshkent shahri",
                0,
                490
            )
        ]

        cursor.executemany('''
        INSERT INTO vehicles (
            title, category, brand, model, year, price, mileage, engine,
            fuel_type, transmission, drive_type, color, body_type, description,
            image_url, additional_images, seller_name, seller_phone, seller_telegram,
            city, is_featured, views
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_vehicles)

    conn.commit()
    conn.close()

def get_vehicles(category=None, search=None, min_price=None, max_price=None, sort_by=None, limit=None, offset=None):
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM vehicles WHERE 1=1"
    params = []

    if category and category != 'all':
        query += " AND category = ?"
        params.append(category)

    if search:
        query += " AND (title LIKE ? OR brand LIKE ? OR model LIKE ? OR city LIKE ? OR description LIKE ?)"
        wildcard = f"%{search}%"
        params.extend([wildcard, wildcard, wildcard, wildcard, wildcard])

    if min_price is not None and str(min_price).strip() != '':
        query += " AND price >= ?"
        params.append(int(min_price))

    if max_price is not None and str(max_price).strip() != '':
        query += " AND price <= ?"
        params.append(int(max_price))

    if sort_by == 'price_asc':
        query += " ORDER BY price ASC"
    elif sort_by == 'price_desc':
        query += " ORDER BY price DESC"
    elif sort_by == 'year_desc':
        query += " ORDER BY year DESC"
    elif sort_by == 'popular':
        query += " ORDER BY views DESC"
    else:
        query += " ORDER BY is_featured DESC, id DESC"

    if limit:
        query += f" LIMIT {int(limit)}"
        if offset:
            query += f" OFFSET {int(offset)}"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    vehicles = [dict(row) for row in rows]
    conn.close()
    return vehicles

def get_vehicle_by_id(vehicle_id):
    conn = get_connection()
    cursor = conn.cursor()
    # ko'rishlar sonini 1 taga oshirish
    cursor.execute("UPDATE vehicles SET views = views + 1 WHERE id = ?", (vehicle_id,))
    conn.commit()

    cursor.execute("SELECT * FROM vehicles WHERE id = ?", (vehicle_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        v = dict(row)
        try:
            v['additional_images'] = json.loads(v['additional_images'])
        except Exception:
            v['additional_images'] = []
        return v
    return None

def add_vehicle(data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO vehicles (
        title, category, brand, model, year, price, mileage, engine,
        fuel_type, transmission, drive_type, color, body_type, description,
        image_url, additional_images, seller_name, seller_phone, seller_telegram,
        city, is_featured
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('title'),
        data.get('category'),
        data.get('brand'),
        data.get('model'),
        int(data.get('year', 2024)),
        int(data.get('price', 0)),
        int(data.get('mileage', 0)),
        data.get('engine', 'Standart'),
        data.get('fuel_type', 'Benzin'),
        data.get('transmission', 'Avtomat'),
        data.get('drive_type', 'Oldi'),
        data.get('color', 'Oq'),
        data.get('body_type', 'Sedan'),
        data.get('description', ''),
        data.get('image_url', ''),
        json.dumps(data.get('additional_images', [])),
        data.get('seller_name'),
        data.get('seller_phone'),
        data.get('seller_telegram', ''),
        data.get('city', 'Toshkent shahri'),
        int(data.get('is_featured', 0))
    ))
    vehicle_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return vehicle_id

def delete_vehicle(vehicle_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vehicles WHERE id = ?", (vehicle_id,))
    conn.commit()
    conn.close()
    return True

def add_inquiry(vehicle_id, name, phone, message, inquiry_type='xarid'):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO inquiries (vehicle_id, name, phone, message, inquiry_type)
    VALUES (?, ?, ?, ?, ?)
    ''', (vehicle_id, name, phone, message, inquiry_type))
    conn.commit()
    conn.close()

def get_stats():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM vehicles")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM vehicles WHERE category = 'luxury'")
    luxury = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM vehicles WHERE category = 'budget'")
    budget = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM vehicles WHERE category = 'moto'")
    moto = cursor.fetchone()[0]

    conn.close()
    return {
        'total': total,
        'luxury': luxury,
        'budget': budget,
        'moto': moto
    }
