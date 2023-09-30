import yadisk

from datetime import datetime as dt
from sqlalchemy.exc import IntegrityError
from openpyxl import Workbook

from config_data.config import load_config
from db.models import Competitor, User
from db.engine import session


config = load_config()


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
        ["Агент", "Компания", "Бренд", "Тип промо", "Бонус", "Условие",
         "Дата создания"]
    )
    competitors = session.query(Competitor)

    for c in competitors:
        ws.append([c.user_id, c.company_name, c.brand, c.promo_type, c.bonus,
                   c.condition, c.created_at])
    date = dt.now().strftime("%d-%m-%y")
    wb.save(f'promo_audit{date}.xlsx')


async def ya_disk_upload(callback):
    y = yadisk.YaDisk(token=config.yandex_id)
    competitors = session.query(Competitor)
    # Достаем дату последнего загруженного файла
    with open('x_date.txt', 'r') as f:
        x_date = f.read()
        f.close()

    for c in competitors:
        file_id = c.files_id
        f_name = str(c.created_at).replace(':', '_')
        file_name = c.created_at
        if f_name > x_date:
            file = await callback.message.bot.get_file(file_id)
            await callback.message.bot.download(file,
                                                destination=f'./photos/{file_name}.jpg')
            y.upload(f'./photos/{file_name}.jpg',
                     f'/EST-TM-photos/{file_name}.jpg')
            x_date = str(file_name)

    with open('x_date.txt', 'w') as f:
        f.seek(0, 0)
        f.write(x_date)
        f.close()
