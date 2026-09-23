import asyncio
import os
from pathlib import Path
from utils.helpers import format_price, clean_phone, is_valid_phone, get_current_time_str
from database.db import (
    init_db,
    get_main_product,
    get_products,
    get_products_by_category,
    get_setting,
    set_setting,
    create_order,
    get_order,
    update_order_status,
    get_statistics,
    add_or_update_user
)

import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

async def test_all():
    print("--- 1. Testing Helpers ---")
    assert format_price(8000) == "8 000 so‘m", f"Price format failed: {format_price(8000)}"
    assert format_price(85000) == "85 000 so‘m", f"Price format failed: {format_price(85000)}"
    assert is_valid_phone("+998333558777") is True, "Phone validation failed"
    assert is_valid_phone("333558777") is True, "Phone validation failed"
    print("[OK] Helpers test passed!")

    print("--- 2. Testing Database Initialization ---")
    await init_db()
    
    somsalar = await get_products_by_category("somsa")
    assert len(somsalar) >= 1, "Somsa ro'yxati bo'sh!"
    assert somsalar[0]["price_unit"] == 8000, f"Somsa narxi 8000 bo'lishi kerak, lekin {somsalar[0]['price_unit']}"
    print(f"[OK] Somsalar yuklandi ({len(somsalar)} xil, narxi {somsalar[0]['price_unit']} so'm): {[s['name'] for s in somsalar]}")

    baliqlar = await get_products_by_category("baliq")
    assert len(baliqlar) >= 1, "Baliq ro'yxati bo'sh!"
    assert baliqlar[0]["price_unit"] == 85000, f"Baliq narxi 85000 bo'lishi kerak, lekin {baliqlar[0]['price_unit']}"
    print(f"[OK] Baliq taomlari yuklandi ({len(baliqlar)} xil, narxi {baliqlar[0]['price_unit']} so'm): {[b['name'] for b in baliqlar]}")

    print("--- 3. Testing Settings ---")
    phone = await get_setting("phone_number")
    assert "33-355-87-77" in phone, f"Phone mismatch: {phone}"
    address = await get_setting("address_text")
    assert "Shahrisabz" in address and "Shamaton" in address, f"Address mismatch: {address}"
    print(f"[OK] Settings test passed (Phone: {phone}, Manzil: {address})")

    print("--- 4. Testing User Registration ---")
    await add_or_update_user(user_id=1234567, username="zar_fan", full_name="Ali Valiyev", phone="+998333558788")
    print("[OK] User registered successfully!")

    print("--- 5. Testing Order Creation & Receipt Calculation ---")
    dish = somsalar[0]
    qty = 5
    unit_price = dish["price_unit"]
    item_total = qty * unit_price
    delivery_price = int(await get_setting("delivery_price", "20000"))
    grand_total = item_total + delivery_price

    order_id = await create_order(
        user_id=1234567,
        product_name=dish["name"],
        quantity=qty,
        product_price=item_total,
        delivery_price=delivery_price,
        total_price=grand_total,
        customer_name="Ali Valiyev",
        customer_phone="+998333558788",
        order_type="Yetkazib berish",
        address="Shahrisabz tumani, Shamaton mahallasi, 12-uy",
        latitude=39.0558,
        longitude=66.8286
    )
    assert order_id > 0, "Order creation failed!"
    print(f"[OK] Buyurtma #{order_id} yaratildi ({dish['name']}, Jami: {grand_total} UZS, Manzil kiritildi)")

    order = await get_order(order_id)
    assert order["status"] == "pending", f"Initial status should be pending, got {order['status']}"
    assert order["address"] == "Shahrisabz tumani, Shamaton mahallasi, 12-uy"

    # Accept order
    await update_order_status(order_id, "accepted")
    order = await get_order(order_id)
    assert order["status"] == "accepted", f"Status should be accepted, got {order['status']}"
    print(f"[OK] Buyurtma #{order_id} muvaffaqiyatli qabul qilindi!")

    print("--- 6. Testing Statistics ---")
    stats = await get_statistics()
    assert stats["total_orders"] >= 1, "Order count failed"
    assert stats["accepted_orders"] >= 1, "Accepted order count failed"
    print("[OK] Statistics test passed:", stats)

    print("\n>>> BARCHA TESTLAR MUVAFFAQIYATLI O'TDI! <<<")

if __name__ == "__main__":
    asyncio.run(test_all())
