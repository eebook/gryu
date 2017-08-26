#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import logging
import inspect
from functools import wraps

from flask import request
import jsonschema

from .exceptions import APIException

SCHEMA_DIR = 'api/specifications/schemas'
SCHEMA_PATH = os.path.join(os.getcwd(), SCHEMA_DIR)
logger = logging.getLogger(__name__)


def _get_request_body(_request):
    """
    Get the json payload of the request
    :param _request: request object
    """
    return _request.json


def serialize_number(value):
    """
    Try to convert `string` to `int`, if it can't, try to convert to `float`, if it fails again,
    the `string` itself is returned
    """
    try:
        _val = int(value)
        return _val
    except ValueError:
        pass
    try:
        _val = float(value)
        return _val
    except ValueError:
        return value


def _multi_dict_to_dict(_md):
    """
    Converts a `MultiDict` to a `dict ` object
    :param _md: object
    :type _md: MultiDict
    :returns: converted MultiDict object
    "rtype: dict
    """
    result = dict(_md)
    for key, value in result.items():
        if len(value) == 1:
            result[key] = serialize_number(value[0])
        else:
            result[key] = [serialize_number(v) for v in value]
    return result


def _get_url_params_as_dict(_request):
    return _multi_dict_to_dict(_request.args)


def get_request_payload(method):
    """
    Get request payload based on the request.method
    :param method: request method
    """
    return {
        'GET': _get_url_params_as_dict,
        'POST': _get_request_body,
        'PUT': _get_request_body,
    }[method]


def get_schema(path):
    """
    Read a json file and return its content(Python object)
    :param path: json file path
    """
    with open(path, 'r') as f:
        return json.load(f)


def _get_path_for_function(func):
    return os.path.dirname(os.path.realpath(inspect.getfile(func)))


def validate_schema(payload, schema):
    """
    Validates the payload against a defined json schema for the requested endpoint.

    :param payload: request data
    :type payload: dict
    :param schema: the schema that the request payload should be validated against
    :type schema: .json file
    :returns: errors if any
    :rtype: list
    """
    errors = []
    validator = jsonschema.Draft4Validator(schema, format_checker=jsonschema.FormatChecker())
    for error in sorted(validator.iter_errors(payload)):
        errors.append(error.message)
    return errors


def schema(path=None):
    """
    Validate the request payload with a JSONSchema.

    Decorator func that will be used to specify the path to the schema that route/endpoint will be validate against.

    :param path: path to the schema file
    :type path: string
    :returns: list of errors if there are any
    "raises: Invalid request if there are any errors

    ex:
    @schema('/path/to/schema.json')
    @app.route('/app-route')
    def app_route():
        ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(request.data is not None)
            if request.data is not None and request.data != b'':
                _path = path.lstrip('/')
                schema_path = os.path.join(SCHEMA_PATH, request.blueprint, _path)
                logger.debug("SCHEMA_PATH: {}, request.blueprint: {}, _path: {}".format(
                    SCHEMA_PATH, request.blueprint, _path))
                payload = get_request_payload(request.method)(request)

                errors = validate_schema(payload, get_schema(schema_path))
                if errors:
                    raise APIException('invalid_request', message_params=errors)
            return func(*args, **kwargs)
        return wrapper
    return decorator
