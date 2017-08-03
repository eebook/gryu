#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

import logging
from flask import request

from ..common.utils import json
from . import auth_bp
from . import domain

logger = logging.getLogger(__name__)


@auth_bp.route("/register", methods=["POST"])
@json
def user_register():
    """
    Register a new user.
    """
    logger.debug("user register, request.json???{}".format(request.json))
    return domain.create_user(request.json)

@auth_bp.route("/mobile/exist", methods=["GET"])
@json
def check_mobile_exist():
    """
    Check if the phone number already exists.
    """
    return {
        "TODO": "check, check mobile phone"
    }


@auth_bp.route("/exist", methods=["GET"])
@json
def check_user_exist():
    """
    Check whether the user already exsits.
    """
    return {
        "TODO": "check, check, check"
    }


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
