import os

from flask import request, make_response
from werkzeug.wsgi import SharedDataMiddleware

class TestMiddleware(object):

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        # How do I access request object here.
        # print("Im in middleware")
        # with self.request_context(environ):
        # try:
        #     response = self.full_dispatch_request()
        # except Exception as e:
        #     response = make_response("asdfsdf")
        # print("__file__???" + os.path.dirname(__file__))
        return self.app(environ, start_response)
