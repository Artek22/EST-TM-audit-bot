from db.models import User, Competitor
from db.engine import session

users = session.query(User)
for u in users:
    print(f'{u.name} {u.surname}')
