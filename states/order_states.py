from aiogram.fsm.state import State, StatesGroup

class OrderStates(StatesGroup):
    selecting_quantity = State()     # Miqdorni tanlash (+ / -)
    entering_name = State()          # Ism kiritish
    entering_phone = State()         # Telefon raqam kiritish
    choosing_order_type = State()    # Yetkazib berish yoki Olib ketish
    entering_address = State()       # Manzil kiritish (faqat yetkazib berishda)
    confirming_order = State()       # Buyurtmani tasdiqlash
