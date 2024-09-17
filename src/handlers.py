import asyncio
from time import sleep
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import src.keyboard as kb

router = Router()

class Registration(StatesGroup):
  name = State()

#Запуск бота
@router.message(CommandStart())
async def start(message: Message):
  await message.answer('Привет!')
  for i in range(1):
    sleep(1)
    await message.answer('Чтобы продолжить, вам нужно', 
                         reply_markup=kb.regkey)

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
  sleep(.7)
  await message.answer(f'Приятно познакомиться, {data["name"]} и добро пожаловать!')
  sleep(2)
  await message.answer('Чтобы продолжить,')
  sleep(.5)
  await message.answer('выберите один из пунктов меню:', reply_markup=kb.main)
  await state.clear()
  
@router.message(F.text == 'Меню')
async def open_main_menu(message: Message):
  sleep(.5)
  await message.answer('Что вы хотите посмотреть?', reply_markup=kb.users)
  
@router.message(F.text == 'Test button')
async def try_again(message: Message):
  sleep(1)
  await message.answer('Неправильно, попробуй ещё...', reply_markup=kb.main)
  
"""
@router.message(Command('users'))
async def users_list(message: Message):
  await message.answer('Список пользователей:')
  

  
@router.callback_query(F.data == 'my_profile')
async def about_me(callback: CallbackQuery):
  await callback.answer('Вы выбрали...')
  await callback.message.answer('Мой профиль')
  
@router.message(Registration.name)
async def reg_name(message: Message, state: FSMContext):
  await state.update_data(name=message.name)
  data = await state.get_data()
  await message.answer(f'Ваше имя: {data["name"]}')
"""