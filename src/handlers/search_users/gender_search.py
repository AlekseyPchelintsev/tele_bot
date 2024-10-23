from src.handlers.search_users.all_users_search import search_all_users
from src.handlers.search_users.city_search import serach_users_by_city
from aiogram.types import CallbackQuery
from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext


router = Router()


class Registration(StatesGroup):
    search_city = State()
    search_hobby = State()


delete_messages = []
delete_last_message = []


# Выбор пола для поиска пользователей


@router.callback_query(F.data.in_(['male-search', 'female-search', 'all-search']))
async def choise_gender_for_search(callback: CallbackQuery, state: FSMContext):

    data = await state.get_data()
    search_data = data.get('type_of_search')
    gender_data = callback.data

    # изменение callback.data из-за конфликта с другой клавиатурой
    if gender_data == 'male-search':
        gender_data = 'male'
    elif gender_data == 'female-search':
        gender_data = 'female'
    elif gender_data == 'all-search':
        gender_data = 'all'

    if search_data == 'all_users':
        await search_all_users(callback, state, gender_data)
    elif search_data == 'advanced_search':
        await state.update_data(type_of_gender=gender_data)
        await serach_users_by_city(callback, state)
