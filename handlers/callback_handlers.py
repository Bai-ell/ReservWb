from aiogram import Router, types
from aiogram.types import CallbackQuery
from aiogram import F
from keyboards.inline import main
from idhandlers.idclass import MyCallbackData 
from aiogram_calendar import SimpleCalendar
from aiogram_calendar import SimpleCalendarCallback




router = Router()



@router.callback_query(MyCallbackData.filter(F.action.in_({'serach_limit', 'limit_search'})))
async def handle_callback_query(query: CallbackQuery, callback_data: MyCallbackData):
    await query.message.answer(text='Выберите склад:', reply_markup=await main())
    




@router.callback_query(SimpleCalendarCallback.filter())
async def process_simple_calendar(callback_query: types.CallbackQuery, callback_data: dict):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if selected:
        await callback_query.message.answer(f'Вы выбрали {date.strftime("%d.%m.%Y")}')