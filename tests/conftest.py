import os
import logging

from sqlalchemy.schema import ForeignKeyConstraint
from flaskish import import_as

logging.basicConfig(level='DEBUG')
if 'ECHO_SQL' in os.environ:
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


@import_as('settings')
class Settings:
    CORRECT_SETTING = True  # ensure we do not use invalid settings
    DATABASE_URI = 'sqlite:////tmp/test.db'


import pytest

import settings
assert settings.CORRECT_SETTING

from my_project import db


@pytest.fixture
def dbsession(request):
    if hasattr(request.module, 'TABLES'):
        tables = [getattr(r, '__table__', r) for r in request.module.TABLES]
    else:
        tables = None

    meta = getattr(request.module, 'METADATA', db.Base.metadata)
    assert Settings.DATABASE_URI == str(db.engine.url), 'WEIRDO!' # double check correct db settings

    if tables:
        for t in tables:
            db.engine.execute('DROP TABLE IF EXISTS {}'.format(t.name))
    else:
        meta.drop_all(db.engine, tables)

    for t in tables or []:
        t.constraints = [r for r in t.constraints if not isinstance(r, ForeignKeyConstraint)]
    meta.create_all(db.engine, tables)

    request.addfinalizer(db.session.remove)

    session = db.session
    def fadd(self, o):
        self.add(o)
        self.flush()
        return o

    def fadd_all(self, *objs):
        self.add_all(objs)
        self.flush()

    def refresh_all(self, *objs):
        for o in objs:
            self.refresh(o)

    session.fadd = fadd.__get__(session)
    session.fadd_all = fadd_all.__get__(session)
    session.refresh_all = refresh_all.__get__(session)
    return session
