from aiogram.fsm.state import StatesGroup, State

class TakeLoanForm(StatesGroup):
    term = State()
    amount = State()