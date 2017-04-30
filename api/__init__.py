#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

from flask_migrate import Migrate
from flask import Flask
from .common.models import db
from config import config


def create_app(config_name='default'):
    app = Flask(__name__)

    # load default configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)

    return app
