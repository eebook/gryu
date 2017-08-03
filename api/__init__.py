#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals


from flask import Flask, Blueprint
from flask_wtf.csrf import CSRFProtect
from flask_logconfig import LogConfig

from config import config
from .middleware import TestMiddleware
from .common.utils import json
from .common.database import init_db
from .common.middleware import response


BP_NAME = 'root'
root = Blueprint(BP_NAME, __name__)

@root.route("/ping", methods=["GET"])
def ping():
    return "pong"

@root.route("/about", methods=["GET"])
@json
def about():
    logger.error("sdfasdfsd")
    return {
        "title": "Why ee-book.org exsits",
        "content": "TODO",
    }


def create_app(config_name='default'):
    app = Flask(__name__)
    app.wsgi_app = TestMiddleware(app.wsgi_app)

    # TODO: Do you understand?
    csrf = CSRFProtect()
    csrf.init_app(app)

    # load default configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    logcfg = LogConfig(app)
    logcfg.init_app(app)

    from .users import auth_bp as auth_bp
    app.register_blueprint(root, url_prefix='/v1')
    app.register_blueprint(auth_bp, url_prefix='/v1/auth')

    app.response_class = response.JSONResponse
    response.json_error_handler(app=app)
    init_db()

    return app
