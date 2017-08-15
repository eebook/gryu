#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

import logging
from flask import request, g

from ..common.utils import json, token_auth
from ..common.validation import schema
from ..common import status
from . import auth_bp
from . import domain

logger = logging.getLogger(__name__)


@auth_bp.route("/register", methods=["POST"])  # TODO: Dont allow GET method access should return 405 error
@json
@schema('register_user.json')
def register_user():
    """
    Register a new user
    """
    return domain.create_user(request.json)


@auth_bp.route("/exist", methods=["GET"])
@token_auth.login_required
def check_user_exist():
    """
    Check whether the user already exsits
    """
    return domain.check_user_exist(request.args)


@auth_bp.route("/profile", methods=["GET", "POST"])
@token_auth.login_required
def get_user_profile():
    """
    Get the user's basic information
    """
    logger.debug("user {} is requesting the profile pages".format(g.user))
    return {
        "TODO": "return user {}\' profile".format(g.user.username)
    }


@auth_bp.route("/activate/<activation_key>", methods=["put"])
def activate(activation_key):
    """
    Activate user via uuid
    """
    domain.activate_user(activation_key)
    return '', status.HTTP_204_NO_CONTENT


@auth_bp.route("/generate-api-token", methods=["POST"])
@json
@schema('get_user_token.json')
def generate_api_token():
    """
    Generate api token
    """
    return domain.generate_api_token(request.json)
