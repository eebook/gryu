# _*_ coding:utf-8 _*_

from __future__ import unicode_literals

import collections
import json
import logging
import os

from . import status
from .utils import convert_to_unicode as u
from .utils import is_string, merge_dicts

logger = logging.getLogger(__name__)

DEFAULT_MESSAGE = 'Unknown issue was caught and message was not specified.'
DEFAULT_TYPE = 'bad_request'

COMMON_ERRORS_MAP = {
    'invalid_args': {
        'message': 'Invalid parameters were passed.'
    },
    'unknown_issue': {
        'message': DEFAULT_MESSAGE,
        'type': 'server_error'
    },
    'permission_denied': {
        'message': 'Current user has no permission to perform the action.',
        'type': 'forbidden'
    },
    'resource_not_exist': {
        'message': 'The requested resource does not exist.',
        'type': 'not_found'
    },
    'resource_state_conflict': {
        'message': 'State of the requested resource is conflict.',
        'type': 'conflict'
    }
}

# reference:
# https://devcenter.heroku.com/articles/platform-api-reference#error-responses
ERROR_TYPES_MAP = {
    'bad_request': {
        'status_code': status.HTTP_400_BAD_REQUEST
    },
    'unauthorized': {
        'status_code': status.HTTP_401_UNAUTHORIZED
    },
    'delinquent': {
        'status_code': status.HTTP_402_PAYMENT_REQUIRED
    },
    'forbidden': {
        'status_code': status.HTTP_403_FORBIDDEN
    },
    'suspended': {
        'status_code': status.HTTP_403_FORBIDDEN
    },
    'not_found': {
        'status_code': status.HTTP_404_NOT_FOUND
    },
    'method_not_allowed': {
        'status_code': status.HTTP_405_METHOD_NOT_ALLOWED
    },
    'not_acceptable': {
        'status_code': status.HTTP_406_NOT_ACCEPTABLE
    },
    'conflict': {
        'status_code': status.HTTP_409_CONFLICT
    },
    'unsupported_media_type': {
        'status_code': status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    },
    'rate_limit': {
        'status_code': status.HTTP_429_TOO_MANY_REQUESTS
    },
    'server_error': {
        'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR
    },
    'not_implemented': {
        'status_code': status.HTTP_501_NOT_IMPLEMENTED
    },
    'bad_gateway': {
        'status_code': status.HTTP_502_BAD_GATEWAY
    },
    'service_unavailable': {
        'status_code': status.HTTP_503_SERVICE_UNAVAILABLE
    },
}


class EEBookBaseAPIException(Exception):

    source = os.getenv('SOURCE', 'None')
    code = 'unknown_issue'
    message = DEFAULT_MESSAGE
    error_type = 'server_error'

    class Meta:
        abstract = True

    @property
    def data(self):
        data = {
            'code': self.code,
            'source': self.source,
            'message': self.message
        }
        if hasattr(self, 'fields'):
            data['fields'] = self.fields
        return data

    def __str__(self):
        return json.dumps(self.data)


class EEBookAPIException(EEBookBaseAPIException):

    errors_map = {}

    def __init__(self, code, message=None, message_params=None):

        errors_map = merge_dicts(self.errors_map, COMMON_ERRORS_MAP)
        assert code in errors_map, (
            'error code {} was not found in errors map'.format(code)
        )

        self.code = code
        self._error = errors_map[code]
        self._message = message
        self._message_params = message_params

    def __str__(self):
        return self.message

    @property
    def error_type(self):
        return self._error.get('type', DEFAULT_TYPE)

    @property
    def message(self):
        if self._message:
            return self._message
        message = self._error.get('message', DEFAULT_MESSAGE)
        message = u(message)
        if not self._message_params:
            return message
        elif is_string(self._message_params):
            return message.format(u(self._message_params))
        elif isinstance(self._message_params, collections.Mapping):
            return message.format(**self._message_params)
        elif isinstance(self._message_params, collections.Iterable):
            return message.format(*self._message_params)
        return message.format(self._message_params)

    @property
    def status_code(self):
        try:
            return ERROR_TYPES_MAP[self.error_type]['status_code']
        except KeyError:
            logger.warning('Error type {} was not found in ERROR_TYPES_MAP.'
                        .format(u(self.error_type)))
            return ERROR_TYPES_MAP[DEFAULT_TYPE]['status_code']


class EEBookFieldValidateFailed(EEBookAPIException):

    def __init__(self, fields, message=None, message_params=(), code='invalid_args'):
        assert (
            isinstance(fields, collections.Iterable) or
            isinstance(fields, collections.Mapping)
        ), 'fields must be a list or dictionary like object.'
        if isinstance(fields, collections.Mapping):
            fields = [fields]
        try:
            json.dumps(fields)
        except ValueError:
            logger.error('fields could not be dumped.')
            raise

        self.code = code
        self.fields = fields
        super(MekFieldValidateFailed, self).__init__(self.code, message=message,
                                                     message_params=message_params)

    @property
    def data(self):
        data = super(MekFieldValidateFailed, self).data
        data['fields'] = self.fields
        return data
