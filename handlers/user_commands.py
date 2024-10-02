from aiogram import Router,types
from aiogram.filters import CommandStart
from keyboards.inline import main

router = Router()



@router.message(CommandStart())
async def start(message: types.Message):  
    await message.answer("Добро пожаловать! ", reply_markup= await main())
  