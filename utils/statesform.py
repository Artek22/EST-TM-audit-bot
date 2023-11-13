from aiogram.fsm.state import State, StatesGroup


class FSMUserForm(StatesGroup):
    """Машина состояний для получения данных о пользователе."""
    get_name = State()
    get_surname = State()


class FSMCompetitor(StatesGroup):
    """Машина состояний для получения данных о конкуренте."""
    get_client = State()
    get_commodity_direction = State()
    get_brand = State()
    get_promo_for = State()
    get_promo_type = State()
    get_bonus = State()
    get_condition = State()
    get_photo = State()
    get_comment = State()
    confirm = State()
