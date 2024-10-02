import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.db import UserRequest, Warehouse 
from bot_instance import bot 




async def check_user_requests(db_session: AsyncSession):
    user_requests = await db_session.execute(select(UserRequest).where(UserRequest.notified == False))
    user_requests = user_requests.scalars().all()

    for user_request in user_requests:
        
        warehouses = await db_session.execute(
            select(Warehouse).where(
                Warehouse.warehouse_name == user_request.need_warehouse_name,
                Warehouse.coefficient <= user_request.need_coefficient,
                Warehouse.date == user_request.need_date
            )
        )
        warehouses = warehouses.scalars().all()

        if warehouses:
            await send_notification(user_request.tg_id, warehouses)

            
            user_request.notified = True
            db_session.add(user_request)  

   
    await db_session.commit()





async def send_notification(tg_id: int, warehouses):
    warehouse_list = "\n".join([f"Склад: {w.warehouse_name}, Коэффициент: {w.coefficient}, Дата: {w.date}, " for w in warehouses])
    message = f"Найдены склады:\n{warehouse_list}"
    await bot.send_message(chat_id=tg_id, text=message)




async def periodic_check(db_session: AsyncSession):
    while True:
        await check_user_requests(db_session)
        await asyncio.sleep(60) 



def start_periodic_check(db_session: AsyncSession):
    asyncio.create_task(periodic_check(db_session))
