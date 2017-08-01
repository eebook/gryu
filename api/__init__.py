#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

from flask import Flask
from flask_wtf.csrf import CSRFProtect

from .models.models import db
from config import config


def create_app(config_name='default'):
    app = Flask(__name__)
    csrf = CSRFProtect()
    csrf.init_app(app)

    # load default configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)

    from api.v1 import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/v1')

    return app
