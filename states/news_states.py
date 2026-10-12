from aiogram.fsm.state import State, StatesGroup

class SearchStates(StatesGroup):
    waiting_for_query = State()

class AdminStates(StatesGroup):
    waiting_for_broadcast = State()
