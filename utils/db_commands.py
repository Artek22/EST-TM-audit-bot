from datetime import datetime as dt
from sqlalchemy.exc import IntegrityError

from db.models import Competitor, User
from db.engine import session


def register_user(user_data):
    user = User(
        id=user_data['id'],
        name=user_data['name'],
        surname=user_data['surname'],
    )
    session.add(user)
    try:
        session.commit()
        return True
    except IntegrityError:
        session.rollback()  # откатываем session.add(user)
        return False


def register_competitor(data):
    competitor = Competitor(
        user_id=data['user_id'],
        company_name=data['company_name'],
        brand=data['brand'],
        promo_type=data['promo_type'],
        bonus=data['bonus'],
        condition=data['fixed_payout'],
        files_id=data['files_id'],
        created_at=dt.now(),
    )
    session.add(competitor)
    try:
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        return False


def select_user(user_id) -> User:
    '''Получаем пользователя по id.'''
    user = session.query(User).filter(User.id == user_id).first()
    return user
