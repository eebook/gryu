#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

import logging
from flask import request

from ..common.utils import json
from ..common.validation import schema
from . import auth_bp
from . import domain

logger = logging.getLogger(__name__)


@auth_bp.route("/register", methods=["POST"])  # Dont allow GET method access should return 405 error
@json
@schema('register_user.json')
def register_user():
    """
    Register a new user.
    """
    return domain.create_user(request.json)


@auth_bp.route("/exist", methods=["GET"])
def check_user_exist():
    """
    Check whether the user already exsits.
    """
    logger.debug("request dir???{}".format(dir(request)))
    logger.debug("request query_string: {}".format(request.query_string))
    logger.debug("request args: {}".format(request.args))
    return domain.check_user_exist(request.args)


@auth_bp.route("/profile", methods=["GET", "POST"])
@json
def get_user_profile():
    """
    Get the user's basic information
    """
    return {
        "TODO": "auth profile"
    }


@auth_bp.route("/activate/activate_key", methods=["put"])
def activate():
    """
    Activate user's email
    """
    return {
        "TODO": "activate"
    }


@auth_bp.route("/generate-api-token", methods=["POST"])
def generate_api_token():
    """
    """
    return {
        "TODO": "API token"
    }
