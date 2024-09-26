from config_reader import config
import asyncio
from datetime import datetime
from database.db import async_session, Warehouse
import aiohttp








headers = {'Authorization': f'Bearer {config.api_key.get_secret_value()}'}
coefficients_url = config.coefficent_url.get_secret_value()








async def save_coefficients_to_db():
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
                print("Данные успешно сохранены в базе данных.")
            else:
                print(f"Ошибка: {response.status}")

async def main():
    await save_coefficients_to_db()

if __name__ == "__main__":
    asyncio.run(main())