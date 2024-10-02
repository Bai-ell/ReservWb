from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from utils.states import UserForm
from datetime import datetime
from aiogram.types import CallbackQuery
from idhandlers.idclass import MyCallbackData
from datetime import datetime, timedelta
from keyboards.inline import create_warehouse_keyboard, create_coefficient_keyboard, create_date_range_keyboard, create_box_type_keyboard
from database.db_actions import load_warehouses_from_json,save_user_request
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback
from aiogram.filters import StateFilter




router = Router()




@router.callback_query(MyCallbackData.filter(F.action == "change_page"))
async def change_page(callback: CallbackQuery, callback_data: MyCallbackData):
    page = int(callback_data.value)  
    warehouses = await load_warehouses_from_json() 
    keyboard = await create_warehouse_keyboard(warehouses, page=page)
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()  




@router.callback_query(MyCallbackData.filter(F.action == "start_questionnaire"))
async def start_questionnaire(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    warehouses = await load_warehouses_from_json() 
    await callback.message.answer("Пожалуйста, выберите склад:", reply_markup=await create_warehouse_keyboard(warehouses, page=1))
    await state.set_state(UserForm.warehouse_name)




@router.callback_query(MyCallbackData.filter(F.action == "select_warehouse"))
async def handle_warehouse_selection(callback: CallbackQuery, callback_data: MyCallbackData, state: FSMContext): 
    await state.update_data(warehouse_id=callback_data.value)
    await callback.message.edit_reply_markup(reply_markup=None)
    warehouses = await load_warehouses_from_json()
    selected_warehouse = next((w for w in warehouses if w['id'] == int(callback_data.value)), None)
    
    if selected_warehouse:
        await state.update_data(warehouse_name=selected_warehouse['name'])
        await callback.answer(f"Вы выбрали: {selected_warehouse['name']}")
        
        # Отправляем инлайн-клавиатуру для выбора коэффициента
        coefficient_keyboard = await create_coefficient_keyboard()
        await callback.message.answer("Пожалуйста, выберите коэффициент:", reply_markup=coefficient_keyboard)
        await state.set_state(UserForm.coefficient)


@router.callback_query(lambda c: c.data.startswith("coefficient:"))
async def get_coefficient(callback: CallbackQuery, state: FSMContext):
    print(callback.data)
    
    # Извлекаем коэффициент из callback данных и преобразуем в целое число
    user_input = int(callback.data.split(":")[1])  # Преобразуем в целое число

    valid_coefficients = [0, 1, 2, 3, 4, 5, 6]

    # Проверяем, является ли коэффициент допустимым
    if user_input in valid_coefficients:
        await state.update_data(need_coefficient=user_input)

        # Показываем клавиатуру с выбором диапазона дат
        await callback.message.answer("Выберите диапазон дат:", reply_markup=await create_date_range_keyboard())
        
        # Удаляем клавиатуру с коэффициентами
        await callback.message.edit_reply_markup(reply_markup=None)
    else:
        await callback.answer("Пожалуйста, выберите корректный коэффициент из предложенных вариантов.", show_alert=True)




@router.callback_query(lambda c: c.data.startswith("date_range:"))
async def process_date_range(callback: CallbackQuery, state: FSMContext):
    await callback.answer()  # Убираем индикатор загрузки
    start_date = datetime.now()

    # Проверяем, если была выбрана опция для самостоятельного выбора диапазона
    if callback.data == "date_range:custom":
        # Отправляем календарь для выбора начальной даты
        await callback.message.answer("Выберите начальную дату:", reply_markup=await SimpleCalendar().start_calendar())
        await state.set_state(UserForm.start_date)  # Устанавливаем состояние для выбора начальной даты
    else:
        # Стандартные диапазоны
        if callback.data == "date_range:tomorrow":
            end_date = start_date + timedelta(days=1)
        elif callback.data == "date_range:week":
            end_date = start_date + timedelta(weeks=1)
        elif callback.data == "date_range:two_weeks":
            end_date = start_date + timedelta(weeks=2)
        elif callback.data == "date_range:month":
            end_date = start_date + timedelta(days=30)

        # Сохраняем даты в состоянии
        await state.update_data(start_date=start_date, end_date=end_date)

        await callback.message.answer(
            f"Вы установили диапазон дат:\nНачальная дата: {start_date.strftime('%Y-%m-%d')}\nКонечная дата: {end_date.strftime('%Y-%m-%d')}")
        
        # Запрашиваем тип коробки
        await callback.message.answer("Введите тип коробки:", reply_markup=await create_box_type_keyboard())
        await state.set_state(UserForm.box_type)






@router.callback_query(lambda c: c.data == "date_range:manual")
async def start_manual_date_selection(callback: CallbackQuery, state: FSMContext):
    # Отправляем первый календарь для выбора начальной даты
    await callback.message.answer("Пожалуйста, выберите начальную дату:", 
                                  reply_markup=await SimpleCalendar().start_calendar())
    await state.set_state(UserForm.start_date)  # Устанавливаем состояние для начала выбора даты




@router.callback_query(SimpleCalendarCallback.filter(), StateFilter(UserForm.start_date))
async def process_start_date(callback: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    await callback.answer()  # Убираем индикатор загрузки

    # Доступ к данным через атрибуты callback_data
    selected_date = datetime.strptime(f"{callback_data.year}-{callback_data.month}-{callback_data.day}", "%Y-%m-%d")

    # Сохраняем выбранную дату в состоянии
    await state.update_data(start_date=selected_date)

    # Отправляем подтверждение пользователю
    await callback.message.answer(f"Вы выбрали дату: {selected_date.strftime('%Y-%m-%d')}")
    
    # Запрашиваем конечную дату
    await callback.message.answer("Пожалуйста, выберите конечную дату:", reply_markup=await SimpleCalendar().start_calendar())
    
    # Удаляем клавиатуру с начальной датой
    await callback.message.edit_reply_markup(reply_markup=None)
    
    await state.set_state(UserForm.end_date) 


@router.callback_query(SimpleCalendarCallback.filter(), StateFilter(UserForm.end_date))
async def process_end_date(callback: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    await callback.answer()  # Убираем индикатор загрузки
    selected_date = datetime.strptime(f"{callback_data.year}-{callback_data.month}-{callback_data.day}", "%Y-%m-%d")
    
    # Получаем начальную дату из состояния
    user_data = await state.get_data()
    start_date = user_data.get("start_date")
    
    # Проверяем, что конечная дата не меньше начальной
    if selected_date < start_date:
        await callback.answer("Конечная дата не может быть меньше начальной.", show_alert=True)
        return

    # Сохраняем конечную дату
    await state.update_data(end_date=selected_date)

    # Подтверждаем выбор диапазона
    await callback.message.answer(f"Вы выбрали диапазон дат:\nНачальная дата: {start_date.strftime('%Y-%m-%d')}\nКонечная дата: {selected_date.strftime('%Y-%m-%d')}")

    # Запрашиваем тип коробки
    await callback.message.answer("Введите тип коробки:", reply_markup=await create_box_type_keyboard())
    await state.set_state(UserForm.box_type)


@router.callback_query(lambda c: c.data.startswith("box_type:"))
async def handle_box_type_selection(callback: CallbackQuery, state: FSMContext):
    box_type = callback.data.split(":")[1]  # Получаем выбранный тип коробки

    # Сохраняем данные пользователя
    user_data = await state.get_data()
    print(user_data)
    await save_user_request(
        tg_id=callback.from_user.id,
        user_name=callback.from_user.username,
        need_warehouse_name=user_data['warehouse_name'],
        need_coefficient=user_data['need_coefficient'],
        start_date=user_data['start_date'],
        end_date=user_data['end_date'],
        box_type_name=box_type  # Сохраняем выбранный тип коробки
    )

    await callback.answer("Ваш запрос успешно сохранен.")
    await callback.message.answer("Ваш запрос успешно сохранен.")  # Сообщение пользователю
    await state.clear()  # Завершение анкеты