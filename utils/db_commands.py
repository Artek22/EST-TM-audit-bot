import time
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from db.models import Competitor, User
from db.engine import session


def register_user(message):
    name = message.chat.first_name if message.chat.first_name else None
    user = User(
        id=int(message.chat.id),
        name=name,
        role="kid",
        language="RU",
        score=0
    )

    session.add(user)

    try:
        session.commit()
        return True
    except IntegrityError:
        session.rollback()  # откатываем session.add(user)
        return False


def select_user(user_id) -> User:
    '''Получаем пользователя по id.'''
    user = session.query(User).filter(User.id == user_id).first()
    return user
