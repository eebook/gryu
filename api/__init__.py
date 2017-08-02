#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals


from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_logconfig import LogConfig

from .models.models import db
from config import config
from .middleware import TestMiddleware


def create_app(config_name='default'):
    app = Flask(__name__)
    app.wsgi_app = TestMiddleware(app.wsgi_app)

    # TODO: Do you understand?
    csrf = CSRFProtect()
    csrf.init_app(app)

    # load default configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    db.init_app(app)
    logcfg = LogConfig(app)
    logcfg.init_app(app)

    from api.v1 import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/v1')

    return app
