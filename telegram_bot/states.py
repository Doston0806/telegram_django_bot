from aiogram.fsm.state import StatesGroup, State

class RegistrationState(StatesGroup):
    first_name = State()
    last_name = State()
    balance = State()

class QarzState(StatesGroup):
    choosing_direction = State()
    choosing_person = State()
    entering_amount = State()
    adding_new_person = State()

class AddExpense(StatesGroup):
    waiting_for_name = State()
    waiting_for_amount = State()
    waiting_for_date = State()
    waiting_for_balance = State()

class XarajatStates(StatesGroup):
    waiting_for_text = State()
    waiting_for_amounts = State()