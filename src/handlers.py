from time import sleep
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.methods import DeleteMessage

from src.database.models import async_session, User
from sqlalchemy import select
import src.keyboard as kb

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

@router.callback_query(F.data == 'registration')
async def reg(callback: CallbackQuery, state: FSMContext):
  await callback.answer('Загружаю...')
  await state.set_state(Registration.name)
  sleep(.5)
  await callback.message.answer('Пожалуйста, ведите ваше имя:')
  
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
      await message.answer('Для продолжения, выберите один из пунктов меню.', 
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
      await message.answer('выберите один из пунктов меню:', reply_markup=kb.main)
      await state.clear()
  
@router.message(F.text == '🗄 Главное меню')
async def open_main_menu(message: Message):
  sleep(.5)
  await message.answer('Что вы хотите посмотреть?', reply_markup=kb.users)
  
@router.message(F.text == '🧪 Test button')
async def try_again(message: Message):
  sleep(1)
  await message.answer('Неправильно, попробуй ещё...', reply_markup=kb.main)