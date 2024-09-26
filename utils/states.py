from aiogram.fsm.state import State, StatesGroup



class UserForm(StatesGroup):
    warehouse_name = State()
    coefficient = State()
    need_date = State()
    box_type = State()