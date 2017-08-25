import json
from functools import singledispatch     # Only Python3 has this library

from flask import jsonify, Response
from werkzeug.exceptions import (BadRequest, ClientDisconnected, SecurityError,
                                 BadHost, NotFound, MethodNotAllowed, BadRequest)

from ..exceptions import JSONException, APIException


@singledispatch
def to_serializable(rv):
    """
    Define a generic serializable function.
    """
    pass


@to_serializable.register(dict)
def ts_dict(rv):
    """Register the `dict` type
    for the generic serializable function.
    :param rv: object to be serialized
    :type rv: dict
    :returns: flask Response object
    """
    return jsonify(rv)


@to_serializable.register(list)
def ts_list(rv):
    """Register the `list` type
    for the generic serializable function.
    :param rv: objects to be serialized
    :type rv: list
    :returns: flask Response object
    """
    return Response(json.dumps(rv, indent=4, sort_keys=True))


class JSONResponse(Response):
    """
    Custom `Response` class that will be
    used as the default one for the application.
    All responses will be of type
    `application-json`.
    """
    @classmethod
    def force_type(cls, rv, environ=None):
        rv = to_serializable(rv)
        return super(JSONResponse, cls).force_type(rv, environ)


def json_error_handler(app):
    @app.errorhandler(JSONException)
    def handle_invalid_usage(error):
        """
        Custom `Exception` class that will be
        used as the default one for the application.
        Returns pretty formatted JSON error
        with detailed information.

        :message: error message
        :status_code: response status code
        :type: error type
        """
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(NotFound.code)
    def resource_not_found(error):
        """
        Custom `errorhandler` for 404 pages.
        Returns a JSON object with a message
        that accessed URL was not found.
        """
        response = jsonify(APIException(code='resource_not_exist').to_dict())
        response.status_code = NotFound.code
        return response

    @app.errorhandler(MethodNotAllowed.code)
    def method_not_allowed(error):
        response = jsonify(
            {
                "errors": [
                    {
                        "code": "method_not_allowed",
                        "messages": error.description,
                        "source": "None"
                    }
                ]
            }
        )
        response.status_code = error.code
        return response

    @app.errorhandler(BadRequest.code)
    def bad_request(error):
        response = jsonify({
            "errors": [
                {
                    "code": "bad_request",
                    "messages": error.description,
                    "source": "None"
                }
            ]
        })
        response.status_code = error.code
        return response

