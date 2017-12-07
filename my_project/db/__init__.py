from flask import request

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

import settings


def scope_func():
    try:
        return request._get_current_object()
    except RuntimeError:
        return '__boo__'


def remove_session(*_args):
    session.rollback()
    session.remove()


def import_all():  # alembic helper
    from . import models


Base = declarative_base()
engine = create_engine(settings.DATABASE_URI, pool_recycle=600)
Session = sessionmaker(bind=engine)
session = scoped_session(lambda: Session(autoflush=False, expire_on_commit=False), scopefunc=scope_func)
