from src.database.models import async_session, User, Hobbies, UserHobbies
from sqlalchemy import select

#

async def set_user(tg_id, name, photo_id):
  async with async_session() as session:
    user_id = await session.scalar(select(User).where(User.tg_id == tg_id))
    if not user_id:
      session.add(User(tg_id=tg_id, name=name, photo_id=photo_id))
      await session.commit()

#

async def get_data():
  async with async_session() as session:
    user_data = await session.execute(select(User.tg_id, User.name, User.photo_id, User.user_name, User.gender, User.age))
    hobbies_data = await session.execute(select(UserHobbies.user_tg_id, UserHobbies.hobbie_name))
    data = [(row[0], row[1], row[2], row[3], row[4], row[5]) for row in user_data]
    hobbies = {}
    for user_tg_id, hobbie_name in hobbies_data:
      hobbies.setdefault(user_tg_id, []).append(hobbie_name)
    for i in range(len(data)):
            user_tg_id = data[i][0]  # Извлекаем user_tg_id
            hobbies_list = hobbies.get(user_tg_id)  # Получаем список хобби
            data[i] = (*data[i], hobbies_list)
    return data

#

async def get_user_data(user_id):
  async with async_session() as session:
    user_data = await session.execute(select(User.name, User.photo_id, User.user_name, User.gender, User.age).where(User.tg_id == user_id))
    user_hobbies = await session.execute(select(UserHobbies.hobbie_name).where(UserHobbies.user_tg_id == user_id))
    data = [(row[0], row[1], row[2], row[3], row[4]) for row in user_data]
    hobbies = [row[0] for row in user_hobbies]
    data.append(hobbies)
    return data

# загрузка нового фото профиля

async def update_user_photo(user_id, photo_id):
  async with async_session() as session: # внесение изменений в бд
    result = await session.execute(select(User).where(User.tg_id == user_id))
    user = result.scalar()
    user.photo_id = photo_id
    await session.commit()

# выборка пользователей по хобби из UserHobbies

async def get_users_by_hobby(hobby):
  user_tg_ids = await check_users_by_hobby(hobby)
  async with async_session() as session:
    if user_tg_ids == None:
      return False
    else:
      user_data = await session.execute(
        select(User.tg_id, User.name, User.photo_id, User.user_name, User.gender, User.age)
        .filter(User.tg_id.in_(user_tg_ids))
        )
      data = [(row[0], row[1], row[2], row[3], row[4], row[5]) for row in user_data]
      hobbies_data = await session.execute( # Получаем хобби пользователей
        select(UserHobbies.user_tg_id, UserHobbies.hobbie_name)
        .filter(UserHobbies.user_tg_id.in_(user_tg_ids))
        )
      hobbies = {}
      for user_tg_id, hobby_name in hobbies_data:
        hobbies.setdefault(user_tg_id, []).append(hobby_name)
      for i in range(len(data)):
        user_tg_id = data[i][0]
        hobbies_list = hobbies.get(user_tg_id)
        data[i] = (*data[i], hobbies_list)
      return data
    
# Обработка интересов

async def check_hobbie(user_tg_id, hobbie):
  hobbie = hobbie.lower()
  async with async_session() as session:
    result = await session.execute(select(Hobbies).where(Hobbies.hobbie_name == hobbie))
    exist_hobbie = result.scalar_one_or_none()
    if exist_hobbie: # Проверка наличия записи в Hobbies
      hobbie_id = exist_hobbie.id
      match = await session.execute(select(UserHobbies).where(UserHobbies.user_tg_id == user_tg_id,
                                                             UserHobbies.hobbie_id == hobbie_id))
      match_result = match.scalar_one_or_none()
      if match_result: # Проверка наличия записи в UserHobbies
        return False # Если запись есть
      else:
        await add_hobbie_to_user(user_tg_id, hobbie_id, hobbie) # Добавляю новую запись в UserHobbies
      return True
    else:
      new_hobbie_id = await add_new_hobbie(hobbie) # Добавляю новую запись в Hobbies
      await add_hobbie_to_user(user_tg_id, new_hobbie_id, hobbie) # Добавляю новую запись в UserHobbies
      return True

# интересы

async def add_new_hobbie(hobbie):
  hobbie = hobbie.lower()
  async with async_session() as session:
    session.add(Hobbies(hobbie_name=hobbie))
    await session.commit()
    hobbie_id = await session.execute(select(Hobbies).where(Hobbies.hobbie_name == hobbie))
    new_added_hobbie = hobbie_id.scalar_one_or_none()
    return new_added_hobbie.id

#

async def add_hobbie_to_user(user_tg_id, new_hobbie_id, hobbie):
  async with async_session() as session:
    session.add(UserHobbies(user_tg_id=user_tg_id, hobbie_id=new_hobbie_id, hobbie_name=hobbie))
    await session.commit()

#

async def delete_hobby(tg_id, hobby):
  async with async_session() as session:
    state = select(UserHobbies).filter_by(user_tg_id=tg_id, hobbie_name=hobby)
    result = await session.execute(state)
    hobby_to_delete = result.scalar()
    if hobby_to_delete is None:
      return False
    await session.delete(hobby_to_delete)
    await session.commit()
    return True
    
# Поиск по интересам

async def check_users_by_hobby(hobby_name):
    # Получаем user_tg_id пользователей с указанным хобби
  async with async_session() as session:
    result = await session.execute(
        select(UserHobbies.user_tg_id).filter(UserHobbies.hobbie_name == hobby_name)
    )
    user_tg_ids = result.scalars().all()  # Получаем список user_tg_id
    if not user_tg_ids:
        return None  # Возвращаем None, если совпадений нет
    return user_tg_ids