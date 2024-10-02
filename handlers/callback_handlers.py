from aiogram import Router, types
from aiogram.types import CallbackQuery
from aiogram import F
from keyboards.inline import main
from idhandlers.idclass import MyCallbackData 
from aiogram_calendar import SimpleCalendar
from aiogram_calendar import SimpleCalendarCallback




router = Router()


@router.callback_query(MyCallbackData.filter(F.action == 'reserve_limit'))
async def handle_reserve_limit(callback: CallbackQuery, callback_data: MyCallbackData):
    await callback.message.answer("Кнопка в разработкке.", reply_markup= await main())
    
    




@router.callback_query(lambda callback: callback.data == "main_menu")
async def handle_main_menu(callback: CallbackQuery):
    await callback.message.answer("Главное меню:", reply_markup=await main())