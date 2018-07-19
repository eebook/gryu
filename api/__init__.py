#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

import logging
from flask import Flask, Blueprint, request
from flask_wtf.csrf import CSRFProtect
from flask_logconfig import LogConfig

from config import config
from .middleware import TestMiddleware
from .common.utils import json, RegexConverter
from .common.middleware import response
from .common.exceptions import APIException
from .common.database import db

# Import models so that they are registered with SQLAlchemy
from api.users.models import Users, ActivationKeys, EncryptedTokens      # noqa
from api.resources.models import Resources  # noqa


BP_NAME = 'root'
root_bp = Blueprint(BP_NAME, __name__)
logger = logging.getLogger(__name__)


@root_bp.route("/ping", methods=["GET"])
def ping():
    return "pong"


def create_app(config_name='dev'):
    app = Flask(__name__)
    app.wsgi_app = TestMiddleware(app.wsgi_app)

    @app.before_request
    def ensure_content_type():
        content_type = request.headers.get('Content-type')
        logger.debug("Request headers: %s", request.headers)
        if not content_type == 'application/json':
            raise APIException('invalid_content_type')

    # load default configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    logcfg = LogConfig(app)
    logcfg.init_app(app)

    # Support regular expression,
    # steal from https://stackoverflow.com/questions/5870188/does-flask-support-regular-expressions-in-its-url-routing
    app.url_map.converters['regex'] = RegexConverter
    app.register_blueprint(root_bp, url_prefix='/v1')

    from .about import about_bp
    app.register_blueprint(about_bp, url_prefix='/v1/about')

    from .users import users_bp, user_bp
    app.register_blueprint(users_bp, url_prefix='/v1/auth')
    app.register_blueprint(user_bp, url_prefix='/v1/user')

    from .books import books_bp
    app.register_blueprint(books_bp, url_prefix='/v1/books')

    from .jobs import jobs_bp as jobs_bp
    app.register_blueprint(jobs_bp, url_prefix='/v1/jobs')

    from .jobs import job_configs_bp as job_configs_bp
    app.register_blueprint(job_configs_bp, url_prefix='/v1/job_configs')

    from .search import search_bp
    app.register_blueprint(search_bp, url_prefix='/v1/search')

    from .url_metadata import url_metadata_bp
    app.register_blueprint(url_metadata_bp, url_prefix='/v1/url_metadata')

    from .tg_bot import tg_bot_bp
    app.register_blueprint(tg_bot_bp, url_prefix='/tg_bot')

    app.response_class = response.JSONResponse
    response.json_error_handler(app=app)

    db.init_app(app)

    return app
