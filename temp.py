from db.models import User, Competitor
from db.engine import session

count = session.query(Competitor).count()
print(count)