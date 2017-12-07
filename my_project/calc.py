from sqlalchemy import func
from .db import session, models as m


def add(value, commit=True):
    v = m.Value(value=value)
    session.add(v)
    commit and session.commit()
    return v


def get_sum():
    return session.query(func.sum(m.Value.value)).scalar()
