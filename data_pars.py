import asyncio
from datetime import datetime
from sqlalchemy import select
import aiohttp
from config_reader import config
from database.db import Warehouses, WarehousesNames, async_session
from notification_service import check_user_requests
import logging




# logging.disable(logging.CRITICAL)




headers = {'Authorization': f'Bearer {config.api_key.get_secret_value()}'}
coefficients_url = config.coefficent_url.get_secret_value()

async def update_coefficients_in_db():
    async with aiohttp.ClientSession() as session:
        async with session.get(coefficients_url, headers=headers) as response:
            if response.status == 200:
                coefficients_data = await response.json()

                async with async_session() as db_session:
                    for item in coefficients_data:
                        date = item.get('date')
                        warehouse_id = item['warehouseID']
                        warehouse_name = item['warehouseName']
                        box_type_id = item.get('boxTypeID')
                        box_type_name = item.get('boxTypeName', 'Unknown')
                        coefficient = item.get('coefficient', 0)

                        # Проверка уникальности названия склада
                        existing_warehouse_name = await db_session.execute(
                            select(WarehousesNames).where(WarehousesNames.warehouse_name == warehouse_name)
                        )
                        existing_warehouse_name = existing_warehouse_name.scalars().first()

                        # Если склад не найден в таблице с названиями, добавляем его
                        if not existing_warehouse_name:
                            new_warehouse_name = WarehousesNames(
                                warehouse_name=warehouse_name,
                                created_at=datetime.now()
                            )
                            db_session.add(new_warehouse_name)

                        # Проверка существования склада с тем же warehouse_id, box_type_id и датой
                        existing_warehouses = await db_session.execute(
                            select(Warehouses).where(
                                Warehouses.warehouse_id == warehouse_id,
                                Warehouses.box_type_id == box_type_id,
                                Warehouses.date == date
                            )
                        )
                        existing_warehouses = existing_warehouses.scalars().all()

                        # Если склад существует, обновляем его
                        if existing_warehouses:
                            for existing_warehouse in existing_warehouses:
                                existing_warehouse.warehouse_name = warehouse_name
                                existing_warehouse.box_type_name = box_type_name
                                existing_warehouse.coefficient = coefficient
                                existing_warehouse.date = date
                                existing_warehouse.created_at = datetime.now()
                        else:
                            # Если склада нет, создаем новую запись
                            new_warehouse = Warehouses(
                                warehouse_id=warehouse_id,
                                warehouse_name=warehouse_name,
                                box_type_name=box_type_name,
                                box_type_id=box_type_id,
                                coefficient=coefficient,
                                created_at=datetime.now(),
                                date=f'{date}'
                            )
                            db_session.add(new_warehouse)

                    await db_session.commit()

                print("Данные успешно обновлены в базе данных.")
            else:
                print(f"Ошибка: {response.status}")

async def periodic_task(interval):
    while True:
        await update_coefficients_in_db()

        async with async_session() as db_session:
            await check_user_requests(db_session)  

        await asyncio.sleep(interval)

async def pars():
    await periodic_task(60)

if __name__ == "__main__":
    asyncio.run(pars())
