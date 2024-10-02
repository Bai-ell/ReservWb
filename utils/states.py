from aiogram.fsm.state import State, StatesGroup



class UserForm(StatesGroup):
    warehouse_name = State()
    coefficient = State()
    start_date = State()
    end_date = State()
    box_type = State()