import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.db import UserRequest, Warehouse  # Импортируйте ваши модели
from bot_instance import bot  # Импортируем экземпляр бота




async def check_user_requests(db_session: AsyncSession):
    user_requests = await db_session.execute(select(UserRequest))
    user_requests = user_requests.scalars().all()

    for user_request in user_requests:
        # Логика поиска совпадений
        warehouses = await db_session.execute(
            select(Warehouse).where(
                Warehouse.warehouse_name == user_request.need_warehouse_name,
                Warehouse.coefficient >= user_request.need_coefficient,
                Warehouse.date <= user_request.need_date
            )
        )
        warehouses = warehouses.scalars().all()

        if warehouses:
            await send_notification(user_request.tg_id, warehouses)




async def send_notification(tg_id: int, warehouses):
    warehouse_list = "\n".join([f"Склад: {w.warehouse_name}, Коэффициент: {w.coefficient}, Дата: {w.date}" for w in warehouses])
    message = f"Найдены склады:\n{warehouse_list}"
    await bot.send_message(chat_id=tg_id, text=message)




async def periodic_check(db_session: AsyncSession):
    while True:
        await check_user_requests(db_session)
        await asyncio.sleep(30)  # Ждать 5 минут (300 секунд)



def start_periodic_check(db_session: AsyncSession):
    asyncio.create_task(periodic_check(db_session))
