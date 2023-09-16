from aiogram.fsm.state import State, StatesGroup


class FSMUserForm(StatesGroup):
    '''
    Машина состояний для получения данных о пользователе.
    '''
    get_name = State()
    get_surname = State()


class FSMCompetitor(StatesGroup):
    '''
    Машина состояний для получения данных о конкуренте.
    '''
    get_company_name = State()
    get_brand = State()
    get_promo_type = State()
    get_bonus = State()
    get_condition = State()
    get_photo = State()
