from my_project.db import models as m
from my_project import calc

TABLES = [m.Value]


def test_get_sum(dbsession):
    calc.add(10)
    calc.add(20)
    assert calc.get_sum() == 30
