"""
FSM (Finite State Machine) holatlari.
"""

from aiogram.fsm.state import State, StatesGroup


class HomeworkStates(StatesGroup):
    waiting_for_question = State()
    waiting_for_essay = State()
    waiting_for_irregular_search = State()
    waiting_for_api_key = State()


class AdminStates(StatesGroup):
    waiting_for_broadcast_message = State()
