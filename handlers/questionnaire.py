from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from utils.states import UserForm
from datetime import datetime
from aiogram.types import CallbackQuery
from idhandlers.idclass import MyCallbackData
from datetime import datetime, timedelta
from keyboards.inline import create_warehouse_keyboard, create_coefficient_keyboard, create_date_range_keyboard, create_box_type_keyboard, main
from database.db_actions import load_warehouses_from_db,save_user_request
from database.db import async_session
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback
from aiogram.filters import StateFilter
import logging




router = Router()




@router.callback_query(MyCallbackData.filter(F.action == "change_page"))
async def change_page(callback: CallbackQuery, callback_data: MyCallbackData, state: FSMContext):
    page = int(callback_data.value)
    async with async_session() as session:
        warehouses = await load_warehouses_from_db(session)  
        keyboard = await create_warehouse_keyboard(warehouses, page=page)
        await callback.message.edit_reply_markup(reply_markup=keyboard)





@router.callback_query(MyCallbackData.filter(F.action == "start_questionnaire"))
async def start_questionnaire(callback: CallbackQuery, state: FSMContext):
    async with async_session() as session:
        warehouses = await load_warehouses_from_db(session) 
        await callback.message.answer(
            text="Пожалуйста, выберите склад:", 
            reply_markup=await create_warehouse_keyboard(warehouses, page=1)
        )
        await state.set_state(UserForm.warehouse_name)

  



@router.callback_query(MyCallbackData.filter(F.action == "select_warehouse"))
async def handle_warehouse_selection(callback: CallbackQuery, callback_data: MyCallbackData, state: FSMContext):
    await state.update_data(warehouse_id=callback_data.value)
    async with async_session() as session:
        warehouses = await load_warehouses_from_db(session)  
        selected_warehouse = next((w for w in warehouses if w['id'] == int(callback_data.value)), None)
        
        if selected_warehouse:
            await state.update_data(warehouse_name=selected_warehouse['name'])
            await callback.message.edit_text(
                text=f"Выбрано:\n\nСклад: {selected_warehouse['name']},\n----------------------------------------\nПожалуйста, выберите коэффициент",  
                reply_markup=await create_coefficient_keyboard()
            )
            await state.set_state(UserForm.coefficient)





@router.callback_query(lambda c: c.data.startswith("coefficient:"))
async def get_coefficient(callback: CallbackQuery, state: FSMContext):
    user_input = int(callback.data.split(":")[1]) 
    user_data = await state.get_data()
    await state.update_data(need_coefficient=user_input)
    await callback.message.edit_text(
        text=f"Выбрано:\n\nСклад: {user_data.get("warehouse_name")}\nКоэффициент: <{user_input}\n----------------------------------------\nВыберите диапазон дат:", 
        reply_markup=await create_date_range_keyboard()
        )



@router.callback_query(lambda c: c.data.startswith("date_range:"))
async def process_date_range(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_data = await state.get_data()
    start_date = datetime.now()

    if callback.data == "date_range:custom":
        await callback.message.edit_text(
            text="Выберите начальную дату:", 
            reply_markup=await SimpleCalendar().start_calendar()
        )
        await state.set_state(UserForm.start_date)  
    else:
        if callback.data == "date_range:tomorrow":
            end_date = start_date + timedelta(days=1)
        elif callback.data == "date_range:week":
            end_date = start_date + timedelta(weeks=1)
        elif callback.data == "date_range:two_weeks":
            end_date = start_date + timedelta(weeks=2)
        elif callback.data == "date_range:month":
            end_date = start_date + timedelta(days=30)

        await state.update_data(start_date=start_date, end_date=end_date)
        await callback.message.edit_text(
            text=f"Выбрано:\n\nСклад: {user_data.get('warehouse_name')}\nКоэффициент: <{user_data['need_coefficient']}\nДиапазон: {start_date.date()}<->{end_date.date()}\n----------------------------------------\nВведите тип приемки:", 
            reply_markup=await create_box_type_keyboard()
        )
        await state.set_state(UserForm.box_type)




@router.callback_query(SimpleCalendarCallback.filter(), StateFilter(UserForm.start_date))
async def process_start_date(callback: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    await callback.answer()
    selected_date = datetime.strptime(f"{callback_data.year}-{callback_data.month}-{callback_data.day}", "%Y-%m-%d")
    await state.update_data(start_date=selected_date)
    await callback.message.edit_text(
        text=f"Начальная дата: {selected_date.strftime('%Y-%m-%d')}\n\nПожалуйста, выберите конечную дату:", 
        reply_markup=await SimpleCalendar().start_calendar()
        )
    await state.set_state(UserForm.end_date) 




@router.callback_query(SimpleCalendarCallback.filter(), StateFilter(UserForm.end_date))
async def process_end_date(callback: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    await callback.answer()
    selected_date = datetime.strptime(f"{callback_data.year}-{callback_data.month}-{callback_data.day}", "%Y-%m-%d")
    user_data = await state.get_data()
    start_date = user_data.get("start_date")
    end_date = user_data.get("end_date")

    if start_date is None:
        await callback.answer("Не указана начальная дата.", show_alert=True)
        return

    if selected_date < start_date:
        await callback.answer("Конечная дата не может быть меньше начальной.", show_alert=True)
        return

    await state.update_data(end_date=selected_date)

    if end_date is None:
        await callback.answer("Не указана конечная дата.", show_alert=True)
        return

    await callback.message.edit_text(
        text=f"Выбрано:\n\nСклад: {user_data.get('warehouse_name')}\nКоэффициент: <{user_data['need_coefficient']}\nДиапазон: {start_date.date()}<->{selected_date.date()}\n----------------------------------------\nВведите тип приемки:", 
        reply_markup=await create_box_type_keyboard()
    )
    
    await state.set_state(UserForm.box_type)










@router.callback_query(lambda c: c.data.startswith("box_type:"))
async def handle_box_type_selection(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    box_type = callback.data.split(":")[1]  
    user_data = await state.get_data()
    
    await save_user_request(
        tg_id=callback.from_user.id,
        user_name=callback.from_user.full_name,
        need_warehouse_name=user_data['warehouse_name'],
        need_coefficient=user_data['need_coefficient'],
        start_date=user_data['start_date'],
        end_date=user_data['end_date'],
        box_type_name=box_type  
    )
    await callback.message.edit_text(
        text=f"\n----------------------------------------\nСклад: {user_data.get("warehouse_name")}\nКоэффициент: <{user_data['need_coefficient']}\nДиопазон: {user_data.get("start_date").date()}<->{user_data.get("end_date").date()}\nТип приемки: {box_type}\n----------------------------------------\nВаш запрос успешно сохранен!",
        reply_markup=await main())  
    await state.clear()  