#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

import logging
from flask import request, g

from ..common.utils import json, token_auth
from ..common.validation import schema
from ..common import status
from . import users_bp, user_bp
from . import domain

LOGGER = logging.getLogger(__name__)


@users_bp.route("/register", methods=["POST"])
@json
@schema('register_user.json')
def register_user():
    """
    Register a new user
    """
    return domain.create_user(request.json)


@users_bp.route("/exist", methods=["GET"])
@token_auth.login_required
def check_user_exist():
    """
    Check whether the user already exsits
    """
    return domain.check_user_exist(request.args)


@users_bp.route("/profile", methods=["GET", "POST"])
@token_auth.login_required
def get_user_profile():
    """
    Get the user's basic information
    """
    LOGGER.debug("user {} is requesting the profile pages".format(g.user))
    return {
        "TODO": "return user {}\' profile".format(g.user.username)
    }


@users_bp.route("/activate/<activation_key>", methods=["PUT"])
def activate(activation_key):
    """
    Activate user via uuid
    """
    domain.activate_user(activation_key)
    return '', status.HTTP_204_NO_CONTENT


@users_bp.route("/generate-api-token", methods=["POST"])
@json
@schema('get_user_token.json')
def generate_api_token():
    """
    Generate api token
    """
    return domain.generate_api_token(request.json)


@user_bp.route("/send_verify_code", methods=["POST"])
@json
@schema('send_verify_code.json')
# TODO: Inner api
def send_captcha_code():
    LOGGER.debug('Send verify code, request.json: %s', request.json)
    domain.send_captcha_code(request.json)
    return {}, status.HTTP_204_NO_CONTENT


@user_bp.route("/reset_password", methods=["POST"])
@json
@schema('reset_password.json')
# TODO: Inner api
def reset_password():
    LOGGER.debug('Reset password, request.json: %s', request.json)
    domain.reset_password(request.json)
    return {'status': 'success'}, status.HTTP_200_OK
