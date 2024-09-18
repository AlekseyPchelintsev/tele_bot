from time import sleep
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from contextlib import suppress
from aiogram.exceptions import TelegramBadRequest

from src.database.models import async_session, User
from sqlalchemy import select
import src.keyboard as kb
from src.database.requests import get_names

router = Router()

class Registration(StatesGroup):
  name = State()

#Запуск бота
@router.message(CommandStart())
async def start(message: Message):
  tg_id = message.from_user.id
  async with async_session() as session:
    user_id = await session.scalar(select(User).where(User.tg_id == tg_id))
    user = await session.scalar(select(User.name).where(User.tg_id == tg_id))
    if user_id:
      await message.answer(f'С возвращением, {user}!')
      sleep(.5)
      await message.answer('Выберите один из пунктов меню:', reply_markup=kb.main)
    else:
      await message.answer('Привет!')
      sleep(.5)
      await message.answer('Чтобы продолжить, вам нужно пройти регистрацию.', reply_markup=kb.regkey)

@router.message(F.text == 'Зарегистрироваться')
async def reg(message: Message, state: FSMContext):
  await state.set_state(Registration.name)
  sleep(.5)
  await message.answer('Пожалуйста, ведите ваше имя:')
  
@router.message(Registration.name)
async def reg_name(message: Message, state: FSMContext):
  await state.update_data(name=message.text)
  data = await state.get_data()
  tg_id = message.from_user.id
  async with async_session() as session:
    user_id = await session.scalar(select(User).where(User.tg_id == tg_id))
    if user_id:
      sleep(.5)
      await message.answer('Вы уже зарегистрированы.')
      sleep(.5)
      await message.answer('Для продолжения, выберите один из разделов.', 
                           reply_markup=kb.main)
      await state.clear()
    else:
      session.add(User(tg_id=tg_id, name=message.text))
      await session.commit()
      sleep(.7)
      await message.answer(f'Приятно познакомиться, {data["name"]}, и добро пожаловать!')
      sleep(2)
      await message.answer('Чтобы продолжить,')
      sleep(.5)
      await message.answer('выберите один из разделов:', reply_markup=kb.main)
      await state.clear()
  
@router.message(F.text == '🗄 Главное меню')
async def open_main_menu(message: Message):
  sleep(.5)
  await message.answer('Выберите один из разделов:', reply_markup=kb.users)
  
@router.message(F.text == '>>>hash(float("inf"))')
async def try_again(message: Message):
  sleep(1)
  await message.answer('Неправильно, попробуй ещё...', reply_markup=kb.main)

@router.message(F.text == '🚑 Помощь')
async def open_help(message: Message):
  sleep(.5)
  await message.answer('Моральная помощь, чтобы немного по чилить.')
  sleep(.5)
  await message.answer('Просто выберите что вам по душе:', reply_markup=kb.help_about)

@router.callback_query(F.data == 'back')
async def back_to_main(callback: CallbackQuery):
  await callback.answer('Загружаю...')
  await callback.message.answer('Выберить раздел:', reply_markup=kb.main)

@router.callback_query(F.data == 'my_profile')
async def about_me(callback: CallbackQuery):
  await callback.answer('Загружаю...')
  sleep(.5)
  await callback.message.answer('Данный раздел находится в стадии разработки')
  sleep(.5)
  await callback.message.answer('и будет доступен позже.')
  sleep(1)
  await callback.message.answer('Выберите один из разделов:', reply_markup=kb.users)

@router.callback_query(F.data == 'users')
async def users_list(callback: CallbackQuery):
  names = await get_names()
  sleep(.5)
  await callback.message.answer(f'{names[0]}', reply_markup=kb.paginator())

@router.callback_query(kb.Pagination.filter(F.action.in_(['prev', 'next', 'menu'])))
async def pagination_handler(callback: CallbackQuery, callback_data: kb.Pagination):
  names = await get_names()
  page_num = int(callback_data.page)
  page = page_num - 1 if page_num > 0 else 0
  
  if callback_data.action == 'next':
    page = page_num + 1 if page_num < (len(names) -1) else page_num
    
  if callback_data.action == 'menu':
    await callback.message.answer('Выберить раздел:', reply_markup=kb.main)
    
  with suppress(TelegramBadRequest):
    await callback.message.edit_text(f'{names[page]}', reply_markup=kb.paginator(page))
    
  await callback.answer()

'''
@router.callback_query(F.data == 'registration')
async def reg(callback: CallbackQuery, state: FSMContext):
  await callback.answer('Загружаю...')
  await state.set_state(Registration.name)
  sleep(.5)
  await callback.message.answer('Пожалуйста, ведите ваше имя:')
'''