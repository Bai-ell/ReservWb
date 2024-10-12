from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from idhandlers.idclass import MyCallbackData 

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup




async def main():
    builder_main = InlineKeyboardBuilder()
    builder_main.button(
        text='Поиск лимитов',  
        callback_data=MyCallbackData(action='start_questionnaire', value=1).pack()
    )
    builder_main.button(
        text='Бронировать лимиты',  
        callback_data=MyCallbackData(action='reserve_limit', value=2).pack()
    )

    return builder_main.as_markup()




ITEMS_PER_PAGE = 16 
ROWS = 8
BUTTONS_PER_ROW = 2  


async def create_warehouse_keyboard(warehouses, page=1):
    builder = InlineKeyboardBuilder()  

    if isinstance(warehouses, list) and all(isinstance(w, dict) for w in warehouses):
        total_items = len(warehouses)
        total_pages = (total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE  

       
        start_index = (page - 1) * ITEMS_PER_PAGE
        end_index = min(start_index + ITEMS_PER_PAGE, total_items)

        row = []  
        for warehouse in warehouses[start_index:end_index]:
          
            callback_data = MyCallbackData(action="select_warehouse", value=warehouse['id']).pack()
            button = InlineKeyboardButton(text=warehouse['name'], callback_data=callback_data)
            row.append(button)

           
            if len(row) == BUTTONS_PER_ROW:
                builder.row(*row)
                row = []  

        if row:
            builder.row(*row)

        navigation_buttons = []
        if page > 1:
            callback_data = MyCallbackData(action="change_page", value=page - 1).pack()
            navigation_buttons.append(InlineKeyboardButton(text="⏮️", callback_data=callback_data))
        if page < total_pages:
            callback_data = MyCallbackData(action="change_page", value=page + 1).pack()
            navigation_buttons.append(InlineKeyboardButton(text="⏩", callback_data=callback_data))

        if navigation_buttons:
            builder.row(*navigation_buttons)

        builder.row(InlineKeyboardButton(text="Главное меню", callback_data="main_menu"))

    return builder.as_markup()



async def create_coefficient_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="Бесплатно", callback_data=f"coefficient:{0}"),
    )
    builder.row(
        InlineKeyboardButton(text="<=1x", callback_data=f"coefficient:{1}"),
        InlineKeyboardButton(text="<=2x", callback_data=f"coefficient:{2}"),
    )
    builder.row(
        InlineKeyboardButton(text="<=3x", callback_data=f"coefficient:{3}"),
        InlineKeyboardButton(text="<=4x", callback_data=f"coefficient:{4}"),
    )
    builder.row(
        InlineKeyboardButton(text="<=5x", callback_data=f"coefficient:{5}"),
        InlineKeyboardButton(text="<=6x", callback_data=f"coefficient:{6}"),
    )
    
    return builder.as_markup()







async def create_date_range_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="На завтра", callback_data="date_range:tomorrow"),
        InlineKeyboardButton(text="На неделю", callback_data="date_range:week")
    )
    builder.row(
        InlineKeyboardButton(text="На 2 недели", callback_data="date_range:two_weeks"),
        InlineKeyboardButton(text="На месяц", callback_data="date_range:month")
    )
    builder.row(
        InlineKeyboardButton(text="Выбрать диапазон", callback_data="date_range:custom")
    )
    
    return builder.as_markup()









async def create_box_type_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="Суперсейф", callback_data="box_type:Суперсейф"),
        InlineKeyboardButton(text="Короба", callback_data="box_type:Короба"),
    )
    builder.row(
        InlineKeyboardButton(text="Монопаллеты", callback_data="box_type:Монопаллеты"),
        InlineKeyboardButton(text="QR-поставка с коробами", callback_data="box_type:QR-поставка с коробами"),
    )

    return builder.as_markup()