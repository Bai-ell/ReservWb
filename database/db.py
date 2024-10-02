from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Boolean
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config_reader import config




engine = create_async_engine(config.database_url.get_secret_value(), echo=True)
Base = declarative_base()



async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)



class Warehouse(Base):
    __tablename__ = 'warehouses'

    id = Column(Integer, primary_key=True)
    warehouse_id = Column(Integer, index=True)
    warehouse_name = Column(String)
    box_type_name = Column(String)
    box_type_id = Column(Integer)
    coefficient = Column(Integer)
    created_at = Column(DateTime)  
    date = Column(String)




class UserRequest(Base):
    __tablename__ = 'user_requests'

    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger) 
    user_name = Column(String)  
    need_warehouse_name = Column(String)  
    need_coefficient = Column(Integer)  
    start_date = Column(DateTime)  # Начальная дата
    end_date = Column(DateTime)    # Конечная дата
    box_type_name = Column(String)  
    notified = Column(Boolean, default=False)
