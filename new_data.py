import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import aiohttp
from config_reader import config
from database.db import async_session, Warehouse, UserRequest
from notification_service import send_notification, check_user_requests  # Импортируйте функции из notification_service






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

                        existing_warehouses = await db_session.execute(
                            select(Warehouse).where(
                                Warehouse.warehouse_id == warehouse_id,
                                Warehouse.box_type_id == box_type_id,
                                Warehouse.date == date
                            )
                        )
                        existing_warehouses = existing_warehouses.scalars().all()

                        if existing_warehouses:
                            for existing_warehouse in existing_warehouses:
                                existing_warehouse.warehouse_name = warehouse_name
                                existing_warehouse.box_type_name = box_type_name
                                existing_warehouse.coefficient = coefficient
                                existing_warehouse.date = date
                                existing_warehouse.created_at = datetime.now()
                        else:
                            new_warehouse = Warehouse(
                                warehouse_id=warehouse_id,
                                warehouse_name=warehouse_name,
                                box_type_name=box_type_name,
                                box_type_id=box_type_id,
                                coefficient=coefficient,
                                created_at=datetime.now(),
                                date=date
                            )
                            db_session.add(new_warehouse)

                    await db_session.commit()

                print("Данные успешно обновлены в базе данных.")
            else:
                print(f"Ошибка: {response.status}")

async def periodic_task(interval):
    while True:
        # Сначала обновляем базу данных
        await update_coefficients_in_db()

        async with async_session() as db_session:
            # Затем проверяем запросы пользователей
            await check_user_requests(db_session)  # Передаем db_session

        # Повторяем задачу через указанный интервал
        await asyncio.sleep(interval)

async def main():
    await periodic_task(30)  # Запускаем задачу с интервалом 30 секунд

if __name__ == "__main__":
    asyncio.run(main())
