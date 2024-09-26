from aiogram import Router,types
from aiogram.filters import CommandStart
from keyboards.inline import get_start_questionnaire_keyboard

router = Router()



@router.message(CommandStart())
async def start(message: types.Message):  
    await message.answer("Добро пожаловать! Нажмите кнопку ниже, чтобы заполнить запрос.", reply_markup=get_start_questionnaire_keyboard())
  