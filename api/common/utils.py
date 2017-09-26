#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import functools
import logging
import six

import requests
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
                'handlers': handlers,
                'level': 'INFO',
                'propagate': False
            },
            # api can not be empty, not consistent with Django, if have time, maybe help fix this?
            'api': {
                'handlers': ['debug', 'info', 'error'],
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
        return True
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

    class Meta:
        abstract = True

    @classmethod
    def send(cls, path, auth=None, method='GET', endpoint=None,
             params=None, data=None, headers=None, target_source=None,
             timeout=DEFAULT_TIMEOUT_SECONDS):
        if endpoint is None:
            endpoint = cls.endpoint
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

        if method == 'POST':
            response = requests.post(url, **args)
        elif method == 'PUT':
            response = requests.put(url, **args)
        elif method == 'DELETE':
            response = requests.delete(url, **args)
        else:
            response = requests.get(url, **args)

        return cls._parse_response(response, target_source)

    @classmethod
    def _parse_response(cls, response, target_source):
        from .exceptions import ServiceException
        code = response.status_code
        LOGGER.debug('response status_code={}, content={}'.format(code, convert_to_unicode(response.content)))

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
            raise ServiceException(status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   'service data was not in valid json format.', target_source)

        if not status.is_success(code):
            raise ServiceException(code, response.text, target_source)
        return result
