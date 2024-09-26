from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from idhandlers.idclass import MyCallbackData 

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup




async def main():
    builder_contacts = InlineKeyboardBuilder()
    builder_contacts.button(
        text='Поиск лимитов',  
        callback_data=MyCallbackData(action='serach_limit', value=1).pack()
    )
    return builder_contacts.as_markup()






def get_start_questionnaire_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    # Добавление кнопки
    builder.button(
        text='Заполнить запрос',
        callback_data=MyCallbackData(action='start_questionnaire', value=1).pack()
    )
    
    # Генерация клавиатуры
    return builder.as_markup()