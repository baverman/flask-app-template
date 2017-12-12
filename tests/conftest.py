import os
import sys
import types
import logging

from sqlalchemy.schema import ForeignKeyConstraint

logging.basicConfig(level='DEBUG')
if 'ECHO_SQL' in os.environ:
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


def make_module(name, content):
    pkg, _, mname = name.rpartition('.')
    if pkg:
        __import__(pkg)
    else:
        module = types.ModuleType(mname)
        module.__dict__.update(content)

    if pkg:
        module.__package__ = pkg
        setattr(sys.modules[pkg], mname, module)

    sys.modules[name] = module


def import_as(name):
    def inner(cls):
        make_module(name, cls.__dict__)
        return cls

    return inner


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
