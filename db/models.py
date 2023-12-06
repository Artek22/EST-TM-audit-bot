from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String, BigInteger
from sqlalchemy.orm import declarative_base

from db.engine import engine

DeclarativeBase = declarative_base()


class User(DeclarativeBase):
    __tablename__ = "users"

    id = Column("user_id", BigInteger, nullable=False, primary_key=True)
    name = Column(String(50), nullable=False)
    surname = Column(String(50), nullable=False)

    def __repr__(self):
        return "<{0.__class__.__name__}(id={0.id!r})>".format(self)


class Competitor(DeclarativeBase):
    __tablename__ = "competitors"

    id = Column("competitor_id", Integer, nullable=False, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"),
                     nullable=False)
    author_name = Column(String(100), nullable=False)
    client = Column(String(100), nullable=False)
    commodity_direction = Column(String(50), nullable=False)
    brand = Column(String(50), nullable=False)
    promo_for = Column(String(100), nullable=False)
    promo_type = Column(String(50), nullable=False)
    bonus = Column(String(50), nullable=False)
    condition = Column(String(100), nullable=False)
    files_id = Column(String, nullable=True)
    comment = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP, nullable=False)

    def __repr__(self):
        return "<{0.__class__.__name__}(id={0.id!r})>".format(self)


def create_db():
    # Метод создания таблиц бд по коду сверху
    DeclarativeBase.metadata.create_all(engine)


if __name__ == "__main__":
    create_db()
