from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from database.db_actions import save_user_request
from utils.states import UserForm
from datetime import datetime
from aiogram.types import CallbackQuery
from idhandlers.idclass import MyCallbackData




router = Router()






@router.callback_query(MyCallbackData.filter(F.action == "start_questionnaire"))
async def start_questionnaire(callback: CallbackQuery, state: FSMContext):
    await callback.answer()  # Отправляем ответ на нажатие кнопки
    await callback.message.answer("Пожалуйста, введите имя склада.")
    await state.set_state(UserForm.warehouse_name)  # Устанавливаем состояние





@router.message(UserForm.warehouse_name)
async def get_warehouse_name(message: types.Message, state: FSMContext):
    await state.update_data(warehouse_name=message.text)
    await message.answer("Введите коэффициент:")
    await state.set_state(UserForm.coefficient)






@router.message(UserForm.coefficient)
async def get_coefficient(message: types.Message, state: FSMContext):
    await state.update_data(coefficient=message.text)
    await message.answer("Введите дату (в формате YYYY-MM-DD):")
    await state.set_state(UserForm.need_date)





@router.message(UserForm.need_date)
async def get_need_date(message: types.Message, state: FSMContext):
    await state.update_data(need_date=message.text)
    await message.answer("Введите тип коробки:")
    await state.set_state(UserForm.box_type)





@router.message(UserForm.box_type)
async def get_box_type(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    
    # Сохранение данных пользователя
    await save_user_request(
        tg_id=message.from_user.id,
        user_name=message.from_user.username,
        warehouse_name=user_data['warehouse_name'],
        coefficient=int(user_data['coefficient']),
        need_date=datetime.strptime(user_data['need_date'], '%Y-%m-%d'),
        box_type_name=message.text
    )

    await message.answer("Ваш запрос успешно сохранен.")
    await state.clear()  # Завершение анкеты
