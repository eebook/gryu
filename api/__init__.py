#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import os
from flask import Flask, Blueprint, request
from flask_wtf.csrf import CSRFProtect
from flask_logconfig import LogConfig

from config import config
from .middleware import TestMiddleware
from .common.utils import json
from .common.database import init_db
from .common.middleware import response
from .common.exceptions import APIException
from .common.database import db_session

BP_NAME = 'root'
API_TOKEN_HEADERS = 'API_TOKEN'
root_bp = Blueprint(BP_NAME, __name__)
logger = logging.getLogger(__name__)


@root_bp.route("/ping", methods=["GET"])
def ping():
    return "pong"


@root_bp.route("/about", methods=["GET"])
@json
def about():
    return {
        "title": "Why ee-book.org exist",
        "content": "TODO: about content",
    }


def create_app(config_name='dev'):
    app = Flask(__name__)
    app.wsgi_app = TestMiddleware(app.wsgi_app)

    @app.before_request
    def ensure_content_type():
        content_type = request.headers.get('Content-type')
        if not content_type == 'application/json':
            raise APIException('invalid_content_type')
        # TODO: Add API_TOKEN_HEADERS
        if not request.headers.get(API_TOKEN_HEADERS, '') == os.environ.get('SECURE_API_KEY', ''):
            raise APIException('permission_denied')

    # @app.teardown_appcontext
    # def shutdown_session(exception=None):
    #     db_session.remove()

    # TODO: Do you understand?
    csrf = CSRFProtect()
    csrf.init_app(app)

    # load default configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    logcfg = LogConfig(app)
    logcfg.init_app(app)

    from .users import auth_bp as auth_bp
    app.register_blueprint(root_bp, url_prefix='/v1')
    app.register_blueprint(auth_bp, url_prefix='/v1/auth')

    app.response_class = response.JSONResponse
    response.json_error_handler(app=app)
    init_db()

    return app
