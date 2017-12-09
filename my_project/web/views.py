from covador.flask import query_string

from .. import calc, statsd
from . import app


@app.api('/add', methods=['POST'])
@query_string(value=int)
def add(value):
    calc.add(value)
    statsd.client.incr('api.add')
    return {'result': 'ok'}


@app.api('/sum')
def get_sum():
    with statsd.client.timer('api.sum'):
        result = calc.get_sum()
    return {'result': result}
