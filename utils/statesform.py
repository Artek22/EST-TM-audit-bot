from aiogram.fsm.state import State, StatesGroup


class UserForm(StatesGroup):
    '''
    Машина состояний для получения данных о пользователе.
    '''
    GET_NAME = State()
    GET_SURNAME = State()


class Competitor(StatesGroup):
    '''
    Машина состояний для получения данных о конкуренте.
    '''
    GET_NAME = State()
    GET_BRAND = State()
    GET_PROMO = State()
    GET_BOMUS = State()
    GET_FIXED_PAYOUT = State()
