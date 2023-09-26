from datetime import datetime as dt
from sqlalchemy.exc import IntegrityError
from openpyxl import Workbook

from db.models import Competitor, User
from db.engine import session


def register_user(user_data):
    '''Регистрируем пользователя.'''
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
    '''Регистрируем активность конкурента.'''
    competitor = Competitor(
        user_id=data['user_id'],
        company_name=data['company_name'],
        brand=data['brand'],
        promo_type=data['promo_type'],
        bonus=data['bonus'],
        condition=data['condition'],
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


def select_user(user_id):
    '''Получаем пользователя по id.'''
    user = session.query(User).filter(User.id == user_id).first()
    return user


def is_user_in_db(user_id):
    '''Проверяем наличие пользователя в базе данных.'''
    return session.query(
        session.query(User).filter(User.id == user_id).exists()).scalar()


def export_xls():
    wb = Workbook()
    ws = wb.active
    ws.append(
        ["Агент", "Компания", "Бренд", "Тип промо", "Бонус", "Условие", "Фото",
         "Дата создания"]
    )
    competitors = session.query(Competitor)

    for c in competitors:
        ws.append([c.user_id, c.company_name, c.brand, c.promo_type, c.bonus,
                   c.condition, c.files_id, c.created_at])
    date = dt.now().strftime("%d-%m-%y")
    wb.save(f'promo_audit{date}.xlsx')
