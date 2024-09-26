from database.db import async_session, UserRequest
from datetime import datetime





async def save_user_request(tg_id, user_name, warehouse_name, coefficient, need_date, box_type_name):
    async with async_session() as db_session:
        new_request = UserRequest(
            tg_id=tg_id,
            user_name=user_name,
            need_warehouse_name=warehouse_name,
            need_coefficient=coefficient,
            need_date=need_date,
            box_type_name=box_type_name
        )
        db_session.add(new_request)
        await db_session.commit()
   
