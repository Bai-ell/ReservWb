import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import asc 
from database.db import UserRequest, Warehouses 
from bot_instance import bot 
from keyboards.inline import main


async def check_user_requests(db_session: AsyncSession):
    user_requests = await db_session.execute(select(UserRequest).where(UserRequest.notified == False))
    user_requests = user_requests.scalars().all()

    for user_request in user_requests:
        start_date = user_request.start_date.strftime('%Y-%m-%d %H:%M:%S')  
        end_date = user_request.end_date.strftime('%Y-%m-%d %H:%M:%S')  
        warehouses = await db_session.execute(
            select(Warehouses)
            .where(
                Warehouses.warehouse_name == user_request.need_warehouse_name,
                Warehouses.coefficient <= user_request.need_coefficient,
                Warehouses.coefficient >= 0, 
                Warehouses.date.between(start_date, end_date),
                Warehouses.box_type_name == user_request.box_type_name
            )
            .order_by(asc(Warehouses.date))
            .limit(1)
        )
        warehouse = warehouses.scalars().first()

        if warehouse:
            await send_notification(tg_id=user_request.tg_id, warehouse=warehouse)

            user_request.notified = True
            db_session.add(user_request)  

    await db_session.commit()


async def send_notification(tg_id: int, warehouse):
    message = (
        f"Найден склад на {warehouse.date}"
        f"\nСклад: {warehouse.warehouse_name}" 
        f"\nКоэффициент: {warehouse.coefficient}"
        f"\nТип поставки: {warehouse.box_type_name}"
    )
    await bot.send_message(chat_id=tg_id, text=message, reply_markup=await main())


async def periodic_check(db_session: AsyncSession):
    while True:
        await check_user_requests(db_session)
        await asyncio.sleep(60)  


def start_periodic_check(db_session: AsyncSession):
    asyncio.create_task(periodic_check(db_session))
