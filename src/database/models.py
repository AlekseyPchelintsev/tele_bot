
from psycopg2 import OperationalError
import psycopg2
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy import BigInteger, String, Integer

engine = create_async_engine(
    'postgresql+asyncpg://postgres:123@localhost:5432/test_bot_tg')
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_tg_id = mapped_column(BigInteger)
    name = mapped_column(String(30))
    photo_id = mapped_column(String())
    user_name = mapped_column(String())
    gender = mapped_column(String())
    age = mapped_column(Integer)
    birth_date = mapped_column(String())


class Hobbies(Base):
    __tablename__ = 'hobbies'
    id: Mapped[int] = mapped_column(primary_key=True)
    hobbie_name = mapped_column(String())


class UserHobbies(Base):
    __tablename__ = 'userhobbies'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_tg_id = mapped_column(BigInteger)
    hobbie_id = mapped_column(Integer)
    hobbie_name = mapped_column(String())


async def asy_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def get_db_connection():
    try:
        conn = psycopg2.connect(
            user='postgres',
            password='123',
            database='test_bot_tg',
            host='localhost'
        )
        return conn
    except OperationalError as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None
