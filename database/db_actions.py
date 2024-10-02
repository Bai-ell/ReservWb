from database.db import async_session, UserRequest
from datetime import datetime
import json





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



async def load_warehouses_from_json(file_path='coefficients.json'):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Извлекаем названия складов из списка
    warehouses = []
    for warehouse in data:
        if 'warehouseName' in warehouse:
            warehouses.append({
                'id': len(warehouses) + 1,  # Добавляем ID на основе порядкового номера
                'name': warehouse['warehouseName']
            })

    return warehouses