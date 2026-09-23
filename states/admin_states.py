from aiogram.fsm.state import State, StatesGroup

class AdminStates(StatesGroup):
    # Sozlamalarni o'zgartirish
    editing_phone = State()
    editing_group_link = State()
    editing_delivery_price = State()

    # Yangi mahsulot qo'shish
    adding_product_name = State()
    adding_product_description = State()
    adding_product_price = State()
    adding_product_photo = State()

    # Mahsulotni tahrirlash
    editing_product_select = State()
    editing_product_price = State()
    editing_product_name = State()
    editing_product_photo = State()

    # Reklama tarqatish (Broadcast)
    broadcasting_message = State()
