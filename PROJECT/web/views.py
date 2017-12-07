from covador.flask import query_string

from .. import calc
from . import app


@app.api('/add', methods=['POST'])
@query_string(value=int)
def add(value):
    calc.add(value)
    return {'result': 'ok'}


@app.api('/sum')
def get_sum():
    return {'result': calc.get_sum()}
