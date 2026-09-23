from pathlib import Path
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from config import is_admin
from database.db import (
    add_or_update_user,
    get_setting,
    get_main_product,
    get_products,
    get_products_by_category,
    get_all_admin_ids,
    add_admin_id
)
from keyboards.default_keyboards import get_main_keyboard
from keyboards.inline_keyboards import (
    get_somsa_page_keyboard,
    get_fish_page_keyboard,
    get_location_inline_keyboard,
    get_group_keyboard,
    get_phone_keyboard
)
from utils.helpers import format_price, escape_text

router = Router(name="user_handlers")

@router.message(Command("myid"))
async def cmd_myid(message: Message):
    """Foydalanuvchining o'z Telegram ID sini ko'rsatish"""
    uid = message.from_user.id
    admins = await get_all_admin_ids()
    is_adm = uid in admins
    adm_text = "Siz <b>Admin</b>siz!" if is_adm else "Siz oddiy foydalanuvchisiz."

    await message.answer(
        f"🆔 <b>Sizning Telegram ID raqamingiz:</b> <code>{uid}</code>\n"
        f"👤 <b>Holatingiz:</b> {adm_text}\n\n"
        f"<i>Agar admin bo'lmoqchi bo'lsangiz: <code>/setadmin</code> buyrug'ini yuboring.</i>",
        parse_mode="HTML"
    )

@router.message(Command("setadmin"))
async def cmd_setadmin(message: Message):
    """Admin tayinlash buyrug'i"""
    uid = message.from_user.id
    admins = await get_all_admin_ids()

    if not admins:
        # Birinchi foydalanuvchini avtomatik bosh admin qilish
        await add_admin_id(uid)
        await message.answer(
            f"🎉 <b>Tabriklaymiz!</b>\n\n"
            f"Siz (ID: <code>{uid}</code>) <b>ZAR BALIQ</b> boti bosh administratori etib tayinlandingiz!\n\n"
            f"Endi botdagi yangi buyurtmalar sizga keladi va <b>⚙️ Admin Panel</b> imkoniyatlaridan to'liq foydalana olasiz.",
            reply_markup=get_main_keyboard(is_admin=True),
            parse_mode="HTML"
        )
    elif uid in admins:
        await message.answer(
            "✅ Siz allaqachon bot administratorisiz!\n\n"
            "Admin panelga kirish uchun pastdagi <b>⚙️ Admin Panel</b> tugmasini bosing yoki <code>/admin</code> deb yozing.",
            reply_markup=get_main_keyboard(is_admin=True),
            parse_mode="HTML"
        )
    else:
        await message.answer(
            "⚠️ Botda allaqachon bosh administrator mavjud. Qo'shimcha admin qo'shish uchun mavjud admin bilan bog'laning."
        )

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Foydalanuvchi /start bosganda chiroyli kutib olish xabari"""
    await state.clear()
    user = message.from_user
    if user:
        await add_or_update_user(
            user_id=user.id,
            username=user.username,
            full_name=user.full_name
        )

    admins = await get_all_admin_ids()
    # Agar bazada hali hech qanday admin bo'lmasa, birinchi bo'lib /start bosgan foydalanuvchini avtomatik admin qilish
    if not admins and user:
        await add_admin_id(user.id)
        admin_status = True
    else:
        admin_status = user.id in admins if user else False

    phone = await get_setting("phone_number", "33-355-87-77")
    address = await get_setting("address_text", "Qashqadaryo viloyati, Shahrisabz tumani, Shamaton mahallasi")

    welcome_text = (
        "Assalomu alaykum! 'ZAR BALIQ' choyxonasining rasmiy botiga xush kelibsiz! 🐟🥟\n\n"
        "🍽 <b>ASOSIY TAOMLARIMIZ VA NARXLAR:</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🥟 <b>SOMSA NARXI:</b> <b>8 000 so‘m</b> (1 dona)\n"
        "🐟 <b>BALIQ NARXI:</b> <b>85 000 so‘m</b> (1 kg qovurilgan baliq)\n"
        "👑 <b>ZAR BALIQ Assorti:</b> <b>350 000 so‘m</b> (Katta patnis)\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📍 <b>Manzil:</b> {address}\n"
        f"📞 <b>Telefon:</b> <code>{phone}</code>\n\n"
        "👇 <b>Quyidagi tugmalardan birini tanlang:</b>"
    )

    if admin_status:
        welcome_text += "\n\n<i>👑 Siz bot administratori sifatida biriktirildingiz!</i>"

    await message.answer(
        text=welcome_text,
        reply_markup=get_main_keyboard(is_admin=admin_status),
        parse_mode="HTML"
    )

# --- 🥟 SOMSA NARXLARI BO'LIMI ---
@router.message(Command("somsa"))
@router.message(F.text.in_({"🥟 Somsa narxlari", "Somsa narxlari", "🥟 Somsa", "Somsa"}))
async def show_somsa_menu(message: Message):
    """Somsa turlari va narxlari haqida to'liq ma'lumot"""
    somsalar = await get_products_by_category("somsa", only_active=True)
    phone = await get_setting("phone_number", "33-355-87-77")

    text = "🥟 <b>'ZAR BALIQ' — Somsalar Menyusi va Narxlari</b>\n\n"
    text += "🔥 <b>Barcha somsalarimiz narxi: 8 000 so‘m / dona</b>\n"
    text += "<i>Yangi, issiq va qarsildoq holda tandirdan uzib tortiladi!</i>\n\n"

    if not somsalar:
        text += (
            "1. <b>🥟 Mazali Tandir Somsa</b> — <b>8 000 so‘m</b>\n"
            "2. <b>🥟 Maxsus Baliqli Somsa</b> — <b>8 000 so‘m</b>\n"
            "3. <b>🥟 Qatlama Tandir Somsa</b> — <b>8 000 so‘m</b>\n\n"
        )
    else:
        for idx, item in enumerate(somsalar, start=1):
            name = item["name"]
            desc = item.get("description", "")
            price = format_price(item["price_unit"])
            text += f"<b>{idx}. {name}</b>\n"
            if desc:
                text += f"   <i>{desc}</i>\n"
            text += f"   💰 Narxi: <b>{price} / dona</b>\n\n"

    text += (
        "📊 <b>Narxlar jadvali:</b>\n"
        "• 1 dona — <b>8 000 so‘m</b>\n"
        "• 2 dona — <b>16 000 so‘m</b>\n"
        "• 5 dona — <b>40 000 so‘m</b>\n"
        "• 10 dona — <b>80 000 so‘m</b>\n\n"
        f"📞 <b>Buyurtma uchun:</b> <code>{phone}</code>\n"
        "📍 <b>Manzil:</b> Qashqadaryo viloyati, Shahrisabz tumani, Shamaton mahallasi"
    )

    await message.answer(
        text=text,
        reply_markup=get_somsa_page_keyboard(phone),
        parse_mode="HTML"
    )

# --- 🐟 BALIQ NARXLARI BO'LIMI ---
@router.message(Command("baliq"))
@router.message(F.text.in_({"🐟 Baliq narxlari", "Baliq narxlari", "🐟 Baliq", "Baliq", "🐟 SOMSA BALIQ"}))
async def show_fish_menu(message: Message):
    """Baliq taomlari va narxlari haqida to'liq ma'lumot"""
    baliqlar = await get_products_by_category("baliq", only_active=True)
    phone = await get_setting("phone_number", "33-355-87-77")

    text = "🐟 <b>'ZAR BALIQ' — Baliq Taomlari va Narxlari</b>\n\n"
    text += "🔥 <b>Qovurilgan sara baliqlarimiz: 85 000 so‘m (1 kg)</b>\n"
    text += "<i>Har kuni yangi tutilgan sara baliqlar, maxsus sous va limon bilan!</i> 😋\n\n"

    if not baliqlar:
        text += (
            "1. <b>🐟 Mazali Qovurilgan Baliq</b> — <b>85 000 so‘m (1 kg)</b>\n"
            "2. <b>🐟 Sazan (Zog'ora baliq)</b> — <b>85 000 so‘m (1 kg)</b>\n"
            "3. <b>🐟 Sudak (Oq baliq)</b> — <b>85 000 so‘m (1 kg)</b>\n"
            "4. <b>👑 ZAR BALIQ Assorti (Patnis)</b> — <b>350 000 so‘m</b>\n\n"
        )
    else:
        for idx, item in enumerate(baliqlar, start=1):
            name = item["name"]
            desc = item.get("description", "")
            price = format_price(item["price_unit"])
            text += f"<b>{idx}. {name}</b>\n"
            if desc:
                text += f"   <i>{desc}</i>\n"
            text += f"   💰 Narxi: <b>{price}</b>\n\n"

    text += (
        "🎁 <i>Har bir baliq taomiga maxsus sarimsoqli sous, yangi piyoz va limon bepul taqdim etiladi!</i>\n\n"
        f"📞 <b>Buyurtma uchun:</b> <code>{phone}</code>\n"
        "📍 <b>Manzil:</b> Qashqadaryo viloyati, Shahrisabz tumani, Shamaton mahallasi"
    )

    await message.answer(
        text=text,
        reply_markup=get_fish_page_keyboard(phone),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "show_phone_direct")
async def callback_show_phone(callback: CallbackQuery):
    """Inline tugmadan telefon raqamni ko'rsatish"""
    phone = await get_setting("phone_number", "33-355-87-77")
    await callback.answer(f"📞 Bog'lanish: {phone}", show_alert=True)

@router.callback_query(F.data == "show_location_direct")
async def callback_show_location(callback: CallbackQuery):
    """Inline tugmadan manzilni ko'rsatish"""
    await callback.answer()
    await show_location(callback.message)

# --- 📍 MANZIL BO'LIMI ---
@router.message(Command("manzil"))
@router.message(F.text.in_({"📍 Manzil", "Manzil", "Manzilimiz", "📍 Joylashuv"}))
async def show_location(message: Message):
    """Manzil va joylashuv ma'lumotlari"""
    address_text = await get_setting(
        "address_text",
        "Qashqadaryo viloyati, Shahrisabz tumani, Shamaton mahallasi (\"ZAR BALIQ\" choyxonasi)"
    )
    work_hours = await get_setting("work_hours", "Har kuni 10:00 dan 23:00 gacha (dam olish kunlarisiz)")
    phone = await get_setting("phone_number", "33-355-87-77")
    lat_str = await get_setting("location_lat", "39.0558")
    lon_str = await get_setting("location_lon", "66.8286")

    try:
        lat = float(lat_str)
        lon = float(lon_str)
    except (ValueError, TypeError):
        lat, lon = 39.0558, 66.8286

    text = (
        "📍 <b>'ZAR BALIQ' Choyxonasi Manzili:</b>\n\n"
        f"🏢 <b>Aniq manzil:</b>\n{address_text}\n\n"
        f"⏰ <b>Ish vaqti:</b> {work_hours}\n"
        f"📞 <b>Telefon:</b> <b>{phone}</b>\n"
        "🚗 <b>Avtoturargoh:</b> Keng va qulay bepul avtoturargoh mavjud.\n\n"
        "<i>Marhamat, oilangiz va do'stlaringiz bilan tashrif buyuring, sizni kutamiz!</i> 😊"
    )

    # Avval manzil va xarita tugmalarini jo'natamiz
    await message.answer(
        text=text,
        reply_markup=get_location_inline_keyboard(phone=phone, lat=lat, lon=lon),
        parse_mode="HTML"
    )

    # Shuningdek xaritada qulay ko'rinishi uchun lokatsiyani ham yuboramiz
    try:
        await message.answer_location(latitude=lat, longitude=lon)
    except Exception:
        pass

# --- 📞 BOG'LANISH BO'LIMI ---
@router.message(Command("aloqa"))
@router.message(Command("phone"))
@router.message(F.text.in_({"📞 Bog'lanish", "📞 Telefon", "Bog'lanish", "Telefon", "Aloqa"}))
async def show_contact(message: Message):
    """Telefon va aloqa ma'lumotlari"""
    phone = await get_setting("phone_number", "33-355-87-77")
    work_hours = await get_setting("work_hours", "Har kuni 10:00 dan 23:00 gacha")

    text = (
        "📞 <b>'ZAR BALIQ' Choyxonasi bilan bog'lanish</b>\n\n"
        "Mazali taomlarga buyurtma berish, so'roqlar yoki choyxonamizda stol band qilish (bron qilish) "
        "uchun biz bilan bog'lanishingiz mumkin:\n\n"
        f"📱 <b>Telefon raqam:</b> <b>{phone}</b>\n"
        f"⏰ <b>Qabul vaqti:</b> {work_hours}\n"
        "🚚 <b>Yetkazib berish:</b> Shahar va tumanlar bo'ylab mavjud\n\n"
        "<i>Qo'ng'iroq qilish yoki buyurtma berish uchun pastdagi tugmalardan foydalaning:</i>"
    )

    await message.answer(
        text=text,
        reply_markup=get_phone_keyboard(phone),
        parse_mode="HTML"
    )

# --- 📋 UMUMIY MENYU VA NARXLAR ---
@router.message(Command("menu"))
@router.message(F.text.in_({"📋 Menyu va narxlar", "📋 Menyu", "Menyu"}))
async def show_all_menu(message: Message):
    """Barcha taomlar (somsa va baliq) ro'yxati"""
    products = await get_products(only_active=True)
    phone = await get_setting("phone_number", "33-355-87-77")

    text = "📋 <b>'ZAR BALIQ' — To'liq Taomnoma</b>\n\n"

    if not products:
        text += "Hozirda menyuda mahsulotlar mavjud emas."
    else:
        for p in products:
            u_price = p["price_unit"]
            cat_emoji = "🥟" if p.get("category") == "somsa" or "somsa" in p["name"].lower() else "🐟"
            text += (
                f"{cat_emoji} <b>{p['name']}</b>\n"
                f"<i>{p.get('description', '')}</i>\n"
                f"• Narxi: <b>{format_price(u_price)}</b>\n\n"
            )

    text += (
        "Buyurtma berish uchun pastdagi <b>🛒 Buyurtma berish</b> tugmasini bosing yoki qo'ng'iroq qiling.\n"
        f"📞 <b>Telefon:</b> {phone}"
    )

    await message.answer(
        text=text,
        reply_markup=get_phone_keyboard(phone),
        parse_mode="HTML"
    )

# --- 🚚 YETKAZIB BERISH ---
@router.message(Command("delivery"))
@router.message(F.text.in_({"🚚 Yetkazib berish", "Yetkazib berish"}))
async def show_delivery_info(message: Message):
    """Yetkazib berish ma'lumotlari"""
    delivery_info = await get_setting("delivery_info")
    delivery_price = await get_setting("delivery_price", "20000")
    formatted_price = format_price(delivery_price)

    text = (
        f"{delivery_info}\n\n"
        f"💰 Standart yetkazib berish narxi: <b>{formatted_price}</b>\n\n"
        f"Buyurtma berish uchun <b>🛒 Buyurtma berish</b> tugmasini bosing."
    )

    await message.answer(
        text=text,
        reply_markup=get_somsa_page_keyboard(),
        parse_mode="HTML"
    )

# --- 👥 TELEGRAM GURUH ---
@router.message(F.text.in_({"👥 Telegram guruhimiz", "Telegram guruhimiz"}))
async def show_telegram_group(message: Message):
    """Telegram guruh havolasi"""
    group_link = await get_setting("telegram_group_link", "BU_YERGA_GURUH_LINKI")

    if not group_link or group_link == "BU_YERGA_GURUH_LINKI":
        text = (
            "👥 <b>'ZAR BALIQ'</b> Telegram guruhi tez orada ishga tushadi!\n"
            "Guruh havolasi yangilangach bu yerda e'lon qilinadi."
        )
        await message.answer(text=text, parse_mode="HTML")
    else:
        text = (
            "👥 <b>'ZAR BALIQ'</b> rasmiy Telegram guruhimizga a'zo bo'ling!\n\n"
            "Guruhda maxsus aksiyalar, chegirmalar va yangiliklar e'lon qilib boriladi."
        )
        await message.answer(
            text=text,
            reply_markup=get_group_keyboard(group_link),
            parse_mode="HTML"
        )

# --- ℹ️ BIZ HAQIMIZDA ---
@router.message(Command("about"))
@router.message(F.text.in_({"ℹ️ Biz haqimizda", "Biz haqimizda"}))
async def show_about(message: Message):
    """Biz haqimizda ma'lumot"""
    about_text = await get_setting("about_text")
    phone = await get_setting("phone_number", "33-355-87-77")

    text = f"{about_text}\n\n📞 Murojaat uchun: <b>{phone}</b>"
    await message.answer(
        text=text,
        reply_markup=get_phone_keyboard(phone),
        parse_mode="HTML"
    )
