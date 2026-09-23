from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from database.db import (
    get_main_product,
    get_products,
    get_products_by_category,
    get_product_by_id,
    get_setting,
    create_order,
    add_or_update_user,
    get_all_admin_ids
)
from states.order_states import OrderStates
from keyboards.default_keyboards import (
    get_main_keyboard,
    get_contact_keyboard,
    get_order_type_keyboard,
    get_location_keyboard,
    get_cancel_keyboard
)
from keyboards.inline_keyboards import (
    get_quantity_keyboard,
    get_order_confirmation_keyboard,
    get_admin_order_keyboard,
    get_product_pick_keyboard
)
from utils.helpers import format_price, clean_phone, is_valid_phone, get_current_time_str, escape_text

router = Router(name="order_handlers")

# --- Kategoriya bo'yicha taom tanlash ---
@router.callback_query(F.data == "order_cat_somsa")
async def pick_somsa_to_order(callback: CallbackQuery, state: FSMContext):
    """Foydalanuvchiga somsa turlarini tanlash imkonini berish"""
    await state.clear()
    somsalar = await get_products_by_category("somsa", only_active=True)
    if not somsalar:
        await callback.answer("Hozirda faol somsa mahsulotlari mavjud emas.", show_alert=True)
        return

    await callback.answer()
    await callback.message.answer(
        "🥟 <b>Qaysi somsaga buyurtma bermoqchisiz?</b>\n\nTanlang:",
        reply_markup=get_product_pick_keyboard(somsalar),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "order_cat_baliq")
async def pick_fish_to_order(callback: CallbackQuery, state: FSMContext):
    """Foydalanuvchiga baliq turlarini tanlash imkonini berish"""
    await state.clear()
    baliqlar = await get_products_by_category("baliq", only_active=True)
    if not baliqlar:
        await callback.answer("Hozirda faol baliq taomlari mavjud emas.", show_alert=True)
        return

    await callback.answer()
    await callback.message.answer(
        "🐟 <b>Qaysi baliq taomiga buyurtma bermoqchisiz?</b>\n\nTanlang:",
        reply_markup=get_product_pick_keyboard(baliqlar),
        parse_mode="HTML"
    )

# --- Muayyan mahsulot tanlanganda buyurtmani boshlash ---
@router.callback_query(F.data.startswith("order_prod_"))
async def start_order_for_product(callback: CallbackQuery, state: FSMContext):
    """Tanlangan mahsulot uchun miqdor tanlash oynasini ochish"""
    await state.clear()
    prod_id = int(callback.data.replace("order_prod_", ""))
    product = await get_product_by_id(prod_id)

    if not product:
        await callback.answer("Kechirasiz, mahsulot topilmadi.", show_alert=True)
        return

    await callback.answer()
    await setup_quantity_step(callback.message, state, product)

# --- Buyurtma jarayonini boshlash ---
@router.message(F.text == "🛒 Buyurtma berish")
@router.callback_query(F.data == "start_order_direct")
async def start_order_flow(event: Message | CallbackQuery, state: FSMContext):
    """Buyurtma berish jarayonini boshlash"""
    await state.clear()
    products = await get_products(only_active=True)

    if not products:
        text = "Kechirasiz, hozirda faol taomlar topilmadi. Keyinroq urinib ko'ring."
        if isinstance(event, CallbackQuery):
            await event.answer(text, show_alert=True)
        else:
            await event.answer(text)
        return

    if len(products) > 1:
        text = "🛒 <b>Qaysi taomga buyurtma bermoqchisiz?</b>\n\nQuyidagi ro'yxatdan tanlang:"
        markup = get_product_pick_keyboard(products)
        if isinstance(event, CallbackQuery):
            await event.answer()
            await event.message.answer(text, reply_markup=markup, parse_mode="HTML")
        else:
            await event.answer(text, reply_markup=markup, parse_mode="HTML")
        return

    product = products[0]
    msg = event.message if isinstance(event, CallbackQuery) else event
    if isinstance(event, CallbackQuery):
        await event.answer()
    await setup_quantity_step(msg, state, product)

async def setup_quantity_step(message: Message, state: FSMContext, product: dict):
    """Miqdor tanlash bosqichini sozlash va ko'rsatish"""
    prod_name = product["name"]
    unit_price = product["price_unit"]
    initial_qty = 1

    await state.set_state(OrderStates.selecting_quantity)
    await state.update_data(
        product_id=product["id"],
        product_name=prod_name,
        unit_price=unit_price,
        quantity=initial_qty
    )

    unit_label = "kg" if "(1 kg)" in prod_name else "dona"
    msg_text = (
        f"🛒 <b>{prod_name}</b> ga buyurtma berish\n\n"
        f"Kerakli miqdorni tanlang (kamida 1 {unit_label}):\n"
        f"• 1 {unit_label} narxi: <b>{format_price(unit_price)}</b>\n"
        f"• Hozirgi tanlov: <b>{initial_qty} {unit_label}</b>\n"
        f"• Mahsulot summasi: <b>{format_price(unit_price * initial_qty)}</b>\n\n"
        f"<i>Miqdorni o'zgartirish uchun ➕ va ➖ tugmalaridan foydalaning:</i>"
    )

    markup = get_quantity_keyboard(initial_qty, unit_price)
    await message.answer(msg_text, reply_markup=markup, parse_mode="HTML")

# --- Bekor qilish buyrug'i ---
@router.message(F.text == "❌ Bekor qilish")
@router.callback_query(F.data == "order_cancel")
async def cancel_order(event: Message | CallbackQuery, state: FSMContext):
    """Buyurtmani istalgan bosqichda bekor qilish"""
    await state.clear()
    user_id = event.from_user.id
    admins = await get_all_admin_ids()
    admin_status = user_id in admins

    text = "❌ Buyurtma bekor qilindi.\nAsosiy menyuga qaytdingiz."

    if isinstance(event, CallbackQuery):
        await event.answer("Buyurtma bekor qilindi")
        await event.message.answer(text, reply_markup=get_main_keyboard(is_admin=admin_status))
    else:
        await event.answer(text, reply_markup=get_main_keyboard(is_admin=admin_status))

# --- Miqdorni boshqarish callbacklari ---
@router.callback_query(OrderStates.selecting_quantity, F.data.startswith("qty_"))
async def handle_quantity_stepper(callback: CallbackQuery, state: FSMContext):
    """Miqdorni oshirish, kamaytirish yoki aniq qiymat belgilash"""
    data = await state.get_data()
    unit_price = data.get("unit_price", 25000)
    current_qty = data.get("quantity", 1)
    prod_name = data.get("product_name", "SOMSA BALIQ")
    unit_label = "kg" if "(1 kg)" in prod_name else "dona"

    action = callback.data

    if action == "qty_plus":
        new_qty = min(current_qty + 1, 100)
    elif action == "qty_minus":
        new_qty = max(current_qty - 1, 1)
    elif action.startswith("qty_set_"):
        new_qty = int(action.split("_")[-1])
    elif action == "qty_current":
        await callback.answer(f"Hozirda tanlangan: {current_qty} {unit_label}")
        return
    elif action == "qty_continue":
        # Keyingi bosqichga o'tish: Ism so'rash
        await state.set_state(OrderStates.entering_name)
        await callback.answer()
        await callback.message.answer(
            f"✅ Tanlangan miqdor: <b>{current_qty} {unit_label}</b> ({format_price(current_qty * unit_price)})\n\n"
            f"👤 Iltimos, <b>ismingizni</b> kiriting:",
            reply_markup=get_cancel_keyboard(),
            parse_mode="HTML"
        )
        return
    else:
        new_qty = current_qty

    if new_qty == current_qty:
        await callback.answer()
        return

    await state.update_data(quantity=new_qty)

    msg_text = (
        f"🛒 <b>{prod_name}</b> ga buyurtma berish\n\n"
        f"Kerakli miqdorni tanlang (kamida 1 {unit_label}):\n"
        f"• 1 {unit_label} narxi: <b>{format_price(unit_price)}</b>\n"
        f"• Hozirgi tanlov: <b>{new_qty} {unit_label}</b>\n"
        f"• Mahsulot summasi: <b>{format_price(unit_price * new_qty)}</b>\n\n"
        f"<i>Miqdorni o'zgartirish uchun ➕ va ➖ tugmalaridan foydalaning:</i>"
    )
    markup = get_quantity_keyboard(new_qty, unit_price)

    await callback.message.edit_text(msg_text, reply_markup=markup, parse_mode="HTML")
    await callback.answer()

# --- Ism kiritish ---
@router.message(OrderStates.entering_name, F.text)
async def process_name(message: Message, state: FSMContext):
    """Mijoz ismini saqlash va telefon so'rash"""
    name = message.text.strip()
    if len(name) < 2:
        await message.answer("Iltimos, ismingizni to'liqroq yozing:")
        return

    await state.update_data(customer_name=name)
    await state.set_state(OrderStates.entering_phone)

    await message.answer(
        "📞 Iltimos, <b>telefon raqamingizni</b> yuboring:\n\n"
        "Pastdagi <b>📱 Telefon raqamni yuborish</b> tugmasini bosing yoki "
        "<code>901234567</code> ko'rinishida yozing.",
        reply_markup=get_contact_keyboard(),
        parse_mode="HTML"
    )

# --- Telefon raqam kiritish ---
@router.message(OrderStates.entering_phone, F.contact)
@router.message(OrderStates.entering_phone, F.text)
async def process_phone(message: Message, state: FSMContext):
    """Telefon raqamni tekshirish va buyurtma turini so'rash"""
    if message.contact:
        phone = message.contact.phone_number
        if not phone.startswith("+"):
            phone = "+" + phone
    else:
        raw_phone = message.text.strip()
        cleaned = clean_phone(raw_phone)
        if not is_valid_phone(cleaned):
            await message.answer(
                "⚠️ Telefon raqam noto'g'ri kiritildi!\n"
                "Iltimos, masalan <code>+998901234567</code> yoki <code>901234567</code> shaklida yozing "
                "yoki <b>📱 Telefon raqamni yuborish</b> tugmasini bosing:",
                reply_markup=get_contact_keyboard(),
                parse_mode="HTML"
            )
            return
        phone = cleaned

    await state.update_data(customer_phone=phone)
    await state.set_state(OrderStates.choosing_order_type)

    delivery_price = int(await get_setting("delivery_price", "20000"))
    formatted_delivery = format_price(delivery_price)

    await message.answer(
        "🛵 <b>Buyurtma turini tanlang:</b>\n\n"
        f"• <b>Yetkazib berish</b> — Shahar va tumanlar bo'ylab yetkazib berish ({formatted_delivery})\n"
        f"• <b>Olib ketish</b> — Choyxonamizdan o'zingiz kelib olib ketish (Yetkazib berish bepul)\n\n"
        "Kerakli variantni tanlang:",
        reply_markup=get_order_type_keyboard(),
        parse_mode="HTML"
    )

# --- Buyurtma turini tanlash ---
@router.message(OrderStates.choosing_order_type, F.text.in_({"🚚 Yetkazib berish", "🏪 Olib ketish"}))
async def process_order_type(message: Message, state: FSMContext):
    """Buyurtma turiga qarab manzil so'rash yoki to'g'ridan-to'g'ri chek ko'rsatish"""
    choice = message.text.strip()

    if "Yetkazib" in choice:
        delivery_price = int(await get_setting("delivery_price", "20000"))
        await state.update_data(
            order_type="Yetkazib berish",
            delivery_price=delivery_price
        )
        await state.set_state(OrderStates.entering_address)

        await message.answer(
            "📍 <b>Yetkazib berish manzilini yuboring:</b>\n\n"
            "Pastdagi <b>📍 Lokatsiyani yuborish</b> tugmasini bosing yoki "
            "manzilingizni matn ko'rinishida yozing (Masalan: Toshkent, Chilonzor 9, 12-uy):",
            reply_markup=get_location_keyboard(),
            parse_mode="HTML"
        )
    else:
        # Olib ketish tanlandi
        address_text = await get_setting("address_text", "ZAR BALIQ choyxonasi")
        await state.update_data(
            order_type="Olib ketish",
            delivery_price=0,
            address=f"Choyxonadan olib ketish ({address_text})"
        )
        await show_order_summary(message, state)

# --- Manzil / Lokatsiya qabul qilish ---
@router.message(OrderStates.entering_address, F.location)
@router.message(OrderStates.entering_address, F.text)
async def process_address(message: Message, state: FSMContext):
    """Yetkazib berish manzilini saqlash"""
    lat, lon = None, None
    if message.location:
        lat = message.location.latitude
        lon = message.location.longitude
        address = f"Xarita lokatsiyasi: https://maps.google.com/?q={lat},{lon}"
    else:
        address = message.text.strip()
        if len(address) < 3:
            await message.answer("Iltimos, aniqroq manzil kiriting:")
            return

    await state.update_data(
        address=address,
        latitude=lat,
        longitude=lon
    )
    await show_order_summary(message, state)

# --- Chek va tasdiqlash sahifasi ---
async def show_order_summary(message: Message, state: FSMContext):
    """Buyurtma ma'lumotlarini umumlashtirib tasdiqlashga chiqarish"""
    data = await state.get_data()
    prod_name = data.get("product_name", "SOMSA BALIQ")
    quantity = data.get("quantity", 1)
    unit_price = data.get("unit_price", 25000)
    product_price = quantity * unit_price
    delivery_price = data.get("delivery_price", 0)
    grand_total = product_price + delivery_price

    customer_name = data.get("customer_name", "Mijoz")
    customer_phone = data.get("customer_phone", "")
    order_type = data.get("order_type", "Yetkazib berish")
    address = data.get("address", "-")
    unit_label = "kg" if "(1 kg)" in prod_name else "dona"

    await state.update_data(
        product_price=product_price,
        total_price=grand_total
    )
    await state.set_state(OrderStates.confirming_order)

    summary_text = (
        "🐟 <b>'ZAR BALIQ' buyurtmasi</b>\n\n"
        f"<b>Taom:</b> {prod_name}\n"
        f"<b>Miqdori:</b> {quantity} {unit_label}\n"
        f"<b>Taom summasi:</b> {format_price(product_price)}\n"
        f"<b>Yetkazib berish:</b> {format_price(delivery_price)}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"💰 <b>Jami to'lov: {format_price(grand_total)}</b>\n\n"
        f"👤 <b>Mijoz:</b> {escape_text(customer_name)}\n"
        f"📞 <b>Telefon:</b> {customer_phone}\n"
        f"🛵 <b>Buyurtma turi:</b> {order_type}\n"
        f"📍 <b>Manzil:</b> {escape_text(address)}\n\n"
        f"<i>Buyurtmangizni tasdiqlaysizmi?</i>"
    )

    await message.answer(
        "Buyurtma ma'lumotlari tayyorlandi:",
        reply_markup=ReplyKeyboardRemove()
    )
    await message.answer(
        text=summary_text,
        reply_markup=get_order_confirmation_keyboard(),
        parse_mode="HTML"
    )

# --- Buyurtmani tasdiqlash ---
@router.callback_query(OrderStates.confirming_order, F.data == "confirm_order_yes")
async def confirm_order(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Buyurtmani bazaga yozish va adminga yuborish"""
    data = await state.get_data()
    user_id = callback.from_user.id
    prod_name = data.get("product_name", "SOMSA BALIQ")
    quantity = data.get("quantity", 1)
    product_price = data.get("product_price", 25000)
    delivery_price = data.get("delivery_price", 0)
    total_price = data.get("total_price", product_price + delivery_price)
    customer_name = data.get("customer_name", "Mijoz")
    customer_phone = data.get("customer_phone", "")
    order_type = data.get("order_type", "Yetkazib berish")
    address = data.get("address", "-")
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    unit_label = "kg" if "(1 kg)" in prod_name else "dona"

    # 1. Bazaga yozish
    order_id = await create_order(
        user_id=user_id,
        product_name=prod_name,
        quantity=quantity,
        product_price=product_price,
        delivery_price=delivery_price,
        total_price=total_price,
        customer_name=customer_name,
        customer_phone=customer_phone,
        order_type=order_type,
        address=address,
        latitude=latitude,
        longitude=longitude
    )

    await state.clear()
    await callback.answer("Buyurtmangiz muvaffaqiyatli qabul qilindi!")

    # 2. Xaridorga rasmiy buyurtma CHEKINI chiqarib berish
    admins = await get_all_admin_ids()
    admin_status = user_id in admins
    order_time = get_current_time_str()

    unit_price = product_price // max(quantity, 1)
    delivery_line = f"• Yetkazib berish: <b>{format_price(delivery_price)}</b>\n" if delivery_price > 0 else "• Yetkazib berish: <b>Bepul (Olib ketish)</b>\n"

    customer_receipt = (
        "🧾 ━━━━━━━━━━━━━━━━━━━━\n"
        "   <b>\"ZAR BALIQ\" CHOYXONASI</b>\n"
        "         <b>XARID CHEKI</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📋 <b>Chek raqami:</b> <code>#{order_id}</code>\n"
        f"📅 <b>Sana va vaqt:</b> {order_time}\n"
        "────────────────────\n"
        f"👤 <b>Xaridor:</b> {escape_text(customer_name)}\n"
        f"📞 <b>Telefon:</b> {customer_phone}\n"
        f"🛵 <b>Xizmat turi:</b> {order_type}\n"
        f"📍 <b>Yetkazish manzili:</b>\n👉 <b>{escape_text(address)}</b>\n"
        "────────────────────\n"
        "🍴 <b>Buyurtma tarkibi:</b>\n"
        f"• {prod_name}\n"
        f"  {quantity} {unit_label} × {format_price(unit_price)} = <b>{format_price(product_price)}</b>\n"
        f"{delivery_line}"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 <b>JAMI TO‘LOV: {format_price(total_price)}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "✅ <i>Buyurtmangiz muvaffaqiyatli qabul qilindi! Operatorimiz tez orada siz bilan bog‘lanadi.</i>\n\n"
        "📞 <b>Aloqa:</b> 33-355-87-77\n"
        "📍 <b>Manzilimiz:</b> Qashqadaryo viloyati, Shahrisabz tumani, Shamaton mahallasi\n\n"
        "<i>\"ZAR BALIQ\" ni tanlaganingiz uchun rahmat! Yoqimli ishtaha! 🐟🥟</i>"
    )
    await callback.message.edit_text(customer_receipt, parse_mode="HTML")
    await callback.message.answer(
        "Asosiy menyu:",
        reply_markup=get_main_keyboard(is_admin=admin_status)
    )

    # 3. Adminga xabar va xaridor manzilini jo'natish
    admin_text = (
        f"🔔 <b>YANGI BUYURTMA! #{order_id}</b>\n\n"
        f"👤 <b>Xaridor:</b> {escape_text(customer_name)}\n"
        f"📞 <b>Telefon:</b> {customer_phone}\n"
        f"🛵 <b>Buyurtma turi:</b> {order_type}\n\n"
        f"📍 <b>XARIDOR MANZILI:</b>\n"
        f"👉 <b>{escape_text(address)}</b>\n\n"
        f"🍴 <b>Taom:</b> {prod_name}\n"
        f"🔢 <b>Miqdori:</b> {quantity} {unit_label}\n"
        f"💰 <b>Taom narxi:</b> {format_price(product_price)}\n"
        f"🚚 <b>Yetkazib berish:</b> {format_price(delivery_price)}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"💵 <b>JAMI TO‘LOV: {format_price(total_price)}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🕐 <b>Vaqti:</b> {order_time}"
    )

    admin_keyboard = get_admin_order_keyboard(order_id, customer_phone, user_id)

    for adm_id in admins:
        try:
            await bot.send_message(
                chat_id=adm_id,
                text=admin_text,
                reply_markup=admin_keyboard,
                parse_mode="HTML"
            )
            # Agar xaridor xaritadan lokatsiya yuborgan bo'lsa, xarita nuqtasini adminga ham yuboramiz
            if latitude and longitude:
                await bot.send_location(
                    chat_id=adm_id,
                    latitude=latitude,
                    longitude=longitude
                )
        except Exception:
            pass

# --- Qaytadan boshlash (o'zgartirish) ---
@router.callback_query(OrderStates.confirming_order, F.data == "order_restart")
async def restart_order(callback: CallbackQuery, state: FSMContext):
    """Buyurtma ma'lumotlarini o'zgartirish uchun mahsulot tanlashga qaytish"""
    await callback.answer("Buyurtmani boshidan tanlash")
    await start_order_flow(callback, state)
