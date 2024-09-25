from time import sleep
import asyncio
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.methods.get_user_profile_photos import GetUserProfilePhotos
from aiogram.filters import CommandStart
from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from contextlib import suppress
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy import select

from src.modules.loader import loader
from src.modules.delete_messages import del_messages, del_last_message
from src.database.models import async_session, User
from src.modules.check_gender import check_gender
from src.modules.hobbies_list import hobbies_list
from src.database.requests import get_data, get_user_data, check_hobbie, get_users_by_hobby, delete_hobby
from config import no_photo_id
import src.keyboard as kb

router = Router()

class Registration(StatesGroup):
  name = State()
  photo = State()
  gender = State()
  age = State()
  message = State()
  callback = State()
  hobbie = State()
  search = State()
  hobby_del = State()
  
delete_messages = []
delete_last_message = []

# Входная точка
@router.message(CommandStart())
async def start(message: Message):
  tg_id = message.from_user.id
  async with async_session() as session:
    user_id = await session.scalar(select(User).where(User.tg_id == tg_id))
    user = await session.scalar(select(User.name).where(User.tg_id == tg_id))
    if user_id:
      await message.answer(f'С возвращением, {user}!\nВыберите один из пунктов меню:', 
                           reply_markup=kb.main)
    else:
      await message.answer('Привет!\nЧтобы продолжить, вам нужно:', reply_markup=kb.regkey)

@router.callback_query(F.data == 'reg')
async def reg(callback: CallbackQuery, state: FSMContext):
  await callback.answer('Загружаю...')
  await del_last_message(callback.message)
  await state.set_state(Registration.name)
  await asyncio.sleep(.5)
  del_message = await callback.message.answer('Пожалуйста, ведите ваше имя:')
  delete_last_message.append(del_message.message_id)

# Получение данных пользователя и добавление их в бд
@router.message(Registration.name)
async def reg_name(message: Message, state: FSMContext):
  from main import bot
  await del_messages(message.chat.id, delete_last_message)
  delete_messages.append(message.message_id)
  name = message.text
  await state.update_data(name=name)
  tg_id = message.from_user.id
  get_user_photo = await bot(GetUserProfilePhotos(user_id=tg_id))
  get_user_nickname = message.from_user.username
  user_nickname = ''
  if get_user_nickname == None:
    user_nickname = 'пользователь скрыл информацию'
  else:
    user_nickname = f'@{get_user_nickname}'
  if len(get_user_photo.photos) == 0:
    async with async_session() as session:
      session.add(User(tg_id=tg_id, name=message.text, photo_id=no_photo_id, user_name=user_nickname))
      await session.commit()
  else:
    photo_id = get_user_photo.photos[0][-1].file_id
    async with async_session() as session:
      session.add(User(tg_id=tg_id, name=message.text, photo_id=photo_id, user_name=user_nickname))
      await session.commit()
  await state.clear()
  await loader(message, 'Обработка')
  # Пол
  await state.set_state(Registration.gender)
  await asyncio.sleep(.5)
  await message.answer('Укажите ваш пол.', reply_markup=kb.gender)

@router.callback_query(Registration.gender, F.data.in_(['male', 'female', 'other']))
async def gender_checked(callback: CallbackQuery, state: FSMContext):
  await callback.answer('Загружаю...')
  await del_last_message(callback.message)
  gender = callback.data
  await state.update_data(gender=gender)
  async with async_session() as session:
      tg_id = callback.from_user.id
      result = await session.execute(select(User).where(User.tg_id == tg_id))
      user = result.scalar()
      user.gender = gender
      await session.commit()
  await state.clear()
  await loader(callback.message, 'Обработка')
  await state.set_state(Registration.age)
  await asyncio.sleep(.5)
  del_message = await callback.message.answer('Укажите ваш возраст (отправив в чат).')
  delete_messages.append(del_message.message_id)
  
@router.message(Registration.age)
async def age_checked(message: Message, state: FSMContext):
  tg_id = message.from_user.id
  chat_id = message.chat.id
  delete_messages.append(message.message_id)
  while True:
    try:
      age = int(message.text)
      await state.update_data(age=age)
      async with async_session() as session:
        result = await session.execute(select(User).where(User.tg_id == tg_id))
        user = result.scalar()
        user.age = age
        await session.commit()
      break
    except ValueError:
      # Если возникла ошибка, значит, введено некорректное значение
      del_message = await message.reply("Пожалуйста, введите целое число для указания возраста.")
      delete_messages.append(del_message.message_id)
      return
  await state.clear()
  await loader(message, 'Обработка')
  response_message = await message.answer('Вы успешно зарегистрированы!')
  await asyncio.sleep(1)
  await response_message.delete()
  await del_messages(chat_id, delete_messages)
  await message.answer(f'Вы также можете рассказать о своих увлечениях людям, чтобы им было проще вас найти.', reply_markup=kb.start_edit)
      
@router.callback_query(F.data == 'main_menu')
async def open_main_menu(callback: CallbackQuery, state: FSMContext):
  await callback.answer('Загружаю...')
  await del_last_message(callback.message)
  await asyncio.sleep(.5)
  await callback.message.answer('Главное меню:', reply_markup=kb.users)
  
@router.callback_query(F.data == 'help')
async def open_help(callback: CallbackQuery):
  await callback.answer('Загружаю...')
  await del_last_message(callback.message)
  await asyncio.sleep(.5)
  await callback.message.answer('Помощь:', reply_markup=kb.help_about)

@router.callback_query(F.data == 'back')
async def back_to_main(callback: CallbackQuery):
  await callback.answer('Загружаю...')
  await del_last_message(callback.message)
  await callback.message.answer('Выберите раздел:', reply_markup=kb.main)

@router.callback_query(F.data == 'my_profile')
async def about_me(callback: CallbackQuery, state: FSMContext):
  await callback.answer('Загружаю...')
  await state.clear()
  await del_messages(callback.message.chat.id, delete_messages)
  try:
    await del_last_message(callback.message)
  except:
    pass
  user_id = callback.from_user.id
  data = await get_user_data(user_id)
  gender = await check_gender(data[0][3])
  hobbies = await hobbies_list(data[1])
  await asyncio.sleep(.5)
  await callback.message.answer_photo(photo=f'{data[0][1]}',
                              caption=f'\n<b>Имя:</b> {data[0][0]}\n<b>Возраст:</b> {data[0][4]}\n<b>Пол:</b> {gender}\n<b>Интересы:</b> {hobbies}', 
                              parse_mode='HTML', 
                              reply_markup=kb.about_me)

# Редактирование увлечений

@router.callback_query(F.data == 'edit_hobbies')
async def edit_hobbies(callback: CallbackQuery, state: FSMContext):
  await state.clear()
  await callback.answer('Загружаю...')
  await del_messages(callback.message.chat.id, delete_messages)
  await del_last_message(callback.message)
  await callback.message.answer('Выберите действие', reply_markup=kb.edit_hobbies)
  
@router.callback_query(F.data == 'new_hobbie')
async def new_hobbie(callback: CallbackQuery, state: FSMContext):
  try:
    await del_last_message(callback.message)
  except:
    pass
  del_message = await callback.message.answer('<b>Расскажите о ваших увлечениях.</b>\n\n<i>Опишите их максимально коротко.</i>\n<i>Например:</i>\n\n⛔️<code>Плохое описание:</code> "Увлекаюсь ловлей рыбы на спиннинг"\n✅<b>Хорошее описание:</b> "рыбалка"\n\n⛔️<code>Плохое описание:</code> "С детства люблю шахматы. Являюсь фанатом Фишера и Каспарова"\n✅<b>Хорошее описание:</b> "шахматы"\n\n⛔️<code>Плохое описание:</code> "люблю смотреть аниме! Особенно "Ходячий замок" и "Унесенные призраками"\n✅<b>Хорошее описание:</b> "аниме"\n\n<b>Чем короче и содержательней будет описание, тем проще вас будет найти другим пользователям!</b>', parse_mode="HTML")
  await asyncio.sleep(.2)
  del_message_second = await callback.message.answer('❗️<b>Придерживайтесь принципа:</b> "Одно увлечение - одно сообщение"', parse_mode="HTML")
  await asyncio.sleep(.2)
  del_message_third = await callback.message.answer('⤵️ Отправьте ваше увлечение сообщением в чат, чтобы я мог его добавить.', reply_markup=kb.back_hobbies)
  delete_messages.clear()
  delete_last_message.clear()
  delete_messages.extend([del_message.message_id, del_message_second.message_id])
  delete_last_message.append(del_message_third.message_id)
  await state.update_data(message=del_message_third)
  await state.set_state(Registration.hobbie)

@router.message(Registration.hobbie)
async def add_hobbie(message: Message, state: FSMContext):
  await del_messages(message.chat.id, delete_last_message)
  await asyncio.sleep(.2)
  await loader(message, 'Обработка')
  hobbie = message.text
  user_id = message.from_user.id
  await state.update_data(hobbie=hobbie)
  checked = await check_hobbie(user_id, hobbie)
  if not checked:
    await asyncio.sleep(.2)
    await loader(message, '❌ Такое увлечение уже находится в вашем списке')
    await asyncio.sleep(.2)
    response_message = await message.answer('⤵️ Отправьте ваше увлечение сообщением в чат, чтобы я мог его добавить.', reply_markup=kb.back)
    delete_last_message.append(response_message.message_id)
  else:
    await asyncio.sleep(.2)
    await loader(message, '✅ Ваш список увлечений успешно обновлен!')
    await asyncio.sleep(.2)
    response_message_third = await message.answer('⤵️ Отправьте ваше увлечение сообщением в чат, чтобы я мог его добавить.', reply_markup=kb.back)
    delete_last_message.append(response_message_third.message_id)
  await state.set_state(Registration.hobbie)

  
  

@router.callback_query(F.data == 'del_hobbie')
async def del_hobby(callback: CallbackQuery, state: FSMContext):
  try:
    await del_last_message(callback.message)
  except:
    pass
  user_id = callback.from_user.id
  data = await get_user_data(user_id)
  hobbies = await hobbies_list(data[1])
  if hobbies != '-':
    response_message = await callback.message.answer(f'<b>Список ваших увлечений:</b> \n\n{hobbies}\n\nЧтобы удалить увлечение, просто пришлите мне его в чат.', 
                                parse_mode='HTML', 
                                reply_markup=kb.back)
    await state.update_data(response_message_id=response_message.message_id)
    await state.set_state(Registration.hobby_del)
  else:
    response_message = await callback.message.answer(f'<b>Список ваших увлечений пуст.</b>', 
                                parse_mode='HTML', 
                                reply_markup=kb.add_hobby)
  delete_messages.append(response_message.message_id)
    
@router.message(Registration.hobby_del)
async def del_hobby_from_db(message: Message, state: FSMContext):
  from main import bot
  user_id = message.from_user.id
  hobby = message.text
  hobby = hobby.lower()
  is_hobby = await delete_hobby(user_id, hobby)
  if is_hobby:
    await loader(message, 'Удаляю')
    response_message = await message.answer('Увлечение успешно удалено!')
    await asyncio.sleep(1)
    await response_message.delete()
    message_from_state = await state.get_data()
    response_message_id = message_from_state.get('response_message_id')
    data = await get_user_data(user_id)
    hobbies = await hobbies_list(data[1])
    if hobbies != '-':
      await message.bot.edit_message_text(
                chat_id=user_id,
                message_id=response_message_id,
                text=f'<b>Список ваших увлечений:</b> \n\n{hobbies}\n\nЧтобы удалить увлечение, просто пришлите мне его в чат.',
                parse_mode='HTML',
                reply_markup=kb.back
            )
    else:
      response_message = await message.answer(f'<b>Список ваших увлечений пуст.</b>', 
                                parse_mode='HTML', 
                                reply_markup=kb.add_hobby)
      await message.bot.delete_message(chat_id=user_id, message_id=response_message_id)
  else:
    await loader(message, 'Такого хобби нет в вашем списке')

# Редактирование фото профиля

@router.callback_query(F.data == 'edit_photo')
async def edit_photo_menu(callback: CallbackQuery):
  await callback.answer('Загружаю...')
  await del_last_message(callback.message)
  await callback.message.answer('Выберите действие:', reply_markup=kb.edit_photo)

@router.callback_query(F.data == 'new_photo')
async def edit_photo(callback: CallbackQuery, state: FSMContext):
  await callback.answer('Загружаю...')
  await del_last_message(callback.message)
  sent_message = await callback.message.answer('Отправьте в чат фото, которое хотите загрузить.', reply_markup=kb.back_to_photo)
  await state.update_data(message=sent_message)
  await state.set_state(Registration.photo)

@router.message(Registration.photo, F.photo)
async def get_new_photo(message: Message, state: FSMContext):
  photo_id = message.photo[-1].file_id
  await state.update_data(photo=photo_id)
  data = await state.get_data() # данные предыдущего callback`a
  sent_message = data.get('message') # данные последнего сообщения из предыдущего callback`a
  await sent_message.delete() # удаление последнего сообщения из предыдущего callback`a
  async with async_session() as session: # внесение изменений в бд
    tg_id = message.from_user.id
    result = await session.execute(select(User).where(User.tg_id == tg_id))
    user = result.scalar()
    user.photo_id = photo_id
    await session.commit()
  await state.clear()
  await asyncio.sleep(.3)
  await loader(message, 'Фото загружается')
  await asyncio.sleep(.3)
  await message.answer('Фото профиля успешно обновлено!', reply_markup=kb.back)

@router.callback_query(F.data == 'del_photo')
async def delete_photo(callback: CallbackQuery, state: FSMContext):
  await callback.answer('Загружаю...')
  await del_last_message(callback.message)
  await state.clear()
  tg_id = callback.from_user.id
  async with async_session() as session: # внесение изменений в бд
    result = await session.execute(select(User).where(User.tg_id == tg_id))
    user = result.scalar()
    user.photo_id = no_photo_id
    await session.commit()
  await state.clear()
  await loader(callback.message, 'Удаляю')
  await asyncio.sleep(.3)
  await callback.message.answer('Фото успешно удалено.', reply_markup=kb.back)


# Список пользователей

@router.callback_query(F.data == 'users')
async def check_users_menu(callback: CallbackQuery, state: FSMContext):
  await state.clear()
  await callback.answer('Загружаю...')
  await del_last_message(callback.message)
  await callback.message.answer('Выберите действие:', reply_markup=kb.users_menu)

# Фильтр пользователей по хобби

@router.callback_query(F.data == 'search_users')
async def search_users_menu(callback: CallbackQuery, state: FSMContext):
  await callback.answer('Загружаю...')
  await del_last_message(callback.message)
  sent_message = await callback.message.answer('Пришлите в чат увлечение, по которому вы хотите найти пользователей:', reply_markup=kb.search_users)
  delete_messages.append(sent_message.message_id)
  await state.set_state(Registration.search)
  
@router.message(Registration.search)
async def search_users(message: Message, state: FSMContext):
  request = message.text
  request = request.lower()
  await state.update_data(search=request)
  data = await get_users_by_hobby(request)
  if data == False:
    await loader(message, 'Обработка')
    await loader(message, '❌ Пользователи с таким увлечением отсутствуют')
    await asyncio.sleep(.5)
  else:
    await state.clear()
    await loader(message, 'Загружаю')
    try:
      await del_messages(message.chat.id, delete_messages)
    except:
      pass
    gender = await check_gender(data[0][4])
    hobbies = await hobbies_list(data[0][6])
    sleep(.5)
    await message.answer_photo(photo=f'{data[0][2]}', 
                                        caption=f'<b>Имя:</b> {data[0][1]}\n<b>Возраст:</b> {data[0][5]}\n<b>Пол:</b> {gender}\n<b>Интересы:</b> {hobbies}',
                                        parse_mode='HTML',
                                        reply_markup=kb.paginator(list_type='hobbies_users'))
    await state.update_data(users_data=data)

@router.callback_query(F.data == 'all_users')
async def users_list(callback: CallbackQuery, state: FSMContext):
  data = await get_data()
  gender = await check_gender(data[0][4])
  hobbies = await hobbies_list(data[0][6])
  sleep(.5)
  await del_last_message(callback.message)
  await callback.message.answer_photo(photo=f'{data[0][2]}', 
                                      caption=f'<b>Имя:</b> {data[0][1]}\n<b>Возраст:</b> {data[0][5]}\n<b>Пол:</b> {gender}\n<b>Интересы:</b> {hobbies}',
                                      parse_mode='HTML',
                                      reply_markup=kb.paginator(list_type='all_users'))
  await state.update_data(users_data=data)
  
# Пагинация списка пользователей

@router.callback_query(kb.Pagination.filter(F.action.in_(['prev', 'next', 'menu', 'user_profile'])))
async def pagination_handler(callback: CallbackQuery, callback_data: kb.Pagination, state: FSMContext):
    from main import bot
    list_type = callback_data.list_type
    data = (await state.get_data()).get('users_data')
    page_num = int(callback_data.page)
    chat_id = callback.message.chat.id
    if callback_data.action == 'prev':
        page = max(page_num - 1, 0)
    elif callback_data.action == 'next':
        page = min(page_num + 1, len(data) - 1)
    else:
        page = page_num

    if callback_data.action == 'menu':
      await del_last_message(callback.message)
      await bot.send_message(chat_id=chat_id, text='Выберите раздел:', reply_markup=kb.users)
    elif callback_data.action == 'user_profile':
      await open_profile(callback)
    else:
      with suppress(TelegramBadRequest):
        gender = await check_gender(data[page][4])
        hobbies = await hobbies_list(data[page][6])
        await callback.message.edit_media(media=InputMediaPhoto(media=f'{data[page][2]}', 
                                                                caption=f'<b>Имя:</b> {data[page][1]}\n<b>Возраст:</b> {data[page][5]}\n<b>Пол:</b> {gender}\n<b>Интересы:</b> {hobbies}',
                                                                parse_mode= 'HTML'),
                                          reply_markup=kb.paginator(page, list_type))

    await callback.answer()

@router.callback_query(F.data == 'user_profile')
async def open_profile(callback: CallbackQuery):
  await del_last_message(callback.message)
  await loader(callback.message, '🚧 Ведутся работы')
  await users_list(callback)
  
# devtools

# Вытягивает id фото
'''
@router.message(F.photo)
async def photo_nahui(message: Message):
  photo_data = message.photo[-1]
  await message.answer(f'id Этого изображения:\n{photo_data.file_id}')
'''
# Тест функций

@router.message(F.text == '/test')
async def test(message: Message):
  check = await get_users_by_hobby('акулы')
  await message.answer(f'{check}')