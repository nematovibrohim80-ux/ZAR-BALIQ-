import asyncio
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.filters import Command, BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from database.db import (
    get_setting,
    set_setting,
    get_products,
    get_product_by_id,
    add_product,
    update_product,
    get_order,
    update_order_status,
    get_pending_orders,
    get_recent_orders,
    get_statistics,
    get_all_users,
    get_all_admin_ids
)
from states.admin_states import AdminStates
from keyboards.default_keyboards import get_main_keyboard, get_cancel_keyboard
from keyboards.inline_keyboards import (
    get_admin_main_keyboard,
    get_admin_products_keyboard,
    get_admin_product_edit_keyboard,
    get_admin_settings_keyboard,
    get_admin_back_keyboard
)
from utils.helpers import format_price, escape_text, clean_phone, is_valid_phone

router = Router(name="admin_handlers")

class IsAdminFilter(BaseFilter):
    """Adminlik huquqini dinamik tekshiruvchi asinxron filtr"""
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        if not event.from_user:
            return False
        admins = await get_all_admin_ids()
        return event.from_user.id in admins

admin_filter = IsAdminFilter()

# Routerning barcha xabarlariga avtomatik admin filtrini ulash
router.message.filter(admin_filter)
router.callback_query.filter(admin_filter)

# --- Admin bosh menyusi ---
@router.message(Command("admin"))
@router.message(F.text == "⚙️ Admin Panel")
async def open_admin_panel(message: Message, state: FSMContext):
    """Admin panelini ochish"""
    await state.clear()
    text = (
        "⚙️ <b>ZAR BALIQ — Administrator Paneli</b>\n\n"
        "Kerakli bo'limni tanlang:"
    )
    await message.answer(text=text, reply_markup=get_admin_main_keyboard(), parse_mode="HTML")

@router.callback_query(F.data == "adm_back_main")
async def back_to_admin_main(callback: CallbackQuery, state: FSMContext):
    """Admin asosiy menyusiga qaytish"""
    await state.clear()
    text = (
        "⚙️ <b>ZAR BALIQ — Administrator Paneli</b>\n\n"
        "Kerakli bo'limni tanlang:"
    )
    await callback.message.edit_text(text=text, reply_markup=get_admin_main_keyboard(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "adm_close", admin_filter)
async def close_admin_panel(callback: CallbackQuery, state: FSMContext):
    """Admin panelidan chiqish"""
    await state.clear()
    await callback.message.delete()
    await callback.message.answer(
        "Asosiy menyuga qaytdingiz.",
        reply_markup=get_main_keyboard(is_admin=True)
    )
    await callback.answer()

# --- Buyurtmani qabul qilish va rad etish ---
@router.callback_query(F.data.startswith("adm_accept_"), admin_filter)
async def handle_accept_order(callback: CallbackQuery, bot: Bot):
    """Admin buyurtmani qabul qilganda"""
    order_id = int(callback.data.split("_")[-1])
    order = await get_order(order_id)
    if not order:
        await callback.answer("Buyurtma topilmadi!", show_alert=True)
        return

    await update_order_status(order_id, "accepted")

    # Mijozga bildirishnoma
    try:
        await bot.send_message(
            chat_id=order["user_id"],
            text=f"✅ <b>Buyurtmangiz qabul qilindi! Tez orada siz bilan bog‘lanamiz.</b>\n\n"
                 f"Buyurtma raqami: <b>#{order_id}</b>",
            parse_mode="HTML"
        )
    except Exception:
        pass

    # Admin xabarini yangilash
    updated_text = (
        f"{callback.message.html_text}\n\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"✅ <b>QABUL QILINDI</b> (Admin: @{callback.from_user.username or callback.from_user.full_name})"
    )
    try:
        await callback.message.edit_text(updated_text, reply_markup=None, parse_mode="HTML")
    except Exception:
        pass

    await callback.answer("Buyurtma qabul qilindi!")

@router.callback_query(F.data.startswith("adm_reject_"), admin_filter)
async def handle_reject_order(callback: CallbackQuery, bot: Bot):
    """Admin buyurtmani rad etganda"""
    order_id = int(callback.data.split("_")[-1])
    order = await get_order(order_id)
    if not order:
        await callback.answer("Buyurtma topilmadi!", show_alert=True)
        return

    await update_order_status(order_id, "rejected")
    phone = await get_setting("phone_number", "+998 33 355 87 77")

    # Mijozga bildirishnoma
    try:
        await bot.send_message(
            chat_id=order["user_id"],
            text=f"❌ <b>Afsuski, #{order_id} raqamli buyurtmangizni hozir qabul qila olmaymiz. "
                 f"Telefon orqali bog‘lanishingiz mumkin: {phone}</b>",
            parse_mode="HTML"
        )
    except Exception:
        pass

    # Admin xabarini yangilash
    updated_text = (
        f"{callback.message.html_text}\n\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"❌ <b>RAD ETILDI</b> (Admin: @{callback.from_user.username or callback.from_user.full_name})"
    )
    try:
        await callback.message.edit_text(updated_text, reply_markup=None, parse_mode="HTML")
    except Exception:
        pass

    await callback.answer("Buyurtma rad etildi!")

# --- Statistika ---
@router.callback_query(F.data == "adm_stats", admin_filter)
async def show_stats(callback: CallbackQuery):
    """Bot statistikasini ko'rsatish"""
    stats = await get_statistics()
    text = (
        "📊 <b>ZAR BALIQ — Statistika</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{stats['total_users']} ta</b>\n"
        f"📦 Jami buyurtmalar: <b>{stats['total_orders']} ta</b>\n"
        f"⏳ Kutilayotgan buyurtmalar: <b>{stats['pending_orders']} ta</b>\n"
        f"✅ Qabul qilingan buyurtmalar: <b>{stats['accepted_orders']} ta</b>\n"
        f"💰 Jami tushum (qabul qilingan): <b>{format_price(stats['total_revenue'])}</b>"
    )
    await callback.message.edit_text(text=text, reply_markup=get_admin_back_keyboard(), parse_mode="HTML")
    await callback.answer()

# --- Buyurtmalar ro'yxati ---
@router.callback_query(F.data == "adm_orders", admin_filter)
async def show_orders_list(callback: CallbackQuery):
    """So'nggi buyurtmalar ro'yxati"""
    pending = await get_pending_orders()
    recent = await get_recent_orders(limit=5)

    text = "📋 <b>Buyurtmalar holati:</b>\n\n"

    if pending:
        text += f"⏳ <b>Kutilayotgan buyurtmalar ({len(pending)} ta):</b>\n"
        for o in pending[:5]:
            text += (
                f"• #{o['id']} | {o['product_name']} x{o['quantity']} | "
                f"{format_price(o['total_price'])} | {o['customer_phone']}\n"
            )
        text += "\n"
    else:
        text += "⏳ Kutilayotgan buyurtmalar yo'q.\n\n"

    text += "🕒 <b>So'nggi 5 ta buyurtma:</b>\n"
    if recent:
        for o in recent:
            st = "✅" if o["status"] == "accepted" else ("❌" if o["status"] == "rejected" else "⏳")
            text += (
                f"{st} #{o['id']} | {o['product_name']} x{o['quantity']} | "
                f"{format_price(o['total_price'])} | {o['created_at'][:16]}\n"
            )
    else:
        text += "Hali buyurtmalar mavjud emas."

    await callback.message.edit_text(text=text, reply_markup=get_admin_back_keyboard(), parse_mode="HTML")
    await callback.answer()

# --- Sozlamalar menyusi ---
@router.callback_query(F.data == "adm_settings", admin_filter)
async def show_settings(callback: CallbackQuery, state: FSMContext):
    """Tizim sozlamalari ko'rinishi"""
    await state.clear()
    phone = await get_setting("phone_number", "+998 33 355 87 77")
    group = await get_setting("telegram_group_link", "BU_YERGA_GURUH_LINKI")
    delivery = await get_setting("delivery_price", "20000")

    text = (
        "⚙️ <b>Tizim Sozlamalari:</b>\n\n"
        f"📞 <b>Telefon raqami:</b> {phone}\n"
        f"👥 <b>Guruh linki:</b> {group}\n"
        f"🚚 <b>Yetkazib berish narxi:</b> {format_price(delivery)}\n\n"
        f"<i>O'zgartirmoqchi bo'lgan parametrni tanlang:</i>"
    )
    await callback.message.edit_text(text=text, reply_markup=get_admin_settings_keyboard(), parse_mode="HTML")
    await callback.answer()

# --- Sozlamalarni tahrirlash (Telefon) ---
@router.callback_query(F.data == "adm_set_phone", admin_filter)
async def start_edit_phone(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.editing_phone)
    await callback.message.answer(
        "📞 Yangi telefon raqamini kiriting (Masalan: <code>+998 33 355 87 77</code>):",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(AdminStates.editing_phone, F.text, admin_filter)
async def save_new_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    await set_setting("phone_number", phone)
    await state.clear()
    await message.answer(
        f"✅ Telefon raqami yangilandi: <b>{phone}</b>",
        reply_markup=get_main_keyboard(is_admin=True),
        parse_mode="HTML"
    )

# --- Sozlamalarni tahrirlash (Telegram guruh linki) ---
@router.callback_query(F.data == "adm_set_group", admin_filter)
async def start_edit_group(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.editing_group_link)
    await callback.message.answer(
        "👥 Yangi Telegram guruh havolasini kiriting (Masalan: <code>https://t.me/zarbaliq_guruhi</code>):",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(AdminStates.editing_group_link, F.text, admin_filter)
async def save_new_group(message: Message, state: FSMContext):
    link = message.text.strip()
    await set_setting("telegram_group_link", link)
    await state.clear()
    await message.answer(
        f"✅ Telegram guruh havolasi yangilandi: <b>{link}</b>",
        reply_markup=get_main_keyboard(is_admin=True),
        parse_mode="HTML"
    )

# --- Sozlamalarni tahrirlash (Yetkazib berish narxi) ---
@router.callback_query(F.data == "adm_set_delivery", admin_filter)
async def start_edit_delivery(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.editing_delivery_price)
    await callback.message.answer(
        "🚚 Yangi yetkazib berish narxini so'mda kiriting (Masalan: <code>20000</code>):",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(AdminStates.editing_delivery_price, F.text, admin_filter)
async def save_new_delivery(message: Message, state: FSMContext):
    text = message.text.strip().replace(" ", "")
    if not text.isdigit():
        await message.answer("Iltimos, faqat raqam kiriting:")
        return

    price = int(text)
    await set_setting("delivery_price", str(price))
    await state.clear()
    await message.answer(
        f"✅ Yetkazib berish narxi yangilandi: <b>{format_price(price)}</b>",
        reply_markup=get_main_keyboard(is_admin=True),
        parse_mode="HTML"
    )

# --- Mahsulotlar bo'limi ---
@router.callback_query(F.data == "adm_products", admin_filter)
async def show_admin_products(callback: CallbackQuery, state: FSMContext):
    """Mahsulotlar boshqaruvi ro'yxati"""
    await state.clear()
    products = await get_products(only_active=False)
    text = (
        "📦 <b>Mahsulotlar boshqaruvi:</b>\n\n"
        "Tahrirlash uchun mahsulotni bosing yoki yangi qo'shing:"
    )
    await callback.message.edit_text(
        text=text,
        reply_markup=get_admin_products_keyboard(products),
        parse_mode="HTML"
    )
    await callback.answer()

# --- Mahsulotni tahrirlash menyusi ---
@router.callback_query(F.data.startswith("adm_edit_prod_"), admin_filter)
async def show_edit_single_product(callback: CallbackQuery):
    prod_id = int(callback.data.split("_")[-1])
    product = await get_product_by_id(prod_id)
    if not product:
        await callback.answer("Mahsulot topilmadi!", show_alert=True)
        return

    status_str = "🟢 Faol" if product["is_active"] else "🔴 Nofaol"
    text = (
        f"🐟 <b>Mahsulot tahrirlash:</b>\n\n"
        f"<b>Nomi:</b> {product['name']}\n"
        f"<b>Tavsifi:</b> {product['description']}\n"
        f"<b>Narxi (1 dona):</b> {format_price(product['price_unit'])}\n"
        f"<b>Holati:</b> {status_str}\n"
    )
    await callback.message.edit_text(
        text=text,
        reply_markup=get_admin_product_edit_keyboard(prod_id, product["is_active"]),
        parse_mode="HTML"
    )
    await callback.answer()

# --- Mahsulot statusini yoqish/o'chirish ---
@router.callback_query(F.data.startswith("adm_toggle_prod_"), admin_filter)
async def toggle_product_active(callback: CallbackQuery):
    prod_id = int(callback.data.split("_")[-1])
    product = await get_product_by_id(prod_id)
    if not product:
        await callback.answer("Topilmadi!")
        return

    new_status = 0 if product["is_active"] else 1
    await update_product(prod_id, is_active=new_status)
    await show_edit_single_product(callback)

# --- Mahsulot narxini o'zgartirish ---
@router.callback_query(F.data.startswith("adm_ch_price_"), admin_filter)
async def start_change_product_price(callback: CallbackQuery, state: FSMContext):
    prod_id = int(callback.data.split("_")[-1])
    await state.set_state(AdminStates.editing_product_price)
    await state.update_data(target_product_id=prod_id)

    await callback.message.answer(
        "💰 Ushbu mahsulot uchun 1 dona narxini so'mda kiriting (Masalan: <code>25000</code>):",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(AdminStates.editing_product_price, F.text, admin_filter)
async def save_product_price(message: Message, state: FSMContext):
    text = message.text.strip().replace(" ", "")
    if not text.isdigit():
        await message.answer("Iltimos, faqat raqam kiriting:")
        return

    data = await state.get_data()
    prod_id = data.get("target_product_id")
    price = int(text)

    await update_product(prod_id, price_unit=price)
    await state.clear()
    await message.answer(
        f"✅ Mahsulot narxi muvaffaqiyatli yangilandi: <b>{format_price(price)}</b>",
        reply_markup=get_main_keyboard(is_admin=True),
        parse_mode="HTML"
    )

# --- Mahsulot nomini o'zgartirish ---
@router.callback_query(F.data.startswith("adm_ch_name_"), admin_filter)
async def start_change_product_name(callback: CallbackQuery, state: FSMContext):
    prod_id = int(callback.data.split("_")[-1])
    await state.set_state(AdminStates.editing_product_name)
    await state.update_data(target_product_id=prod_id)

    await callback.message.answer(
        "📝 Mahsulot uchun yangi nom kiriting (Masalan: <code>SOMSA BALIQ (Maxsus)</code>):",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(AdminStates.editing_product_name, F.text, admin_filter)
async def save_product_name(message: Message, state: FSMContext):
    name = message.text.strip()
    data = await state.get_data()
    prod_id = data.get("target_product_id")

    await update_product(prod_id, name=name)
    await state.clear()
    await message.answer(
        f"✅ Mahsulot nomi yangilandi: <b>{name}</b>",
        reply_markup=get_main_keyboard(is_admin=True),
        parse_mode="HTML"
    )

# --- Mahsulot rasmini almashtirish ---
@router.callback_query(F.data.startswith("adm_ch_photo_"), admin_filter)
async def start_change_product_photo(callback: CallbackQuery, state: FSMContext):
    prod_id = int(callback.data.split("_")[-1])
    await state.set_state(AdminStates.editing_product_photo)
    await state.update_data(target_product_id=prod_id)

    await callback.message.answer(
        "🖼 Mahsulot uchun yangi rasm yuboring:",
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()

@router.message(AdminStates.editing_product_photo, F.photo, admin_filter)
async def save_product_photo(message: Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    data = await state.get_data()
    prod_id = data.get("target_product_id")

    await update_product(prod_id, photo_file_id=file_id)
    await state.clear()
    await message.answer(
        "✅ Mahsulot rasmi muvaffaqiyatli saqlandi!",
        reply_markup=get_main_keyboard(is_admin=True)
    )

# --- Yangi mahsulot qo'shish jarayoni ---
@router.callback_query(F.data == "adm_add_product", admin_filter)
async def start_add_product(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.adding_product_name)
    await callback.message.answer(
        "🆕 Yangi mahsulot nomini kiriting:",
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()

@router.message(AdminStates.adding_product_name, F.text, admin_filter)
async def add_product_name_step(message: Message, state: FSMContext):
    await state.update_data(new_prod_name=message.text.strip())
    await state.set_state(AdminStates.adding_product_description)
    await message.answer(
        "Tavsifini kiriting (yoki 'yo'q' deb yozing):",
        reply_markup=get_cancel_keyboard()
    )

@router.message(AdminStates.adding_product_description, F.text, admin_filter)
async def add_product_desc_step(message: Message, state: FSMContext):
    desc = message.text.strip()
    if desc.lower() == "yo'q":
        desc = ""
    await state.update_data(new_prod_desc=desc)
    await state.set_state(AdminStates.adding_product_price)
    await message.answer(
        "1 dona narxini so'mda kiriting (Masalan: <code>25000</code>):",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(AdminStates.adding_product_price, F.text, admin_filter)
async def add_product_price_step(message: Message, state: FSMContext):
    text = message.text.strip().replace(" ", "")
    if not text.isdigit():
        await message.answer("Iltimos, faqat raqam kiriting:")
        return

    await state.update_data(new_prod_price=int(text))
    await state.set_state(AdminStates.adding_product_photo)
    await message.answer(
        "Mahsulot rasmini yuboring (yoki rasmsiz qoldirish uchun 'rasmsiz' deb yozing):",
        reply_markup=get_cancel_keyboard()
    )

@router.message(AdminStates.adding_product_photo, F.photo, admin_filter)
@router.message(AdminStates.adding_product_photo, F.text, admin_filter)
async def finish_add_product(message: Message, state: FSMContext):
    photo_file_id = None
    if message.photo:
        photo_file_id = message.photo[-1].file_id

    data = await state.get_data()
    name = data.get("new_prod_name")
    desc = data.get("new_prod_desc")
    price = data.get("new_prod_price")
    category = "somsa" if "somsa" in (name or "").lower() else "baliq"
    await add_product(
        name=name,
        description=desc,
        price_unit=price,
        category=category,
        photo_file_id=photo_file_id
    )

    await state.clear()
    await message.answer(
        f"✅ Yangi mahsulot <b>{name}</b> ({format_price(price)}) muvaffaqiyatli qo'shildi!",
        reply_markup=get_main_keyboard(is_admin=True),
        parse_mode="HTML"
    )

# --- Reklama tarqatish (Broadcast) ---
@router.callback_query(F.data == "adm_broadcast", admin_filter)
async def start_broadcast(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.broadcasting_message)
    await callback.message.answer(
        "📢 <b>Reklama tarqatish</b>\n\n"
        "Barcha foydalanuvchilarga yubormoqchi bo'lgan xabaringizni yuboring "
        "(matn, rasm yoki video):\n\n"
        "<i>Bekor qilish uchun '❌ Bekor qilish' tugmasini bosing.</i>",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(AdminStates.broadcasting_message, admin_filter)
async def execute_broadcast(message: Message, state: FSMContext, bot: Bot):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Reklama tarqatish bekor qilindi.", reply_markup=get_main_keyboard(is_admin=True))
        return

    users = await get_all_users()
    total_users = len(users)

    if total_users == 0:
        await state.clear()
        await message.answer("Bazada foydalanuvchilar mavjud emas.", reply_markup=get_main_keyboard(is_admin=True))
        return

    status_msg = await message.answer(f"⏳ Reklama {total_users} ta foydalanuvchiga yuborilmoqda...")

    success_count = 0
    failed_count = 0

    for u in users:
        uid = u["id"]
        try:
            await message.copy_to(chat_id=uid)
            success_count += 1
            await asyncio.sleep(0.05) # Telegram API flood limits prevention
        except (TelegramForbiddenError, TelegramBadRequest):
            failed_count += 1
        except Exception:
            failed_count += 1

    await state.clear()
    report_text = (
        "📢 <b>Reklama tarqatish yakunlandi!</b>\n\n"
        f"✅ Yetkazildi: <b>{success_count} ta</b>\n"
        f"❌ Yetkazilmadi (bloklagan): <b>{failed_count} ta</b>\n"
        f"👥 Jami: <b>{total_users} ta</b>"
    )
    try:
        await status_msg.delete()
    except Exception:
        pass
    await message.answer(report_text, reply_markup=get_main_keyboard(is_admin=True), parse_mode="HTML")
