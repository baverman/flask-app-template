from __future__ import print_function
from functools import wraps
import logging

try:
    import ujson as json
except ImportError:
    import json

from flask import Flask as _Flask
from flask.globals import _request_ctx_stack
from werkzeug.wrappers import Response
from werkzeug.datastructures import Headers
from werkzeug.exceptions import HTTPException

_Request = _Flask.request_class


class cached_property(object):
    def __init__(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value


class ApiError(Exception):
    status_code = 500
    error = 'internal-error'

    def __init__(self, error=None, status_code=None, **kwargs):
        self.status_code = status_code or self.status_code
        self.error = error or self.error
        self.details = kwargs

    def to_json(self):
        data = {'error': self.error}
        self.details and data.update(self.details)
        return data


class Request(_Request):
    def __init__(self, *args, **kwargs):
        _Request.__init__(self, *args, **kwargs)
        self._response = None

    @cached_property
    def response(self):
        self._response = HeaderResponse()
        return self._response

    def process_response(self, response):
        headers = self._response and self._response.headers
        if headers:
            response.headers._list.extend(headers)
        return response


class HeaderResponse(Response):
    def __init__(self):
        self.headers = Headers()


class Flask(_Flask):
    request_class = Request

    def __init__(self, *args, static_folder=None, **kwargs):
        _Flask.__init__(self, *args, static_folder=static_folder, **kwargs)
        self.url_map.strict_slashes = False
        self.endpoint_counter = 0
        self._logger = logging.getLogger(self.logger_name)

    def route(self, rule, endpoint=None, weight=None, **options):
        if weight is not None:
            weight = False, -9999, weight

        def decorator(func):
            lendpoint = endpoint
            if not lendpoint:
                lendpoint = '{}_{}'.format(func.__name__, self.endpoint_counter)
                self.endpoint_counter += 1
            self.add_url_rule(rule, lendpoint, func, **options)
            if weight:
                self.url_map._rules[-1].match_compare_key = lambda: weight
            return func
        return decorator

    def api(self, *args, **kwargs):
        def decorator(func):
            @wraps(func)
            def inner(*args, **kwargs):
                try:
                    result = func(*args, **kwargs)
                except ApiError as e:
                    result = e
                except HTTPException as e:
                    result = e
                except Exception:
                    self.logger.exception('Unhandled error')
                    result = ApiError()

                if isinstance(result, Response):
                    return result
                elif isinstance(result, ApiError):
                    code = result.status_code
                    result = result.to_json()
                else:
                    code = 200
                return self.response_class(json.dumps(result, ensure_ascii=False), code,
                                           content_type='application/json')
            return self.route(*args, **kwargs)(inner)
        return decorator

    def process_response(self, response):
        response = _request_ctx_stack.top.request.process_response(response)
        return _Flask.process_response(self, response)

    def print_routes(self, sort=False):
        rules = self.url_map.iter_rules()
        if sort:
            rules = sorted(rules, key=lambda r: r.rule)

        for rule in rules:
            func = self.view_functions[rule.endpoint]
            print('{:10} {}\t{}.{}'.format(
                ','.join(rule.methods),
                rule.rule,
                func.__module__,
                func.__name__))
