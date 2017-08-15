#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import logging
import json
import collections

from . import status
from .utils import convert_to_unicode as u
from .utils import is_string, merge_dicts

SOURCE = os.getenv('SOURCE', '1000')
DEFAULT_CODE = 'bad_request'
DEFAULT_MESSAGE = 'Unknown issue was caught and message was not specified'
DEFAULT_ERROR_TYPE = 'bad_request'
logger = logging.getLogger(__name__)

MAP_COMMON_ERRORS_MESSAGES = {
    'invalid_args': {
        'message': 'Invalid parameters were passed'
    },
    'unknown_issue': {
        'message': DEFAULT_MESSAGE,
        'type': 'server_error'
    },
    'permission_denied': {
        'message': 'You don\'t have enough permission to perform this action',
        'type': 'forbidden'
    },
    'resource_not_exist': {
        'message': 'The requested resource was not found on the server',
        'type': 'not_found'
    },
    'resource_state_conflict': {
        'message': 'State of the requested resource is conflict',
        'type': 'conflict'
    },
    'invalid_content_type': {
        'message': 'Invalid content-type. Only `application-json` is allowed.',
        'type': 'bad_request'
    },
    'invalid_request': {
        'message': 'Not verified by json schema, errors: {}',
        'type': 'bad_request'
    }
}

# reference:
# https://devcenter.heroku.com/articles/platform-api-reference#error-responses
MAP_ERROR_TYPES_STATUS_CODE = {
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


class JSONException(Exception):
    source = SOURCE
    code = DEFAULT_CODE
    message = DEFAULT_MESSAGE
    error_type = DEFAULT_ERROR_TYPE

    class Meta:
        abstract = True

    def to_dict(self):
        data = {
            'code': self.code,
            'source': self.source,
            'message': self.message
        }
        if hasattr(self, 'fields'):
            data['fields'] = self.fields
        return data

    def __str__(self):
        """
        :return: Json encoded string
        """
        return json.dumps(self.to_dict())


class APIException(JSONException):
    errors_map = {}

    def __init__(self, code, message=None, message_params=None):
        errors_map = merge_dicts(self.errors_map, MAP_COMMON_ERRORS_MESSAGES)
        assert code in errors_map, (
            'error code {} was not found in errors_map'.format(code)
        )
        self.code = code
        self._error = errors_map[code]
        self._message = message
        self._message_params = message_params

    @property
    def message(self):
        if self._message:
            return self._message

        message = self._error.get('message', DEFAULT_MESSAGE)
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
    def error_type(self):
        return self._error.get('type', DEFAULT_ERROR_TYPE)

    @property
    def status_code(self):
        try:
            return MAP_ERROR_TYPES_STATUS_CODE[self.error_type]['status_code']
        except KeyError:
            logger.warning("Error type {} was not found in MAP_ERROR_TYPES_STATUS_CODE".format(u(self.error_type)))
            return MAP_ERROR_TYPES_STATUS_CODE[DEFAULT_ERROR_TYPE]['status_code']

    def __str__(self):
        return self.message


class FieldValidateFaield(APIException):

    def __init__(self, fields, message=None, message_params=(), code='invalid_args'):
        assert isinstance(fields, (collections.Iterable, collections.Mapping)),\
            'fields must be a list or dict like object'

        if isinstance(fields, collections.Mapping):
            fields = [fields]
        try:
            json.dumps(fields)
        except ValueError:
            logger.error('fields could not be dumped.')
            raise

        self.code = code
        self.fields = fields
        super(FieldValidateFaield, self).__init__(self.code, message=message, message_params=message_params)

    def to_dict(self):
        data = super(FieldValidateFaield, self).to_dict()
        data['fields'] = self.fields
        return data
