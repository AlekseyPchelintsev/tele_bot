from src.database.models import async_session, User
from sqlalchemy import select

async def set_user(tg_id, name):
  async with async_session() as session:
    user_id = await session.scalar(select(User).where(User.tg_id == tg_id))
    if not user_id:
      session.add(User(tg_id=tg_id, name=name))
      await session.commit()

async def get_names():
  async with async_session() as session:
    async with session.begin():
      result = await session.execute(select(User.name))
      names = [row for row in result.scalars()]
      return names