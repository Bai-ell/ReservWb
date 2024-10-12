from database.db import async_session, UserRequest, WarehousesNames 
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select




async def save_user_request(tg_id, user_name, need_warehouse_name, need_coefficient, start_date, end_date, box_type_name):
    async with async_session() as session:
        new_request = UserRequest(
            tg_id=tg_id,
            user_name=user_name,
            need_warehouse_name=need_warehouse_name,
            need_coefficient=need_coefficient,
            start_date=start_date,
            end_date=end_date,
            box_type_name=box_type_name
        )
        session.add(new_request)
        await session.commit()



async def load_warehouses_from_db(db_session: AsyncSession):
    async with db_session.begin():  
        result = await db_session.execute(select(WarehousesNames))
        warehouses = result.scalars().all()  
    return [{'id': warehouse.id, 'name': warehouse.warehouse_name} for warehouse in warehouses]