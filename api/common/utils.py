#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import functools
import logging
import six
import time

import requests
from requests.exceptions import ConnectionError, ConnectTimeout
from flask import jsonify
from flask import g
from flask_httpauth import HTTPTokenAuth
from werkzeug.routing import BaseConverter

from .database import db
from . import status


DEFAULT_TIMEOUT_SECONDS = 30
token_auth = HTTPTokenAuth('token')
LOGGER = logging.getLogger(__name__)


def merge_dicts(*dict_args):
    """
    Given any number of dict, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


def is_string(text):
    """
    :param text: input content
    check if the text is string type, return True if it is, else return False.
    """
    if six.PY2:
        return isinstance(text, basestring)
    return isinstance(text, (str, bytes))


def str2bool(v):
    return v and v.lower() in ("yes", "true", "t", "1")


def str2int(v, default):
    try:
        return int(v)
    except:
        return default

def convert_to_unicode(text):
    """
    :param text: input content
    If text is utf8 encoded, then decode it with utf8 and return it, else just return it.
    """
    assert is_string(text), 'text must be string types.'

    try:
        return text.decode('utf-8')
    except UnicodeEncodeError:  # python2 will raise this exception when decode unicode.
        return text
    except AttributeError:  # python3 will raise this exception when decode unicode.
        return text


# Can be moved to a common package, Temporarily did not add a colored log
def get_log_config(component, handlers, level='DEBUG', path='/var/log/eebook'):
    """
    Return a log config.
    :param component: name of component
    :param handlers: debug, info, error
    :param level: the level of the log
    :param path: The path to the log
    :return: config for flask-logconfig
    """
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s][%(threadName)s]' +
                '[%(name)s.%(funcName)s():%(lineno)d] %(message)s'
            },
        },
        'handlers': {
            'debug': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': path + component + '.debug.log',
                'maxBytes': 1024 * 1024 * 1024,
                'backupCount': 5,
                'formatter': 'standard',
            },
            'info': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': path + component + '.info.log',
                'maxBytes': 1024 * 1024 * 1024,
                'backupCount': 5,
                'formatter': 'standard',
            },
            'error': {
                'level': 'ERROR',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': path + component + '.error.log',
                'maxBytes': 1024 * 1024 * 100,
                'backupCount': 5,
                'formatter': 'standard',
            },
            'console': {
                'level': level,
                'class': 'logging.StreamHandler',
                'formatter': 'standard'
            },
        },
        'loggers': {
            'werkzeug': {
                'handlers': ['info', 'console'],
                'level': 'INFO',
                'propagate': False
            },
            # api can not be empty, not consistent with Django, if have time, maybe help fix this?
            'api': {
                'handlers': handlers,
                'level': level,
                'propagate': False
            }
        }
    }
    return config


def json(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        rv = f(*args, **kwargs)
        from .middleware.response import JSONResponse
        if isinstance(rv, JSONResponse):
            return rv
        status_or_headers = None
        headers = None
        if isinstance(rv, tuple):
            rv, status_or_headers, headers = rv + (None,) * (3 - len(rv))
        if isinstance(status_or_headers, (dict, list)):
            headers, status_or_headers = status_or_headers, None
        if not isinstance(rv, dict):
            rv = rv.to_json()
        rv = jsonify(rv)
        if status_or_headers is not None:
            rv.status_code = status_or_headers
        if headers is not None:
            rv.headers.extend(headers)
        return rv
    return wrapped


@token_auth.verify_token
def verify_token(token):
    from ..users.models import EncryptedTokens
    # Here is a pit, spend a lot of time
    token = token.strip('b').strip('\'')
    instance = db.session.query(EncryptedTokens).filter(EncryptedTokens.key == token.encode('utf-8')).first()
    if instance:
        user = instance.users
        g.user = user
        LOGGER.info("user???{}".format(user))
        return True
    LOGGER.info("no instance...")
    return False


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


class DoRequest(object):
    endpoint = None
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    target_source = None

    class Meta:
        abstract = True

    @classmethod
    def send(cls, path, auth=None, method='GET', endpoint=None,
             params=None, data=None, headers=None, target_source=None,
             timeout=DEFAULT_TIMEOUT_SECONDS):
        if endpoint is None:
            endpoint = cls.endpoint
        if target_source is None:
            target_source = cls.target_source
        url = '/'.join([endpoint, path.lstrip('/')])

        LOGGER.info('requesting url={}, method={}, header={}, data={}, params={}, '
                    'target_source={}'.format(url, method, headers, data, params, target_source))

        if headers is None:
            headers = cls.headers.copy()
        else:
            headers = merge_dicts(cls.headers, headers)

        args = {'headers': headers, "timeout": timeout}
        if auth is not None:
            args['auth'] = auth
        if params is not None:
            args['params'] = params
        if data is not None:
            args['json'] = data
        try:
            if method == 'POST':
                response = requests.post(url, **args)
            elif method == 'PUT':
                response = requests.put(url, **args)
            elif method == 'DELETE':
                response = requests.delete(url, **args)
            else:
                response = requests.get(url, **args)
        except ConnectTimeout as e:
            LOGGER.error('Timeout, url: %s', url)
            from .exceptions import ServiceException
            raise ServiceException(status.HTTP_503_SERVICE_UNAVAILABLE, 'service timeout.', target_source)
        except ConnectionError as e:
            LOGGER.error('Connection error!, url: %s', url)
            LOGGER.error('error: {}'.format(e))
            from .exceptions import ServiceException
            raise ServiceException(status.HTTP_503_SERVICE_UNAVAILABLE, 'service is unavailable.', target_source)
        except Exception as e:
            raise(e)

        return cls._parse_response(response, target_source)

    @classmethod
    def _parse_response(cls, response, target_source):
        from .exceptions import ServiceException
        code = response.status_code

        result = {
            'status_code': code,
            'data': None,
        }

        if code == status.HTTP_204_NO_CONTENT:
            return result
        elif code == status.HTTP_503_SERVICE_UNAVAILABLE:
            raise ServiceException(status.HTTP_503_SERVICE_UNAVAILABLE,
                                   'service is unavailable.', target_source)

        try:
            result['data'] = response.json()
        except Exception as ex:
            LOGGER.error('Failed to parse response: {}.\n'
                         'Raw response text is {}.'.format(type(ex), response.text))
            if response.status_code == status.HTTP_401_UNAUTHORIZED:
                raise ServiceException(status.HTTP_401_UNAUTHORIZED,
                                       'service data was not in valid json format.', target_source)
            raise ServiceException(status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   'service data was not in valid json format.', target_source)

        if not status.is_success(code):
            raise ServiceException(code, response.text, target_source)
        return result


def singleton(cls):
    obj = cls()
    # Always return the same object
    cls.__new__ = staticmethod(lambda cls: obj)
    # Disable __init__
    try:
        del cls.__init__
    except AttributeError:
        pass
    return cls

@singleton
class Diagnoser(object):
    _subscriptions = []

    def __init__(self):
        self._subscriptions = []

    def add(self, diagnose):
        assert isinstance(diagnose, Check)
        self._subscriptions.append(diagnose)

    def add_check(self, name, check_function):
        self.add(Check(name, check_function))

    def check(self):
        report = {'status': 'OK', 'details': []}
        for d in self._subscriptions:
            subreport = d.check()
            if subreport['status'] != 'OK' and report['status'] == 'OK':
                report['status'] = subreport['status']
            report['details'].append(subreport)
        return report


class Check(object):
    _name = ''
    _function = None

    def __init__(self, name, check_function):
        assert name
        self._name = name
        self._function = check_function

    def _current(self):
        return int(time.time()*1000)

    def check(self):
        start = self._current()
        try:
            result = self._function()
        except Exception as e:
            result = {'status': 'ERROR', 'message': '{}'.format(e.message)}
        assert isinstance(result, dict)
        assert 'status' in result
        result.update({
            'name': self._name,
            'latency': str(self._current() - start) + 'ms'
        })
        return result
